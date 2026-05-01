from __future__ import annotations

import json
import statistics
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.product_client import ProductServiceClient
from app.config import get_settings
from app.graph.store import Neo4jGraphStore
from app.models.behavior import BehaviorEvent
from app.schemas.product import ProductCatalogItem
from app.schemas.recommend import RecommendationItem, RecommendationResponse
from app.services.graph import get_graph_recommendations
from app.services.lstm_service import LstmRecommendationService
from app.services.rag import retrieve_products


matplotlib.use("Agg")
import matplotlib.pyplot as plt


BASE_WEIGHTS: dict[str, float] = {
    "lstm": 0.4,
    "graph": 0.3,
    "rag": 0.3,
    "popularity": 0.2,
}


@dataclass
class CandidateSignal:
    product_id: int
    source_scores: dict[str, float]
    reasons: list[str]


@dataclass
class RecommendationDiagnostics:
    response: RecommendationResponse
    latency_ms: float
    source_availability: dict[str, bool]
    normalized_weights: dict[str, float]


def recommend_products(
    session: Session,
    user_id: int,
    query: str | None = None,
    limit: int = 5,
    client: ProductServiceClient | None = None,
) -> RecommendationResponse:
    return recommend_products_with_diagnostics(
        session=session,
        user_id=user_id,
        query=query,
        limit=limit,
        client=client,
    ).response


def recommend_products_with_diagnostics(
    session: Session,
    user_id: int,
    query: str | None = None,
    limit: int = 5,
    client: ProductServiceClient | None = None,
) -> RecommendationDiagnostics:
    started = time.perf_counter()
    effective_client = client or ProductServiceClient()
    products = load_products(client=effective_client)
    product_map = {product.id: product for product in products}
    interacted_ids = load_user_interacted_product_ids(session=session, user_id=user_id)

    candidates: dict[int, CandidateSignal] = {}
    source_availability = {"lstm": False, "graph": False, "rag": False, "popularity": False}

    lstm_result = LstmRecommendationService().recommend_for_user(session=session, user_id=user_id, top_k=max(limit * 2, 5))
    if lstm_result.items and lstm_result.source == "lstm":
        source_availability["lstm"] = True
        add_candidates(
            candidates=candidates,
            source="lstm",
            rows=[{"product_id": item.product_id, "score": item.score, "reason": lstm_result.reason} for item in lstm_result.items],
        )

    graph_rows = load_graph_candidates(user_id=user_id, limit=max(limit * 2, 5))
    if graph_rows:
        source_availability["graph"] = True
        add_candidates(
            candidates=candidates,
            source="graph",
            rows=[{"product_id": row.id, "score": row.score, "reason": row.reason} for row in graph_rows],
        )

    cleaned_query = query.strip() if query else None
    if cleaned_query:
        rag_rows = retrieve_products(cleaned_query, top_k=max(limit * 2, 5), client=effective_client)
        if rag_rows:
            source_availability["rag"] = True
            add_candidates(
                candidates=candidates,
                source="rag",
                rows=[
                    {
                        "product_id": row.id,
                        "score": row.score,
                        "reason": f"RAG match for query with terms: {', '.join(row.matched_terms) or 'n/a'}",
                    }
                    for row in rag_rows
                ],
            )

    popularity_rows = load_popularity_candidates(
        session=session,
        product_map=product_map,
        exclude_ids=interacted_ids,
        limit=max(limit * 3, 8),
    )
    if popularity_rows:
        source_availability["popularity"] = True
        add_candidates(
            candidates=candidates,
            source="popularity",
            rows=popularity_rows,
        )

    weighted_sources = {
        source: weight
        for source, weight in BASE_WEIGHTS.items()
        if source_availability.get(source)
        and (source != "popularity" or not any(source_availability[name] for name in ("lstm", "graph", "rag")) or source in any_candidate_sources(candidates))
    }
    normalized_weights = normalize_weights(weighted_sources)

    ranked_items: list[RecommendationItem] = []
    for product_id, candidate in candidates.items():
        product = product_map.get(product_id)
        if product is None:
            continue
        if interacted_ids and product_id in interacted_ids:
            continue
        final_score = sum(
            normalized_weights.get(source, 0.0) * score
            for source, score in candidate.source_scores.items()
        )
        if final_score <= 0:
            continue
        ranked_items.append(
            RecommendationItem(
                id=product.id,
                name=product.name,
                price=product.price,
                category=product.category_data.name,
                detail_type=product.detail_type,
                score=round(final_score, 4),
                reason=build_reason(candidate.source_scores, candidate.reasons),
                source_scores={source: round(score, 4) for source, score in candidate.source_scores.items()},
            )
        )

    ranked_items.sort(key=lambda item: (-item.score, item.id))
    selected_items = ranked_items[:limit]
    sources_used = sorted({source for item in selected_items for source in item.source_scores})
    latency_ms = round((time.perf_counter() - started) * 1000, 4)
    return RecommendationDiagnostics(
        response=RecommendationResponse(
            user_id=user_id,
            query=cleaned_query,
            total=len(selected_items),
            items=selected_items,
            sources_used=sources_used,
        ),
        latency_ms=latency_ms,
        source_availability=source_availability,
        normalized_weights=normalized_weights,
    )


