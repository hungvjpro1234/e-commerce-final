# AI Service

AI service implementation for Chapter 3 is complete through Phase 10, including cleanup/documentation.

## Current scope

- FastAPI application
- `/health` endpoint
- `POST /behavior`
- `GET /behavior/user/{user_id}`
- containerized runtime
- Docker Compose integration
- PostgreSQL-backed behavior event storage
- artifact export scripts for behavior analysis
- live product catalog sync from `product-service`
- product document corpus generation
- cleaned and synthetic dataset generation for downstream ML phases
- Neo4j graph sync for users products interactions and similarity edges
- graph recommendation and graph analysis artifact export
- RAG index rebuild with TF-IDF cosine retrieval and runtime artifact persistence
- PyTorch LSTM next-product training, evaluation, and runtime model loading
- Hybrid recommendation endpoint with source-score fusion and fallback normalization
- Grounded chatbot endpoint with template generation over retrieved catalog products

## Structure

```text
ai-service/
|-- app/
|   |-- clients/
|   |-- graph/
|   |-- ml/
|   |-- rag/
|   |-- routers/
|   |-- schemas/
|   |-- services/
|   |-- utils/
|   |-- config.py
|   |-- db.py
|   `-- main.py
|-- artifacts/
|-- scripts/
|-- tests/
|-- .env.example
|-- Dockerfile
`-- requirements.txt
```

## Run with Docker Compose

From the monorepo root:

```bash
docker compose up -d --build ai-service ai-db neo4j
```

Health check:

```bash
curl http://localhost:8007/health
```

Seed sample behavior events:

```bash
docker compose exec ai-service python scripts/seed_behavior_sample.py
```

Export Phase 2 artifacts:

```bash
docker compose exec ai-service python scripts/export_behavior_artifacts.py
```

Build Phase 3 dataset artifacts:

```bash
docker compose exec ai-service python scripts/build_phase3_datasets.py
```

Build Phase 4 graph artifacts:

```bash
docker compose exec ai-service python scripts/export_graph_artifacts.py
```

Build Phase 5 RAG artifacts:

```bash
docker compose exec ai-service python scripts/rebuild_rag_index.py
curl.exe -X POST http://localhost:8007/rag/rebuild-index
```

Retrieve via service layer for sanity-checking:

```bash
python -c "import sys; sys.path.append('d:/CHAP2_E-COMMERCE/ai-service'); from app.services.rag import retrieve_products; print([item.model_dump() for item in retrieve_products('programming architecture book', top_k=2)])"
```

Build Phase 6 LSTM artifacts:

```bash
docker compose exec ai-service python scripts/train_lstm.py
```

Build Phase 7 hybrid recommendation artifacts:

```bash
docker compose exec ai-service python scripts/export_phase7_recommendations.py
curl.exe "http://localhost:8007/recommend?user_id=1&query=budget%20laptop&limit=5"
```

Build Phase 8 chatbot artifacts:

```bash
docker compose exec ai-service python scripts/export_phase8_chatbot.py
curl.exe -X POST "http://localhost:8007/chatbot" -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"toi can laptop gia re\"}"
```

## Phase status

Implemented through Phase 10:

- backend AI endpoints for behavior, graph, RAG, recommendation, and chatbot
- runtime LSTM and RAG artifacts
- frontend integration via `/api/ai/*` proxy (in `frontend`)
- final documentation and evidence cleanup
