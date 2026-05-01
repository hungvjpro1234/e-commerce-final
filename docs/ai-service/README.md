# AI Service Workspace

This directory stores Chapter 3 artifacts for AI-powered product recommendation and chatbot support.

## Structure

- `architecture/`: architecture and integration design notes
- `plots/`: key visualization evidence by phase
- `reports/`: phase reports and final summary
- `screenshots/`: UI evidence for recommendation/chatbot flows
- `artifacts/`: minimal reproducibility datasets and selected legacy phase outputs
- `ai-service-api.md`: API contract
- `ai-recommendation-pipeline.md`: end-to-end recommendation flow
- `ai-chatbot-rag.md`: chatbot + RAG design
- `ai-service-smoke-test.md`: final smoke checklist

## Current phase status

- Phase 0: complete
- Phase 1: complete
- Phase 2: complete
- Phase 3: complete
- Phase 4: complete
- Phase 5: complete

Current implementation now includes:

- runnable `ai-service` FastAPI container
- `GET /health`
- `POST /behavior`
- `GET /behavior/user/{user_id}`
- PostgreSQL-backed `behavior_events` schema
- Phase 2 behavior dataset export, tables, chart, and markdown reports
- Phase 3 live product snapshot and product document corpus
- Phase 3 cleaned behavior, synthetic behavior, sequence, split, and vocab artifacts
- Phase 3 PNG charts and dataset analysis reports
- Phase 4 Neo4j graph sync and graph recommendation APIs
- Phase 4 graph stats, tables, PNG charts, and Mermaid snapshot/report artifacts
- Phase 5 RAG rebuild API, runtime index files, retrieval plots, and markdown report

## Artifact policy

Phase 10 cleanup keeps only high-value evidence:

- runtime model/index artifacts in `ai-service/artifacts/`
- plots in `docs/ai-service/plots/`
- markdown reports in `docs/ai-service/reports/`
- screenshots in `docs/ai-service/screenshots/`

Intermediate inventory/manifests and table-style auxiliary artifacts were removed.
