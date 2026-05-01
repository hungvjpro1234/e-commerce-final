# AI Service Phase Plan

## Delivery roadmap

| Phase | Goal | Main outputs | Code mutation level |
| --- | --- | --- | --- |
| 0 | Audit and design | Docs, tables, design diagrams, artifact structure | Low |
| 1 | AI service skeleton | `ai-service` FastAPI app, Dockerfile, `/health` | Medium |
| 2 | Behavior tracking | DB schema, behavior APIs, minimal frontend hooks | Medium |
| 3 | Product sync and dataset prep | product client, corpus build, synthetic data scripts | Medium |
| 4 | Knowledge graph | Neo4j, graph sync, graph recommendation | High |
| 5 | RAG and vector search | FAISS index, retrieval services, rebuild tooling | High |
| 6 | LSTM model | preprocessing, training, evaluation, model artifact | High |
| 7 | Hybrid recommendation API | `/recommend`, scoring fusion, benchmarks | High |
| 8 | Chatbot | `/chatbot`, retrieve-and-generate MVP | Medium |
| 9 | Frontend integration | recommendation block, chatbot UI, behavior UX | Medium |
| 10 | Final polish | docs, smoke tests, benchmark summary, final evidence | Medium |

## Recommended execution order rationale

1. Build `ai-service` skeleton first to establish deployment boundaries.
2. Capture and persist behavior before training or graph work.
3. Sync product data before graph and RAG, because both depend on a stable catalog snapshot.
4. Implement graph and RAG before LSTM inference integration, so hybrid recommendation has fallback sources.
5. Train LSTM only after behavior/dataset pipelines exist.
6. Expose recommendation and chatbot APIs before frontend UI integration.
7. Finish with documentation and evidence hardening.

## Phase gating

Each later phase depends on the prior artifacts:

- Phase 1 depends on Phase 0 docs and folder structure.
- Phase 2 depends on Phase 1 service runtime.
- Phase 3 depends on Phase 2 event storage.
- Phase 4 and 5 depend on Phase 3 catalog sync outputs.
- Phase 6 depends on Phase 3 datasets.
- Phase 7 depends on Phase 4, 5, and 6 scoring services.
- Phase 8 depends on Phase 5 retrieval and Phase 7 recommendation support.
- Phase 9 depends on stable APIs from Phases 2, 7, and 8.
- Phase 10 depends on all previous phases.
