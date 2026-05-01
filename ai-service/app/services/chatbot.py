from __future__ import annotations

import json
import statistics
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import matplotlib
from sqlalchemy.orm import Session

from app.config import get_settings
from app.schemas.chatbot import ChatbotProductSuggestion, ChatbotRequest, ChatbotResponse
from app.services.rag import retrieve_products
from app.services.recommend import recommend_products_with_diagnostics


matplotlib.use("Agg")
import matplotlib.pyplot as plt


QUERY_TYPE_KEYWORDS: dict[str, set[str]] = {
    "budget": {"cheap", "budget", "gia re", "re", "affordable", "under"},
    "gift": {"gift", "qua", "present"},
    "fashion": {"fashion", "hoodie", "shirt", "wear", "thoi trang"},
    "book": {"book", "books", "sach", "programming", "architecture"},
    "electronics": {"laptop", "phone", "earbuds", "electronics", "computer"},
}


def generate_chatbot_response(session: Session, payload: ChatbotRequest) -> ChatbotResponse:
    query = payload.message.strip()
    query_type = classify_query_type(query)
    rag_results = retrieve_products(expand_query_for_rag(query=query, query_type=query_type), top_k=5)

    personalized_scores: dict[int, float] = {}
    if payload.user_id is not None:
        diagnostics = recommend_products_with_diagnostics(
            session=session,
            user_id=payload.user_id,
            query=query,
            limit=5,
        )
        personalized_scores = {
            item.id: item.score for item in diagnostics.response.items
        }
        if not rag_results and diagnostics.response.items:
            fallback_products = [
                {
                    "id": item.id,
                    "name": item.name,
                    "price": item.price,
                    "category": item.category,
                    "detail_type": item.detail_type,
                    "score": item.score,
                    "reason": f"Fallback from recommendation pipeline. {item.reason}",
                    "context": f"{item.name} | {item.category} | {item.detail_type} | price={item.price} | recommendation_fallback=true",
                }
                for item in diagnostics.response.items[:3]
            ]
            suggestions = [
                ChatbotProductSuggestion(
                    id=item["id"],
                    name=item["name"],
                    price=item["price"],
                    category=item["category"],
                    detail_type=item["detail_type"],
                    score=item["score"],
                    reason=item["reason"],
                )
                for item in fallback_products
            ]
            return ChatbotResponse(
                answer=build_chatbot_answer(query=query, query_type=query_type, products=suggestions),
                products=suggestions,
                retrieved_context=[item["context"] for item in fallback_products],
                query_type=query_type,
            )

    ranked_products = rerank_chatbot_products(
        rag_results=rag_results,
        personalized_scores=personalized_scores,
    )
    selected_products = ranked_products[:3]
    suggestions = [
        ChatbotProductSuggestion(
            id=item["id"],
            name=item["name"],
            price=item["price"],
            category=item["category"],
            detail_type=item["detail_type"],
            score=item["score"],
            reason=item["reason"],
        )
        for item in selected_products
    ]
    retrieved_context = [item["context"] for item in selected_products]
    answer = build_chatbot_answer(query=query, query_type=query_type, products=suggestions)
    return ChatbotResponse(
        answer=answer,
        products=suggestions,
        retrieved_context=retrieved_context,
        query_type=query_type,
    )


def classify_query_type(query: str) -> str:
    lowered = query.lower()
    for query_type, keywords in QUERY_TYPE_KEYWORDS.items():
        if any(keyword in lowered for keyword in keywords):
            return query_type
    return "general"


def expand_query_for_rag(query: str, query_type: str) -> str:
    expansions = {
        "budget": "budget affordable cheap laptop electronics deal",
        "gift": "gift present popular fashion book electronics",
        "fashion": "fashion clothing hoodie shirt style",
        "book": "programming book architecture software learning",
        "electronics": "electronics laptop earbuds device technology",
        "general": "product recommendation shopping catalog",
    }
    return f"{query} {expansions.get(query_type, expansions['general'])}".strip()


def rerank_chatbot_products(
    rag_results: list[Any],
    personalized_scores: dict[int, float],
) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for item in rag_results:
        rag_score = float(item.score)
        personalized = float(personalized_scores.get(item.id, 0.0))
        final_score = 0.75 * rag_score + 0.25 * personalized
        reason_parts = [f"Grounded RAG match via terms: {', '.join(item.matched_terms) or 'n/a'}"]
        if personalized > 0:
            reason_parts.append("boosted by user recommendation history")
        ranked.append(
            {
                "id": item.id,
                "name": item.name,
                "price": item.price,
                "category": item.category,
                "detail_type": item.detail_type,
                "score": round(final_score, 4),
                "reason": ". ".join(reason_parts).strip() + ".",
                "context": f"{item.name} | {item.category} | {item.detail_type} | price={item.price} | matched_terms={', '.join(item.matched_terms) or 'n/a'}",
            }
        )
    ranked.sort(key=lambda row: (-row["score"], row["id"]))
    return ranked


