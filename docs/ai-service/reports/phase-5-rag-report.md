# Phase 5 RAG Report

## Document construction

- Product documents are built from catalog fields: `name`, `category`, `detail_type`, `price`, and normalized detail attributes.
- Each retrieved result maps to a real `product_id`, so chatbot and recommendation responses remain grounded.

## Retrieval method

- Runtime method: `TF-IDF + cosine similarity` (deterministic local fallback when FAISS is not enabled).
- Index artifacts used at runtime:
  - `ai-service/artifacts/rag/tfidf_cosine_index.pkl`
  - `ai-service/artifacts/rag/tfidf_cosine_documents.json`
  - `ai-service/artifacts/rag/tfidf_cosine_metadata.json`

## Example retrieval

- Query: `laptop work`
- Top match: `Laptop Pro 14`
- Matching evidence is returned as keyword overlap in service response.

## Evidence

- `docs/ai-service/plots/rag/retrieval_latency.png`
- `docs/ai-service/plots/rag/topk_score_distribution.png`
- `docs/ai-service/plots/rag/index_build_time.png`
- `docs/ai-service/plots/rag/retrieval_method_comparison.png`

## Strengths and limitations

- Strong point: fast local retrieval, no external vector database dependency.
- Limitation: lexical retrieval still weaker on synonym/semantic drift than dense embedding search.
