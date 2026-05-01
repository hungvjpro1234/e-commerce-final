import csv
import json
import math
from collections import Counter
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import matplotlib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.product_client import ProductServiceClient
from app.graph.store import Neo4jGraphStore
from app.models.behavior import BehaviorEvent
from app.schemas.graph import GraphRecommendationItem, GraphRecommendationResponse, GraphSyncResponse
from app.schemas.product import ProductCatalogItem
from app.services.catalog import fetch_product_catalog
from app.config import get_settings


matplotlib.use("Agg")
import matplotlib.pyplot as plt


def sync_graph(
    session: Session,
    store: Neo4jGraphStore | Any,
    client: ProductServiceClient | None = None,
) -> GraphSyncResponse:
    products = fetch_product_catalog(client=client)
    events = session.scalars(
        select(BehaviorEvent).order_by(BehaviorEvent.timestamp.asc(), BehaviorEvent.id.asc())
    ).all()

    store.clear_graph()

    user_ids = sorted({event.user_id for event in events})
    for product in products:
        store.upsert_product(
            {
                "id": product.id,
                "name": product.name,
                "price": float(product.price),
                "stock": product.stock,
                "category_id": product.category,
                "category_name": product.category_data.name,
                "detail_type": product.detail_type,
                "detail_json": json.dumps(product.detail, sort_keys=True),
            }
        )

    for user_id in user_ids:
        store.upsert_user(user_id)

    interaction_edge_count = 0
    for event in events:
        if event.product_id is None or event.action == "search":
            continue
        store.add_interaction(
            user_id=event.user_id,
            product_id=event.product_id,
            action=event.action,
            timestamp=event.timestamp.isoformat(),
        )
        interaction_edge_count += 1

    similar_edges = compute_similarity_edges(products)
    for edge in similar_edges:
        store.add_similarity(
            source_id=edge["source_id"],
            target_id=edge["target_id"],
            score=edge["score"],
            reason_summary=edge["reason_summary"],
        )

    return GraphSyncResponse(
        product_count=len(products),
        user_count=len(user_ids),
        interaction_edge_count=interaction_edge_count,
        similar_edge_count=len(similar_edges),
        message="Graph sync completed.",
    )


def get_graph_recommendations(
    user_id: int,
    store: Neo4jGraphStore | Any,
    limit: int = 5,
) -> GraphRecommendationResponse:
    rows = store.get_user_recommendations(user_id=user_id, limit=limit)
    if not rows:
        exclude_ids = store.get_user_interacted_product_ids(user_id=user_id)
        rows = [
            {
                "id": int(row["id"]),
                "name": str(row["name"]),
                "price": float(row["price"]),
                "category_name": str(row["category_name"]),
                "detail_type": str(row["detail_type"]),
                "score": float(row["interaction_count"]),
                "source_products": [],
                "similarity_reasons": ["Fallback popularity score"],
            }
            for row in store.get_popular_products(limit=limit, exclude_product_ids=exclude_ids)
        ]

    items = [
        GraphRecommendationItem(
            id=int(row["id"]),
            name=str(row["name"]),
            price=float(row["price"]),
            category=str(row["category_name"]),
            detail_type=str(row["detail_type"]),
            score=round(float(row["score"]), 4),
            reason=_format_recommendation_reason(row),
        )
        for row in rows
    ]
    return GraphRecommendationResponse(user_id=user_id, total=len(items), items=items)