def build_chatbot_answer(
    query: str,
    query_type: str,
    products: list[ChatbotProductSuggestion],
) -> str:
    if not products:
        return "Toi chua tim duoc san pham phu hop tu catalog hien tai. Ban co the mo ta cu the hon ve muc gia, loai san pham, hoac muc dich su dung."

    lead = products[0]
    if query_type == "budget":
        extra_count = max(0, len(products) - 1)
        comparison_clause = (
            f", va toi kem them {extra_count} lua chon de ban so sanh."
            if extra_count > 0
            else "."
        )
        return (
            f"Voi nhu cau '{query}', toi uu tien cac san pham co muc gia de tiep can hon va lien quan truc tiep den truy van. "
            f"Goi y dau tien la {lead.name} gia {lead.price}{comparison_clause}"
        )
    if query_type == "gift":
        return (
            f"Neu ban dang tim qua tang, toi uu tien nhung san pham de hinh dung muc dich su dung va de chon nhanh. "
            f"{lead.name} la goi y noi bat nhat, sau do la cac lua chon cung chu de de ban can nhac."
        )
    if query_type in {"book", "electronics", "fashion"}:
        return (
            f"Toi da truy xuat catalog theo truy van '{query}' va chon cac san pham co do phu hop cao nhat. "
            f"{lead.name} dang la ket qua phu hop nhat, cac san pham con lai giup ban mo rong pham vi lua chon trong cung nhom nhu cau."
        )
    return (
        f"Toi da tim cac san pham lien quan nhat cho truy van '{query}'. "
        f"{lead.name} la ket qua noi bat nhat, va cac goi y di kem duoc lay tu chinh du lieu san pham retrieve duoc."
    )


def export_phase8_artifacts(session: Session) -> dict[str, object]:
    sample_requests = [
        {"user_id": 1, "message": "toi can laptop gia re", "label": "budget-laptop"},
        {"user_id": 2, "message": "goi y sach hoc lap trinh", "label": "programming-book"},
        {"user_id": 3, "message": "tim san pham thoi trang", "label": "fashion"},
        {"user_id": 999, "message": "san pham nao phu hop de lam qua", "label": "gift"},
    ]
    latency_rows: list[dict[str, Any]] = []
    query_type_counts: Counter[str] = Counter()
    score_samples: list[float] = []
    category_counts: Counter[str] = Counter()
    transcript_rows: list[dict[str, Any]] = []

    for sample in sample_requests:
        started = time.perf_counter()
        response = generate_chatbot_response(
            session=session,
            payload=ChatbotRequest(user_id=sample["user_id"], message=sample["message"]),
        )
        latency_ms = round((time.perf_counter() - started) * 1000, 4)
        latency_rows.append({"label": sample["label"], "latency_ms": latency_ms})
        query_type_counts[response.query_type] += 1
        transcript_rows.append(
            {
                "label": sample["label"],
                "user_id": sample["user_id"],
                "message": sample["message"],
                "query_type": response.query_type,
                "answer": response.answer,
                "top_product": response.products[0].name if response.products else None,
            }
        )
        for product in response.products:
            score_samples.append(product.score)
            category_counts[product.category] += 1

    settings = get_settings()
    docs_artifacts_dir = Path(settings.docs_artifacts_dir)
    docs_root_dir = docs_artifacts_dir.parent
    eval_dir = docs_artifacts_dir / "eval"
    tables_dir = docs_artifacts_dir / "tables"
    plots_dir = docs_root_dir / "plots" / "rag"
    reports_dir = docs_root_dir / "reports"
    for directory in [eval_dir, tables_dir, plots_dir, reports_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    summary_path = eval_dir / "phase-8-chatbot-summary.json"
    transcripts_path = tables_dir / "phase-8-chatbot-case-studies.csv"
    report_path = reports_dir / "phase-8-chatbot-report.md"
    plot_paths = {
        "chatbot_latency": plots_dir / "chatbot_latency.png",
        "query_type_distribution": plots_dir / "query_type_distribution.png",
        "chatbot_retrieval_score_distribution": plots_dir / "chatbot_retrieval_score_distribution.png",
        "chatbot_top_product_categories": plots_dir / "chatbot_top_product_categories.png",
    }

    summary_payload = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "sample_requests": sample_requests,
        "average_latency_ms": round(statistics.mean(row["latency_ms"] for row in latency_rows), 4),
        "query_type_counts": dict(query_type_counts),
        "retrieval_score_mean": round(statistics.mean(score_samples), 4) if score_samples else 0.0,
        "top_categories": dict(category_counts),
    }
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
    write_rows(transcripts_path, transcript_rows)

    plot_chatbot_latency(latency_rows, plot_paths["chatbot_latency"])
    plot_query_type_distribution(query_type_counts, plot_paths["query_type_distribution"])
    plot_score_distribution(score_samples, plot_paths["chatbot_retrieval_score_distribution"])
    plot_top_categories(category_counts, plot_paths["chatbot_top_product_categories"])

    report_path.write_text(
        build_phase8_report(summary_path=summary_path, transcripts_path=transcripts_path, plot_paths=plot_paths, transcripts=transcript_rows),
        encoding="utf-8",
    )
    return {
        "summary_path": str(summary_path),
        "transcripts_path": str(transcripts_path),
        "report_path": str(report_path),
        "plot_paths": {key: str(value) for key, value in plot_paths.items()},
    }