def add_candidates(
    candidates: dict[int, CandidateSignal],
    source: str,
    rows: list[dict[str, Any]],
) -> None:
    if not rows:
        return
    max_score = max(float(row["score"]) for row in rows) or 1.0
    for row in rows:
        product_id = int(row["product_id"])
        normalized = round(float(row["score"]) / max_score, 4) if max_score else 0.0
        candidate = candidates.setdefault(product_id, CandidateSignal(product_id=product_id, source_scores={}, reasons=[]))
        candidate.source_scores[source] = max(candidate.source_scores.get(source, 0.0), normalized)
        reason = str(row.get("reason") or "").strip()
        if reason:
            candidate.reasons.append(reason)


def any_candidate_sources(candidates: dict[int, CandidateSignal]) -> set[str]:
    return {source for candidate in candidates.values() for source in candidate.source_scores}


def normalize_weights(weights: dict[str, float]) -> dict[str, float]:
    total = sum(weights.values())
    if total <= 0:
        return {}
    return {key: round(value / total, 4) for key, value in weights.items()}


def build_reason(source_scores: dict[str, float], reasons: list[str]) -> str:
    source_list = " + ".join(sorted(source_scores))
    unique_reasons: list[str] = []
    for reason in reasons:
        if reason not in unique_reasons:
            unique_reasons.append(reason)
    detail = "; ".join(unique_reasons[:3]) if unique_reasons else "scored from available recommendation signals"
    return f"Recommended from {source_list}. {detail}."


def load_products(client: ProductServiceClient | None = None) -> list[ProductCatalogItem]:
    settings = get_settings()
    snapshot_path = Path(settings.docs_artifacts_dir) / "datasets" / "phase-3-product-snapshot.json"
    if snapshot_path.exists():
        payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
        return [ProductCatalogItem.model_validate(item) for item in payload]
    return (client or ProductServiceClient()).fetch_products()


def load_user_interacted_product_ids(session: Session, user_id: int) -> set[int]:
    rows = session.scalars(
        select(BehaviorEvent.product_id)
        .where(BehaviorEvent.user_id == user_id, BehaviorEvent.product_id.is_not(None))
    ).all()
    return {int(product_id) for product_id in rows if product_id is not None}


def load_graph_candidates(user_id: int, limit: int) -> list[Any]:
    try:
        with Neo4jGraphStore() as store:
            return get_graph_recommendations(user_id=user_id, store=store, limit=limit).items
    except Exception:
        return []


def load_popularity_candidates(
    session: Session,
    product_map: dict[int, ProductCatalogItem],
    exclude_ids: set[int],
    limit: int,
) -> list[dict[str, Any]]:
    events = session.scalars(
        select(BehaviorEvent).where(BehaviorEvent.product_id.is_not(None)).order_by(BehaviorEvent.timestamp.asc(), BehaviorEvent.id.asc())
    ).all()
    scores = Counter()
    action_weights = {"view": 1.0, "click": 1.3, "add_to_cart": 2.0, "buy": 3.0}
    for event in events:
        if event.product_id is None or event.product_id in exclude_ids:
            continue
        scores[int(event.product_id)] += action_weights.get(event.action, 0.5)

    rows: list[dict[str, Any]] = []
    for product_id, score in scores.most_common(limit):
        if product_id not in product_map:
            continue
        rows.append(
            {
                "product_id": product_id,
                "score": round(float(score), 4),
                "reason": "Popularity fallback from aggregate interaction counts",
            }
        )
    if rows:
        return rows

    for product_id in sorted(product_map):
        if product_id in exclude_ids:
            continue
        rows.append(
            {
                "product_id": product_id,
                "score": 1.0 / (len(rows) + 1),
                "reason": "Catalog-order fallback because no popularity data is available",
            }
        )
        if len(rows) >= limit:
            break
    return rows