def export_graph_artifacts(
    session: Session,
    store: Neo4jGraphStore | Any,
    client: ProductServiceClient | None = None,
) -> dict[str, object]:
    sync_summary = sync_graph(session=session, store=store, client=client)
    stats = store.get_graph_stats()
    settings = get_settings()
    docs_artifacts_dir = Path(settings.docs_artifacts_dir)
    tables_dir = docs_artifacts_dir / "tables"
    plots_dir = docs_artifacts_dir / "plots"
    reports_dir = docs_artifacts_dir / "reports"
    eval_dir = docs_artifacts_dir / "eval"
    screenshots_dir = docs_artifacts_dir / "screenshots"
    for directory in [tables_dir, plots_dir, reports_dir, eval_dir, screenshots_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    summary_json_path = eval_dir / "phase-4-graph-summary.json"
    relationship_counts_csv = tables_dir / "phase-4-relationship-counts.csv"
    top_products_csv = tables_dir / "phase-4-top-connected-products.csv"
    top_users_csv = tables_dir / "phase-4-top-users-by-activity.csv"
    recommendation_samples_csv = tables_dir / "phase-4-graph-recommendation-samples.csv"
    cypher_examples_csv = tables_dir / "phase-4-cypher-examples.csv"

    node_edge_plot = plots_dir / "phase-4-node-edge-counts.png"
    degree_distribution_plot = plots_dir / "phase-4-degree-distribution.png"
    relationship_distribution_plot = plots_dir / "phase-4-relationship-distribution.png"
    graph_snapshot_md = screenshots_dir / "phase-4-graph-snapshot.md"
    graph_report_md = reports_dir / "phase-4-graph-analysis.md"

    summary_payload = {
        "sync_summary": sync_summary.model_dump(),
        "graph_stats": stats,
    }
    summary_json_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    _write_rows(
        relationship_counts_csv,
        [
            {"relationship_type": key, "count": value}
            for key, value in sorted(stats["relationship_counts"].items())
        ],
    )
    _write_rows(top_products_csv, stats["top_products"])
    _write_rows(top_users_csv, stats["top_users"])
    _write_rows(cypher_examples_csv, store.get_cypher_examples())

    sample_user_ids = sorted({event.user_id for event in session.scalars(select(BehaviorEvent)).all()})[:5]
    recommendation_rows: list[dict[str, object]] = []
    for user_id in sample_user_ids:
        for item in get_graph_recommendations(user_id=user_id, store=store, limit=3).items:
            recommendation_rows.append(
                {
                    "user_id": user_id,
                    "product_id": item.id,
                    "name": item.name,
                    "score": item.score,
                    "reason": item.reason,
                }
            )
    _write_rows(recommendation_samples_csv, recommendation_rows)

    _plot_node_edge_counts(sync_summary, stats, node_edge_plot)
    _plot_degree_distribution(stats["degree_distribution"], degree_distribution_plot)
    _plot_relationship_distribution(stats["relationship_counts"], relationship_distribution_plot)

    graph_snapshot_md.write_text(_build_graph_snapshot(store.get_snapshot_edges()), encoding="utf-8")
    graph_report_md.write_text(_build_graph_report(sync_summary, stats), encoding="utf-8")

    return {
        "user_count": stats["user_count"],
        "product_count": stats["product_count"],
        "relationship_types": len(stats["relationship_counts"]),
        "graph_summary_path": str(summary_json_path),
        "graph_report_path": str(graph_report_md),
        "graph_snapshot_path": str(graph_snapshot_md),
    }


def compute_similarity_edges(products: Sequence[ProductCatalogItem]) -> list[dict[str, object]]:
    edges: list[dict[str, object]] = []
    ordered = sorted(products, key=lambda item: item.id)
    for index, source in enumerate(ordered):
        for target in ordered[index + 1 :]:
            score, reasons = _calculate_similarity(source, target)
            if score <= 0:
                continue
            edges.append(
                {
                    "source_id": source.id,
                    "target_id": target.id,
                    "score": round(score, 4),
                    "reason_summary": "; ".join(reasons),
                }
            )
    return edges


def _calculate_similarity(source: ProductCatalogItem, target: ProductCatalogItem) -> tuple[float, list[str]]:
    score = 0.0
    reasons: list[str] = []
    if source.category == target.category:
        score += 0.35
        reasons.append("same category")
    if source.detail_type == target.detail_type:
        score += 0.35
        reasons.append("same detail_type")

    max_price = max(float(source.price), float(target.price), 1.0)
    price_delta = abs(float(source.price) - float(target.price)) / max_price
    price_similarity = max(0.0, 1.0 - price_delta)
    if price_similarity >= 0.8:
        score += 0.2 * price_similarity
        reasons.append("close price")

    source_tokens = _extract_keywords(source)
    target_tokens = _extract_keywords(target)
    overlap = source_tokens & target_tokens
    if overlap:
        union_size = max(1, len(source_tokens | target_tokens))
        keyword_score = len(overlap) / union_size
        score += min(0.1, keyword_score)
        reasons.append(f"keyword overlap: {', '.join(sorted(overlap)[:4])}")

    if score < 0.35:
        return 0.0, []
    return min(score, 0.99), reasons


def _extract_keywords(product: ProductCatalogItem) -> set[str]:
    raw_parts = [product.name, product.category_data.name, product.detail_type]
    raw_parts.extend(str(value) for value in product.detail.values())
    tokens: set[str] = set()
    for part in raw_parts:
        normalized = (
            str(part)
            .lower()
            .replace("-", " ")
            .replace("_", " ")
            .replace("/", " ")
            .replace(":", " ")
        )
        for token in normalized.split():
            stripped = token.strip(" ,.;()[]{}")
            if len(stripped) >= 3:
                tokens.add(stripped)
    return tokens


def _format_recommendation_reason(row: dict[str, Any]) -> str:
    sources = row.get("source_products") or []
    reasons = row.get("similarity_reasons") or []
    joined_sources = ", ".join(str(source) for source in sources[:3]) if sources else "graph popularity"
    joined_reasons = ", ".join(str(reason) for reason in reasons[:2]) if reasons else "graph traversal"
    return f"Sources: {joined_sources}. Signals: {joined_reasons}."


def _write_rows(path: Path, rows: Sequence[dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _plot_node_edge_counts(sync_summary: GraphSyncResponse, stats: dict[str, Any], path: Path) -> None:
    labels = ["Users", "Products", "Interactions", "Similar"]
    values = [
        sync_summary.user_count,
        sync_summary.product_count,
        sync_summary.interaction_edge_count,
        sync_summary.similar_edge_count,
    ]
    plt.figure(figsize=(8, 5))
    plt.bar(labels, values, color=["#4c78a8", "#f58518", "#54a24b", "#e45756"])
    plt.title("Graph Node and Edge Counts")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _plot_degree_distribution(rows: Sequence[dict[str, Any]], path: Path) -> None:
    degrees = [int(row["degree"]) for row in rows]
    plt.figure(figsize=(8, 5))
    plt.hist(degrees, bins=min(10, max(1, len(set(degrees)))), color="#72b7b2", edgecolor="black")
    plt.title("Product Degree Distribution")
    plt.xlabel("Degree")
    plt.ylabel("Product Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _plot_relationship_distribution(relationship_counts: dict[str, int], path: Path) -> None:
    labels = list(relationship_counts.keys())
    values = [relationship_counts[label] for label in labels]
    plt.figure(figsize=(9, 5))
    plt.bar(labels, values, color="#b279a2")
    plt.title("Graph Relationship Distribution")
    plt.xlabel("Relationship Type")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def _build_graph_snapshot(rows: Sequence[dict[str, Any]]) -> str:
    lines = ["# Phase 4 Graph Snapshot", "", "```mermaid", "graph LR"]
    for row in rows:
        source = str(row["source"]).replace(":", "_").replace(" ", "_")
        target = str(row["target"]).replace(":", "_").replace(" ", "_").replace("-", "_")
        label = str(row["relationship_type"])
        lines.append(f"    {source}[\"{row['source']}\"] -->|{label}| {target}[\"{row['target']}\"]")
    lines.append("```")
    lines.append("")
    lines.append("This snapshot is generated from the live Neo4j contents after Phase 4 sync.")
    return "\n".join(lines)


def _build_graph_report(sync_summary: GraphSyncResponse, stats: dict[str, Any]) -> str:
    return (
        "# Phase 4 Graph Analysis\n\n"
        "## Summary\n\n"
        f"- User nodes: `{stats['user_count']}`\n"
        f"- Product nodes: `{stats['product_count']}`\n"
        f"- Interaction edges: `{sync_summary.interaction_edge_count}`\n"
        f"- Similar edges: `{sync_summary.similar_edge_count}`\n\n"
        "## Relationship counts\n\n"
        "| Relationship | Count |\n"
        "| --- | --- |\n"
        + "".join(
            f"| {relationship_type} | {count} |\n"
            for relationship_type, count in sorted(stats["relationship_counts"].items())
        )
        + "\n## Artifact links\n\n"
        "- Graph summary: [phase-4-graph-summary.json](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/eval/phase-4-graph-summary.json)\n"
        "- Graph snapshot: [phase-4-graph-snapshot.md](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/screenshots/phase-4-graph-snapshot.md)\n"
        "- Top connected products: [phase-4-top-connected-products.csv](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/tables/phase-4-top-connected-products.csv)\n"
        "- Recommendation samples: [phase-4-graph-recommendation-samples.csv](/d:/CHAP2_E-COMMERCE/docs/ai-service/artifacts/tables/phase-4-graph-recommendation-samples.csv)\n\n"
        "## Methodology\n\n"
        "- Product nodes are sourced from the live product snapshot fetched from `product-service`.\n"
        "- User-product interaction edges are sourced from persisted behavior events excluding `search` events.\n"
        "- `SIMILAR` edges combine same-category, same-detail-type, close-price, and keyword-overlap signals.\n"
        "- Graph recommendation traverses user interactions into `SIMILAR` neighbors and falls back to graph popularity when needed.\n\n"
        "## Limitations and trade-offs\n\n"
        "- `SIMILAR` scoring is heuristic and intentionally lightweight for this phase.\n"
        "- Search intent is not yet represented as its own graph node type.\n"
        "- Graph quality will improve as later phases add richer retrieval and model-based signals.\n"
    )
