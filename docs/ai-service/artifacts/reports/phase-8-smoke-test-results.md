# Phase 8 Smoke Test Results

## Commands run

```bash
docker compose up -d --build ai-service
docker compose exec ai-service python scripts/export_phase8_chatbot.py
curl.exe -X POST "http://localhost:8007/chatbot" -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"toi can laptop gia re\"}"
curl.exe -X POST "http://localhost:8007/chatbot" -H "Content-Type: application/json" -d "{\"user_id\":999,\"message\":\"san pham nao phu hop de lam qua\"}"
```

## Results

| Check | Status | Notes |
| --- | --- | --- |
| Chatbot endpoint | Pass | `/chatbot` returned grounded answer, products, retrieved context, and `query_type` |
| Budget laptop case | Pass | Returned real products grounded in RAG retrieval |
| Gift case | Pass | Returned product-backed answer with non-empty retrieved context |
| Artifact export | Pass | Summary JSON, case-study CSV, 4 PNG plots, and `phase-8-chatbot-report.md` created |

## Notes

- The chatbot uses real RAG retrieval and optional personalization boost from the existing recommendation pipeline.
- Generation is template-based on top of retrieved products, which keeps the response grounded without introducing an external LLM dependency.
