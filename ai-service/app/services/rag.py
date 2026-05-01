from __future__ import annotations

import json
import math
import pickle
import re
import statistics
import time
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib

from app.clients.product_client import ProductServiceClient
from app.config import get_settings
from app.schemas.product import ProductCatalogItem
from app.schemas.rag import RagRetrievedProduct, RagRebuildResponse


matplotlib.use("Agg")
import matplotlib.pyplot as plt


TOKEN_PATTERN = re.compile(r"[a-z0-9]+")
STOPWORDS = {
    "a",
    "an",
    "and",
    "cho",
    "cua",
    "de",
    "gia",
    "hai",
    "i",
    "is",
    "it",
    "la",
    "lam",
    "mot",
    "nang",
    "nhe",
    "nhung",
    "or",
    "pham",
    "phamvi",
    "san",
    "the",
    "toi",
    "va",
    "voi",
}


@dataclass
class RagDocument:
    doc_id: str
    product_id: int
    category_name: str
    detail_type: str
    text: str
    metadata: dict[str, Any]


@dataclass
class RagQueryResult:
    product_id: int
    score: float
    matched_terms: list[str]


class RagIndexer:
    def __init__(self) -> None:
        settings = get_settings()
        self.runtime_dir = Path(settings.artifacts_dir) / "rag"
        self.docs_artifacts_dir = Path(settings.docs_artifacts_dir)
        self.docs_root_dir = self.docs_artifacts_dir.parent
        self.docs_artifacts_dir.mkdir(parents=True, exist_ok=True)
        self.docs_root_dir.mkdir(parents=True, exist_ok=True)
        self.runtime_dir.mkdir(parents=True, exist_ok=True)

    def rebuild(
        self,
        client: ProductServiceClient | None = None,
        sample_queries: list[str] | None = None,
    ) -> RagRebuildResponse:
        start_time = time.perf_counter()
        documents = _load_rag_documents(client=client)
        matrix_payload = _build_tfidf_matrix(documents)
        method = "tfidf-cosine"
        runtime_paths = self._runtime_paths(method=method)

        with runtime_paths["matrix"].open("wb") as handle:
            pickle.dump(matrix_payload, handle)
        runtime_paths["documents"].write_text(
            json.dumps([document.__dict__ for document in documents], indent=2),
            encoding="utf-8",
        )

        queries = sample_queries or _default_sample_queries(documents)
        benchmark = self._benchmark_queries(queries=queries, documents=documents, matrix_payload=matrix_payload)
        build_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
        metadata = {
            "method": method,
            "document_count": len(documents),
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "build_time_ms": build_time_ms,
            "sample_queries": queries,
            "average_latency_ms": benchmark["average_latency_ms"],
        }
        runtime_paths["metadata"].write_text(json.dumps(metadata, indent=2), encoding="utf-8")

        artifact_paths = self._export_phase5_artifacts(
            documents=documents,
            benchmark=benchmark,
            metadata=metadata,
            client=client,
        )
        artifact_paths["runtime_matrix"] = str(runtime_paths["matrix"])
        artifact_paths["runtime_documents"] = str(runtime_paths["documents"])
        artifact_paths["runtime_metadata"] = str(runtime_paths["metadata"])
        return RagRebuildResponse(
            message="RAG index rebuilt successfully.",
            method=method,
            document_count=len(documents),
            artifact_paths=artifact_paths,
        )

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        client: ProductServiceClient | None = None,
    ) -> list[RagRetrievedProduct]:
        documents, matrix_payload, _ = self.load_runtime_state(client=client)
        results = _query_documents(query=query, documents=documents, matrix_payload=matrix_payload, top_k=top_k)
        product_map = {product.id: product for product in _load_products(client=client)}
        document_map = {document.product_id: document for document in documents}

        items: list[RagRetrievedProduct] = []
        for result in results:
            product = product_map.get(result.product_id)
            document = document_map.get(result.product_id)
            if product is None or document is None:
                continue
            items.append(
                RagRetrievedProduct(
                    id=product.id,
                    name=product.name,
                    price=product.price,
                    category=product.category_data.name,
                    detail_type=product.detail_type,
                    score=round(result.score, 4),
                    matched_terms=result.matched_terms,
                    document_text=document.text,
                )
            )
        return items

    def load_runtime_state(
        self,
        client: ProductServiceClient | None = None,
    ) -> tuple[list[RagDocument], dict[str, Any], dict[str, Any]]:
        runtime_paths = self._runtime_paths(method="tfidf-cosine")
        if not all(path.exists() for path in runtime_paths.values()):
            self.rebuild(client=client)

        with runtime_paths["matrix"].open("rb") as handle:
            matrix_payload = pickle.load(handle)
        documents_data = json.loads(runtime_paths["documents"].read_text(encoding="utf-8"))
        metadata = json.loads(runtime_paths["metadata"].read_text(encoding="utf-8"))
        documents = [RagDocument(**document_data) for document_data in documents_data]
        return documents, matrix_payload, metadata

    def _runtime_paths(self, method: str) -> dict[str, Path]:
        safe_method = method.replace("-", "_")
        return {
            "matrix": self.runtime_dir / f"{safe_method}_index.pkl",
            "documents": self.runtime_dir / f"{safe_method}_documents.json",
            "metadata": self.runtime_dir / f"{safe_method}_metadata.json",
        }

    def _benchmark_queries(
        self,
        queries: list[str],
        documents: list[RagDocument],
        matrix_payload: dict[str, Any],
    ) -> dict[str, Any]:
        latencies_ms: list[float] = []
        all_scores: list[float] = []
        comparison_rows: list[dict[str, Any]] = []

        for query in queries:
            started = time.perf_counter()
            results = _query_documents(query=query, documents=documents, matrix_payload=matrix_payload, top_k=5)
            latencies_ms.append(round((time.perf_counter() - started) * 1000, 4))
            all_scores.extend(result.score for result in results)
            comparison_rows.append(
                {
                    "query": query,
                    "method": "tfidf-cosine",
                    "top_score": round(results[0].score, 4) if results else 0.0,
                    "result_count": len(results),
                }
            )

        return {
            "queries": queries,
            "latencies_ms": latencies_ms,
            "score_samples": all_scores,
            "comparison_rows": comparison_rows,
            "average_latency_ms": round(statistics.mean(latencies_ms), 4) if latencies_ms else 0.0,
        }

    def _export_phase5_artifacts(
        self,
        documents: list[RagDocument],
        benchmark: dict[str, Any],
        metadata: dict[str, Any],
        client: ProductServiceClient | None = None,
    ) -> dict[str, str]:
        eval_dir = self.docs_artifacts_dir / "eval"
        plots_dir = self.docs_root_dir / "plots" / "rag"
        reports_dir = self.docs_root_dir / "reports"
        for directory in [eval_dir, plots_dir, reports_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        summary_path = eval_dir / "phase-5-rag-summary.json"
        summary_path.write_text(
            json.dumps(
                {
                    "document_count": len(documents),
                    "method": metadata["method"],
                    "build_time_ms": metadata["build_time_ms"],
                    "average_latency_ms": metadata["average_latency_ms"],
                    "queries": benchmark["queries"],
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        latency_plot = plots_dir / "retrieval_latency.png"
        score_plot = plots_dir / "topk_score_distribution.png"
        build_time_plot = plots_dir / "index_build_time.png"
        comparison_plot = plots_dir / "retrieval_method_comparison.png"

        _plot_retrieval_latency(benchmark["queries"], benchmark["latencies_ms"], latency_plot)
        _plot_score_distribution(benchmark["score_samples"], score_plot)
        _plot_build_time(metadata["build_time_ms"], build_time_plot)
        _plot_method_comparison(benchmark["comparison_rows"], comparison_plot)

        sample_query = benchmark["queries"][0] if benchmark["queries"] else "laptop"
        sample_results = self.retrieve(sample_query, top_k=5, client=client)
        report_path = reports_dir / "phase-5-rag-report.md"
        report_path.write_text(
            _build_phase5_report(
                sample_query=sample_query,
                sample_results=sample_results,
                metadata=metadata,
                summary_path=summary_path,
                latency_plot=latency_plot,
                score_plot=score_plot,
                build_time_plot=build_time_plot,
                comparison_plot=comparison_plot,
            ),
            encoding="utf-8",
        )

        return {
            "phase5_summary": str(summary_path),
            "phase5_report": str(report_path),
            "retrieval_latency_plot": str(latency_plot),
            "topk_score_distribution_plot": str(score_plot),
            "index_build_time_plot": str(build_time_plot),
            "retrieval_method_comparison_plot": str(comparison_plot),
        }


def rebuild_rag_index(client: ProductServiceClient | None = None) -> RagRebuildResponse:
    return RagIndexer().rebuild(client=client)


def retrieve_products(query: str, top_k: int = 5, client: ProductServiceClient | None = None) -> list[RagRetrievedProduct]:
    return RagIndexer().retrieve(query=query, top_k=top_k, client=client)


def _load_rag_documents(client: ProductServiceClient | None = None) -> list[RagDocument]:
    products = _load_products(client=client)
    corpus_records = _load_phase3_corpus() or _build_product_corpus(products)
    product_map = {product.id: product for product in products}
    documents: list[RagDocument] = []
    for record in corpus_records:
        product = product_map[int(record["product_id"])]
        documents.append(
            RagDocument(
                doc_id=str(record["doc_id"]),
                product_id=product.id,
                category_name=product.category_data.name,
                detail_type=product.detail_type,
                text=str(record["text"]),
                metadata={
                    "name": product.name,
                    "price": product.price,
                    "category": product.category_data.name,
                    "detail_type": product.detail_type,
                },
            )
        )
    return documents


def _load_products(client: ProductServiceClient | None = None) -> list[ProductCatalogItem]:
    snapshot_products = _load_phase3_product_snapshot()
    if snapshot_products:
        return snapshot_products
    return (client or ProductServiceClient()).fetch_products()


def _load_phase3_product_snapshot() -> list[ProductCatalogItem]:
    settings = get_settings()
    snapshot_path = Path(settings.docs_artifacts_dir) / "datasets" / "phase-3-product-snapshot.json"
    if not snapshot_path.exists():
        return []
    payload = json.loads(snapshot_path.read_text(encoding="utf-8"))
    return [ProductCatalogItem.model_validate(item) for item in payload]


def _load_phase3_corpus() -> list[dict[str, Any]]:
    settings = get_settings()
    corpus_path = Path(settings.docs_artifacts_dir) / "datasets" / "phase-3-product-document-corpus.jsonl"
    if not corpus_path.exists():
        return []
    rows: list[dict[str, Any]] = []
    with corpus_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped:
                rows.append(json.loads(stripped))
    return rows


def _build_product_corpus(products: list[ProductCatalogItem]) -> list[dict[str, Any]]:
    corpus_records: list[dict[str, Any]] = []
    for product in products:
        detail_parts = [f"{key}: {value}" for key, value in sorted(product.detail.items())]
        corpus_records.append(
            {
                "doc_id": f"product-{product.id}",
                "product_id": product.id,
                "category_id": product.category,
                "category_name": product.category_data.name,
                "detail_type": product.detail_type,
                "text": " | ".join(
                    [
                        product.name,
                        f"category: {product.category_data.name}",
                        f"detail_type: {product.detail_type}",
                        f"price: {product.price}",
                        *detail_parts,
                    ]
                ),
            }
        )
    return corpus_records


def _normalize_tokens(text: str) -> list[str]:
    return [token for token in TOKEN_PATTERN.findall(text.lower()) if token not in STOPWORDS]


def _build_tfidf_matrix(documents: list[RagDocument]) -> dict[str, Any]:
    tokenized_documents = [_normalize_tokens(document.text) for document in documents]
    document_frequency = Counter(token for tokens in tokenized_documents for token in set(tokens))
    total_documents = max(len(documents), 1)
    idf = {
        token: math.log((1 + total_documents) / (1 + frequency)) + 1.0
        for token, frequency in document_frequency.items()
    }

    vectors: list[dict[str, float]] = []
    norms: list[float] = []
    for tokens in tokenized_documents:
        term_frequency = Counter(tokens)
        token_count = max(len(tokens), 1)
        vector = {
            token: (count / token_count) * idf[token]
            for token, count in term_frequency.items()
            if token in idf
        }
        vectors.append(vector)
        norms.append(math.sqrt(sum(value * value for value in vector.values())))

    return {
        "idf": idf,
        "vectors": vectors,
        "norms": norms,
    }


def _query_documents(
    query: str,
    documents: list[RagDocument],
    matrix_payload: dict[str, Any],
    top_k: int,
) -> list[RagQueryResult]:
    query_tokens = _normalize_tokens(query)
    if not query_tokens:
        return []

    idf = matrix_payload["idf"]
    term_frequency = Counter(query_tokens)
    token_count = max(len(query_tokens), 1)
    query_vector = {
        token: (count / token_count) * idf[token]
        for token, count in term_frequency.items()
        if token in idf
    }
    query_norm = math.sqrt(sum(value * value for value in query_vector.values()))
    if query_norm == 0:
        return []

    scored: list[RagQueryResult] = []
    for index, document in enumerate(documents):
        document_vector = matrix_payload["vectors"][index]
        document_norm = matrix_payload["norms"][index]
        if document_norm == 0:
            continue
        dot_product = sum(query_vector[token] * document_vector.get(token, 0.0) for token in query_vector)
        if dot_product <= 0:
            continue
        matched_terms = sorted(token for token in query_vector if token in document_vector)
        scored.append(
            RagQueryResult(
                product_id=document.product_id,
                score=dot_product / (query_norm * document_norm),
                matched_terms=matched_terms,
            )
        )

    return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]


def _default_sample_queries(documents: list[RagDocument]) -> list[str]:
    detail_types = sorted({document.detail_type for document in documents})
    categories = sorted({document.category_name.lower() for document in documents})
    queries: list[str] = []
    if "electronics" in detail_types:
        queries.append("laptop electronics budget")
    if "book" in detail_types:
        queries.append("programming architecture book")
    if categories:
        queries.append(f"best {categories[0]} product")
    return queries or ["product recommendation"]


def _plot_retrieval_latency(queries: list[str], latencies_ms: list[float], output_path: Path) -> None:
    plt.figure(figsize=(8, 4))
    labels = [query[:18] + ("..." if len(query) > 18 else "") for query in queries]
    plt.bar(labels, latencies_ms, color="#0f766e")
    plt.title("RAG Retrieval Latency")
    plt.xlabel("Query")
    plt.ylabel("Latency (ms)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_score_distribution(scores: list[float], output_path: Path) -> None:
    plt.figure(figsize=(8, 4))
    if scores:
        plt.hist(scores, bins=min(8, max(1, len(scores))), color="#1d4ed8", edgecolor="black")
    plt.title("Top-k Retrieval Score Distribution")
    plt.xlabel("Cosine similarity")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_build_time(build_time_ms: float, output_path: Path) -> None:
    plt.figure(figsize=(5, 4))
    plt.bar(["tfidf-cosine"], [build_time_ms], color="#b45309")
    plt.title("Index Build Time")
    plt.ylabel("Time (ms)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _plot_method_comparison(rows: list[dict[str, Any]], output_path: Path) -> None:
    labels = [f"{row['method']}-{index + 1}" for index, row in enumerate(rows)]
    scores = [float(row["top_score"]) for row in rows]
    plt.figure(figsize=(8, 4))
    plt.bar(labels, scores, color="#7c3aed")
    plt.title("Retrieval Method Comparison")
    plt.xlabel("Query sample")
    plt.ylabel("Top-1 score")
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def _repo_link(path: Path) -> str:
    normalized = path.as_posix()
    lowered = normalized.lower()
    repo_prefix = "d:/chap2_e-commerce/"
    if lowered.startswith(repo_prefix):
        normalized = normalized[len("D:/CHAP2_E-COMMERCE/") :]
        return f"/d:/CHAP2_E-COMMERCE/{normalized}"
    return normalized


def _build_phase5_report(
    sample_query: str,
    sample_results: list[RagRetrievedProduct],
    metadata: dict[str, Any],
    summary_path: Path,
    latency_plot: Path,
    score_plot: Path,
    build_time_plot: Path,
    comparison_plot: Path,
) -> str:
    result_lines = "\n".join(
        f"- `{item.name}` (`{item.category}` / `{item.detail_type}`) score `{item.score}` via terms `{', '.join(item.matched_terms) or 'n/a'}`"
        for item in sample_results
    ) or "- No products matched the sample query."
    return (
        "# Phase 5 RAG Report\n\n"
        "## Document construction\n\n"
        "- Product documents are rebuilt from the Phase 3 corpus format: name, category, detail type, price, and flattened detail fields.\n"
        "- Each document maps directly to a real product so later chatbot and hybrid recommendation phases can return grounded product payloads.\n\n"
        "## Retrieval method\n\n"
        f"- Active method: `{metadata['method']}`\n"
        "- The implementation uses local TF-IDF plus cosine similarity as a deterministic fallback vector search path.\n"
        "- Runtime artifacts are stored in `ai-service/artifacts/rag/` and can be loaded without rebuilding during normal inference.\n\n"
        "## Example query\n\n"
        f"- Sample query: `{sample_query}`\n"
        f"{result_lines}\n\n"
        "## Performance summary\n\n"
        f"- Document count: `{metadata['document_count']}`\n"
        f"- Index build time: `{metadata['build_time_ms']} ms`\n"
        f"- Average retrieval latency: `{metadata['average_latency_ms']} ms`\n\n"
        "## Evidence\n\n"
        f"- Summary JSON: [{summary_path.name}]({_repo_link(summary_path)})\n"
        f"- Retrieval latency plot: [{latency_plot.name}]({_repo_link(latency_plot)})\n"
        f"- Top-k score distribution: [{score_plot.name}]({_repo_link(score_plot)})\n"
        f"- Build-time plot: [{build_time_plot.name}]({_repo_link(build_time_plot)})\n"
        f"- Method comparison plot: [{comparison_plot.name}]({_repo_link(comparison_plot)})\n\n"
        "## Strengths and limitations\n\n"
        "- Retrieval is grounded on the real product catalog and produces ranked products with match evidence.\n"
        "- The current fallback is lexical-semantic rather than dense embeddings, so synonym handling is still limited.\n"
        "- If `faiss` is introduced later, the same document mapping can be reused with a denser vector representation.\n"
    )