def export_phase7_artifacts(session: Session, client: ProductServiceClient | None = None) -> dict[str, object]:
    sample_requests = [
        {"user_id": 1, "query": "budget laptop", "label": "u1-budget-laptop"},
        {"user_id": 2, "query": "programming book", "label": "u2-programming-book"},
        {"user_id": 3, "query": None, "label": "u3-no-query"},
        {"user_id": 999, "query": "gift fashion", "label": "cold-start-query"},
    ]
    diagnostics_rows: list[dict[str, Any]] = []
    latency_rows: list[dict[str, Any]] = []
    score_distribution: list[float] = []
    source_score_rows: list[dict[str, Any]] = []
    top_product_counter: Counter[str] = Counter()
    model_counts = {"lstm": 0, "graph": 0, "rag": 0, "hybrid": 0, "popularity": 0}

    for sample in sample_requests:
        diagnostics = recommend_products_with_diagnostics(
            session=session,
            user_id=int(sample["user_id"]),
            query=sample["query"],
            limit=5,
            client=client,
        )
        latency_rows.append({"label": sample["label"], "latency_ms": diagnostics.latency_ms})
        model_counts["hybrid"] += len(diagnostics.response.items)
        for item in diagnostics.response.items:
            score_distribution.append(item.score)
            top_product_counter[item.name] += 1
            diagnostics_rows.append(
                {
                    "label": sample["label"],
                    "user_id": diagnostics.response.user_id,
                    "query": diagnostics.response.query,
                    "product_id": item.id,
                    "name": item.name,
                    "score": item.score,
                    "reason": item.reason,
                    "sources_used": ",".join(sorted(item.source_scores)),
                }
            )
            for source, value in item.source_scores.items():
                source_score_rows.append({"source": source, "score": value, "label": sample["label"]})
                model_counts[source] += 1

    settings = get_settings()
    docs_artifacts_dir = Path(settings.docs_artifacts_dir)
    docs_root_dir = docs_artifacts_dir.parent
    eval_dir = docs_artifacts_dir / "eval"
    tables_dir = docs_artifacts_dir / "tables"
    plots_dir = docs_root_dir / "plots" / "hybrid"
    reports_dir = docs_root_dir / "reports"
    for directory in [eval_dir, tables_dir, plots_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    summary_path = eval_dir / "phase-7-hybrid-summary.json"
    samples_path = tables_dir / "phase-7-recommendation-samples.csv"
    report_path = reports_dir / "phase-7-hybrid-recommendation-report.md"
    plot_paths = {
        "source_score_comparison": plots_dir / "source_score_comparison.png",
        "final_score_distribution": plots_dir / "final_score_distribution.png",
        "model_ablation_comparison": plots_dir / "model_ablation_comparison.png",
        "baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid": plots_dir / "baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid.png",
        "recommendation_latency": plots_dir / "recommendation_latency.png",
        "top_recommended_products": plots_dir / "top_recommended_products.png",
    }

    summary_payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sample_requests": sample_requests,
        "average_latency_ms": round(statistics.mean(row["latency_ms"] for row in latency_rows), 4) if latency_rows else 0.0,
        "sample_count": len(diagnostics_rows),
        "top_product_counts": dict(top_product_counter),
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    write_rows(samples_path, diagnostics_rows)

    plot_source_score_comparison(source_score_rows, plot_paths["source_score_comparison"])
    plot_final_score_distribution(score_distribution, plot_paths["final_score_distribution"])
    plot_model_ablation(source_score_rows, plot_paths["model_ablation_comparison"])
    plot_phase7_baseline_comparison(model_counts, plot_paths["baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid"])
    plot_recommendation_latency(latency_rows, plot_paths["recommendation_latency"])
    plot_top_recommended_products(top_product_counter, plot_paths["top_recommended_products"])

    report_path.write_text(
        build_phase7_report(summary_path=summary_path, samples_path=samples_path, plot_paths=plot_paths, summary_payload=summary_payload),
        encoding="utf-8",
    )
    return {
        "summary_path": str(summary_path),
        "samples_path": str(samples_path),
        "report_path": str(report_path),
        "plot_paths": {key: str(value) for key, value in plot_paths.items()},
    }


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        import csv

        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def plot_source_score_comparison(rows: list[dict[str, Any]], path: Path) -> None:
    grouped: dict[str, list[float]] = defaultdict(list)
    for row in rows:
        grouped[str(row["source"])].append(float(row["score"]))
    labels = sorted(grouped)
    values = [round(statistics.mean(grouped[label]), 4) for label in labels]
    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color="#2563eb")
    plt.title("Source Score Comparison")
    plt.ylabel("Mean normalized score")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_final_score_distribution(scores: list[float], path: Path) -> None:
    plt.figure(figsize=(8, 4))
    plt.hist(scores, bins=min(8, max(1, len(scores))), color="#0f766e", edgecolor="black")
    plt.title("Hybrid Final Score Distribution")
    plt.xlabel("Final score")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_model_ablation(rows: list[dict[str, Any]], path: Path) -> None:
    counts = Counter(str(row["source"]) for row in rows)
    labels = sorted(counts)
    values = [counts[label] for label in labels]
    plt.figure(figsize=(8, 4))
    plt.bar(labels, values, color="#7c3aed")
    plt.title("Model Ablation Comparison")
    plt.ylabel("Contribution count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_phase7_baseline_comparison(model_counts: dict[str, int], path: Path) -> None:
    labels = ["popularity", "lstm", "graph", "rag", "hybrid"]
    values = [model_counts.get(label, 0) for label in labels]
    plt.figure(figsize=(9, 4))
    plt.bar(labels, values, color=["#94a3b8", "#ea580c", "#16a34a", "#2563eb", "#dc2626"])
    plt.title("Baseline vs LSTM vs Graph vs RAG vs Hybrid")
    plt.ylabel("Recommended item count across sample runs")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_recommendation_latency(rows: list[dict[str, Any]], path: Path) -> None:
    labels = [str(row["label"]) for row in rows]
    values = [float(row["latency_ms"]) for row in rows]
    plt.figure(figsize=(9, 4))
    plt.bar(labels, values, color="#0891b2")
    plt.title("Recommendation Latency")
    plt.ylabel("Latency (ms)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_top_recommended_products(counter: Counter[str], path: Path) -> None:
    rows = counter.most_common(6)
    labels = [name for name, _ in rows]
    values = [count for _, count in rows]
    plt.figure(figsize=(9, 4))
    plt.bar(labels, values, color="#b45309")
    plt.title("Top Recommended Products")
    plt.ylabel("Frequency")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def build_phase7_report(
    summary_path: Path,
    samples_path: Path,
    plot_paths: dict[str, Path],
    summary_payload: dict[str, Any],
) -> str:
    evidence_lines = "\n".join(
        [f"- [{summary_path.name}]({_repo_link(summary_path)})", f"- [{samples_path.name}]({_repo_link(samples_path)})"]
        + [f"- [{path.name}]({_repo_link(path)})" for path in plot_paths.values()]
    )
    return (
        "# Phase 7 Hybrid Recommendation Report\n\n"
        "## Scoring formula\n\n"
        "- Base weights: `lstm=0.4`, `graph=0.3`, `rag=0.3`, `popularity=0.2`.\n"
        "- For each request, only available sources are kept and the weights are normalized back to sum to `1.0`.\n"
        "- Popularity participates as a fallback source when the richer signals are absent or sparse.\n\n"
        "## Fallback logic\n\n"
        "- Short history or missing model artifact: fallback from LSTM to popularity.\n"
        "- Missing query: RAG is skipped and its weight is redistributed.\n"
        "- Graph connection/runtime failure: graph source is dropped and the response still returns hybrid results from the remaining sources.\n\n"
        "## Sample summary\n\n"
        f"- Sample request count: `{len(summary_payload['sample_requests'])}`\n"
        f"- Hybrid items exported: `{summary_payload['sample_count']}`\n"
        f"- Average latency: `{summary_payload['average_latency_ms']} ms`\n\n"
        "## Request / response examples\n\n"
        "- See the exported sample table for grounded responses across query and cold-start cases.\n\n"
        "## Why hybrid is stronger than a single source\n\n"
        "- LSTM captures next-item sequence preference from interaction order.\n"
        "- Graph captures structural similarity and neighbor traversal from the Neo4j layer.\n"
        "- RAG captures explicit natural-language intent when a query is provided.\n"
        "- Popularity keeps the endpoint usable under sparse or degraded conditions.\n\n"
        "## Evidence\n\n"
        f"{evidence_lines}\n"
    )


def _repo_link(path: Path) -> str:
    normalized = path.as_posix()
    lowered = normalized.lower()
    repo_prefix = "d:/chap2_e-commerce/"
    docs_mount_prefix = "/workspace-docs/ai-service/"
    if lowered.startswith(repo_prefix):
        normalized = normalized[len("D:/CHAP2_E-COMMERCE/") :]
        return f"/d:/CHAP2_E-COMMERCE/{normalized}"
    if lowered.startswith(docs_mount_prefix):
        normalized = normalized[len("/workspace-docs/ai-service/") :]
        return f"/d:/CHAP2_E-COMMERCE/docs/ai-service/{normalized}"
    return normalized