def write_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    import csv

    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def plot_chatbot_latency(rows: list[dict[str, Any]], path: Path) -> None:
    plt.figure(figsize=(8, 4))
    plt.bar([row["label"] for row in rows], [row["latency_ms"] for row in rows], color="#0891b2")
    plt.title("Chatbot Latency")
    plt.ylabel("Latency (ms)")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_query_type_distribution(counter: Counter[str], path: Path) -> None:
    plt.figure(figsize=(7, 4))
    plt.bar(list(counter.keys()), list(counter.values()), color="#7c3aed")
    plt.title("Chatbot Query Type Distribution")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_score_distribution(scores: list[float], path: Path) -> None:
    plt.figure(figsize=(8, 4))
    plt.hist(scores, bins=min(8, max(1, len(scores))), color="#2563eb", edgecolor="black")
    plt.title("Chatbot Retrieval Score Distribution")
    plt.xlabel("Score")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def plot_top_categories(counter: Counter[str], path: Path) -> None:
    rows = counter.most_common(6)
    plt.figure(figsize=(8, 4))
    plt.bar([name for name, _ in rows], [count for _, count in rows], color="#b45309")
    plt.title("Chatbot Top Product Categories")
    plt.ylabel("Frequency")
    plt.xticks(rotation=20, ha="right")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def build_phase8_report(
    summary_path: Path,
    transcripts_path: Path,
    plot_paths: dict[str, Path],
    transcripts: list[dict[str, Any]],
) -> str:
    case_lines = "\n".join(
        f"- `{row['message']}` -> top product: `{row['top_product']}`"
        for row in transcripts
    )
    evidence_lines = "\n".join(
        [f"- [{summary_path.name}]({_repo_link(summary_path)})", f"- [{transcripts_path.name}]({_repo_link(transcripts_path)})"]
        + [f"- [{path.name}]({_repo_link(path)})" for path in plot_paths.values()]
    )
    return (
        "# Phase 8 Chatbot Report\n\n"
        "## Chatbot pipeline\n\n"
        "- Receive `user_id` and natural-language `message`.\n"
        "- Classify lightweight intent from the message.\n"
        "- Retrieve real products from the RAG index.\n"
        "- Optionally boost ranking with personalized recommendation scores when `user_id` is available.\n"
        "- Generate a grounded template answer from the retrieved product context.\n\n"
        "## Input / output examples\n\n"
        f"{case_lines}\n\n"
        "## Case studies\n\n"
        "- `toi can laptop gia re`\n"
        "- `goi y sach hoc lap trinh`\n"
        "- `tim san pham thoi trang`\n"
        "- `san pham nao phu hop de lam qua`\n\n"
        "## Limitations\n\n"
        "- The response generation is template-based rather than LLM-based, so phrasing is controlled and concise.\n"
        "- Query understanding is heuristic; richer NLP can improve intent extraction later.\n"
        "- Retrieval quality still depends on the small current product corpus.\n\n"
        "## Why template generation is used now\n\n"
        "- It keeps the chatbot grounded in retrieved catalog data and avoids fabricated product claims.\n"
        "- It is sufficient for the Chapter 3 MVP without introducing an external LLM dependency.\n\n"
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
