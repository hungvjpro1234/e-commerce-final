# AI Service API

## Endpoints

| Phase | Endpoint | Purpose | Current status |
| --- | --- | --- | --- |
| 1 | `GET /health` | service health check | Implemented |
| 2 | `POST /behavior` | ingest behavior event | Implemented |
| 2 | `GET /behavior/user/{user_id}` | user behavior history | Implemented |
| 4 | `POST /graph/sync` | sync graph data | Implemented |
| 4 | `GET /graph/recommend?user_id=...` | graph recommendation | Implemented |
| 5 | `POST /rag/rebuild-index` | rebuild vector index | Implemented |
| 7 | `GET /recommend?user_id=...&query=...` | hybrid recommendation | Implemented |
| 8 | `POST /chatbot` | product advisory chatbot | Implemented |

## Request/response schemas

### `POST /behavior`

Request:

```json
{
  "user_id": 1,
  "product_id": 10,
  "action": "view",
  "query_text": null,
  "timestamp": "2026-04-28T12:30:00Z"
}
```

Rules:

- `product_id` nullable for `search`
- `query_text` nullable except for search events when available
- `action` in `view`, `click`, `search`, `add_to_cart`, `buy`

Response:

```json
{
  "id": 1,
  "user_id": 1,
  "product_id": 10,
  "action": "view",
  "query_text": null,
  "timestamp": "2026-04-28T12:30:00Z"
}
```

### `GET /behavior/user/{user_id}`

Response:

```json
{
  "user_id": 1,
  "total": 2,
  "items": [
    {
      "id": 1,
      "user_id": 1,
      "product_id": null,
      "action": "search",
      "query_text": "wireless headphones",
      "timestamp": "2026-04-28T10:00:00Z"
    },
    {
      "id": 2,
      "user_id": 1,
      "product_id": 2,
      "action": "view",
      "query_text": null,
      "timestamp": "2026-04-28T10:01:00Z"
    }
  ]
}
```

### `GET /recommend`

Response:

```json
{
  "user_id": 1,
  "query": "budget laptop",
  "total": 5,
  "items": [
    {
      "id": 2,
      "name": "Laptop Pro 14",
      "price": 1299.0,
      "category": "Electronics",
      "detail_type": "electronics",
      "score": 0.3852,
      "reason": "Recommended from popularity + rag. RAG match for query with terms: laptop; Popularity fallback from aggregate interaction counts.",
      "source_scores": {
        "rag": 1.0,
        "popularity": 0.8113
      }
    }
  ],
  "sources_used": ["graph", "lstm", "popularity", "rag"]
}
```

### `POST /rag/rebuild-index`

Response:

```json
{
  "message": "RAG index rebuilt successfully.",
  "method": "tfidf-cosine",
  "document_count": 12,
  "artifact_paths": {
    "phase5_report": "docs/ai-service/reports/phase-5-rag-report.md",
    "runtime_matrix": "ai-service/artifacts/rag/tfidf_cosine_index.pkl",
    "runtime_documents": "ai-service/artifacts/rag/tfidf_cosine_documents.json",
    "runtime_metadata": "ai-service/artifacts/rag/tfidf_cosine_metadata.json"
  }
}
```

### `POST /graph/sync`

Response:

```json
{
  "product_count": 12,
  "user_count": 4,
  "interaction_edge_count": 11,
  "similar_edge_count": 2,
  "message": "Graph sync completed."
}
```

### `GET /graph/recommend?user_id=1&limit=3`

Response:

```json
{
  "user_id": 1,
  "total": 1,
  "items": [
    {
      "id": 4,
      "name": "Clean Architecture",
      "price": 34.5,
      "category": "Books",
      "detail_type": "book",
      "score": 8.2782,
      "reason": "Sources: Django for APIs. Signals: same category; same detail_type; close price; keyword overlap: book, books."
    }
  ]
}
```

### `POST /chatbot`

Request:

```json
{
  "user_id": 1,
  "message": "toi can laptop gia re"
}
```

Response:

```json
{
  "answer": "Voi nhu cau 'toi can laptop gia re', toi uu tien cac san pham co muc gia de tiep can hon va lien quan truc tiep den truy van. Goi y dau tien la Laptop Pro 14 gia 1299.0, va toi kem them 2 lua chon de ban so sanh.",
  "products": [
    {
      "id": 2,
      "name": "Laptop Pro 14",
      "price": 1299.0,
      "category": "Electronics",
      "detail_type": "electronics",
      "score": 0.75,
      "reason": "Grounded RAG match via terms: laptop."
    }
  ],
  "retrieved_context": [
    "Laptop Pro 14 | Electronics | electronics | price=1299.0 | matched_terms=laptop"
  ],
  "query_type": "budget"
}
```

## Frontend proxy impact

`frontend/app/api/[...path]/route.ts` will need one new prefix:

| Prefix | Target env var |
| --- | --- |
| `ai` | `AI_SERVICE_URL` |

This remains the preferred integration point because it preserves the existing API-gateway pattern in Next.js.
