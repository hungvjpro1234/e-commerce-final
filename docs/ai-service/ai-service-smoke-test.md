# AI Service Smoke Test Plan

## Current status

- Phase 1 to Phase 9 implementation is completed.
- Phase 10 keeps a lean smoke checklist focused on runtime behavior and demo-readiness.

## Final smoke checklist

| Area | Verification target |
| --- | --- |
| Health | `GET /health` returns `200` |
| Behavior | `POST /behavior` persists and `GET /behavior/user/{user_id}` returns event history |
| Graph | `POST /graph/sync` and `GET /graph/recommend` return graph-backed output |
| RAG | `POST /rag/rebuild-index` rebuilds runtime index artifacts |
| Recommendation | `GET /recommend` returns scored hybrid items and `reason` metadata |
| Chatbot | `POST /chatbot` returns grounded `answer` + `products` + `retrieved_context` |
| Frontend | `/api/ai/*` proxy drives recommendation block and chatbot page |

## Command matrix

| Area | Command pattern | Expected outcome |
| --- | --- | --- |
| AI health | `curl http://localhost:8007/health` | `200 OK` |
| Behavior write/read | `curl -X POST /behavior` then `curl /behavior/user/{id}` | persisted event history |
| Graph sync/recommend | `curl -X POST /graph/sync` and `curl /graph/recommend?user_id=...` | graph scores returned |
| RAG rebuild | `curl -X POST /rag/rebuild-index` | runtime index files refreshed |
| Hybrid recommend | `curl /recommend?user_id=...&query=...` | scored products with reasons |
| Chatbot | `curl -X POST /chatbot` | grounded answer with product suggestions |

## Final verification notes

- Runtime model artifacts: `ai-service/artifacts/lstm/best_lstm_model.pt`
- Runtime retrieval artifacts:
  - `ai-service/artifacts/rag/tfidf_cosine_index.pkl`
  - `ai-service/artifacts/rag/tfidf_cosine_documents.json`
  - `ai-service/artifacts/rag/tfidf_cosine_metadata.json`
