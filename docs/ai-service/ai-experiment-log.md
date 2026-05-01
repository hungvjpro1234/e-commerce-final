# AI Experiment Log

## Phase 0 entries

| Date | Phase | Decision | Reason | Impact |
| --- | --- | --- | --- | --- |
| 2026-04-28 | 0 | Use `FastAPI` for `ai-service` | Explicitly required by master prompt and suitable for ML-oriented microservices | Defines service skeleton in Phase 1 |
| 2026-04-28 | 0 | Keep existing services unchanged except for minimal integration hooks | Current microservices already work and should not be destabilized | Low-risk integration path |
| 2026-04-28 | 0 | Use frontend proxy `/api/ai/*` | Matches existing gateway pattern | Simplifies frontend integration |
| 2026-04-28 | 0 | Prefer frontend-origin behavior events first | Lowest coupling and easiest rollout | Shapes Phase 2 |
| 2026-04-28 | 0 | Use `product-service` as authoritative product source | Catalog already normalized and AI-friendly | Shapes product sync and RAG |
| 2026-04-28 | 0 | Plan for `Neo4j` + local `FAISS` | Required by Chapter 3 target architecture | Shapes Compose and artifact design |
| 2026-04-28 | 0 | Synthetic behavior generation allowed but must be reproducible | Prompt requires truthful labeling and saved generator scripts | Shapes Phase 3 |

## Phase 2 entries

| Date | Phase | Decision | Reason | Impact |
| --- | --- | --- | --- | --- |
| 2026-04-28 | 2 | Use `SQLAlchemy` with PostgreSQL runtime and SQLite test mode | Keeps production aligned with Compose while allowing fast isolated API tests | Enables safe Phase 2 persistence rollout |
| 2026-04-28 | 2 | Auto-create `behavior_events` table at service startup | Phase 2 needs real persistence without introducing a full migration framework yet | Low-friction schema bootstrap |
| 2026-04-28 | 2 | Export Phase 2 behavior artifacts into `docs/ai-service/artifacts` | Evidence files must live with Chapter 3 documentation | Produces reusable dataset/report inputs for later phases |
| 2026-04-28 | 2 | Use deterministic sample behavior data instead of synthetic large-scale generation | Phase 2 only needs persistence verification and initial analysis | Defers heavy dataset generation to Phase 3 |

## Phase 3 entries

| Date | Phase | Decision | Reason | Impact |
| --- | --- | --- | --- | --- |
| 2026-04-28 | 3 | Treat `product-service` as the live source-of-truth for catalog snapshot sync | Product schema is already normalized and stable after the 10-type refactor | Aligns later graph and RAG work with the real catalog |
| 2026-04-28 | 3 | Generate a deterministic synthetic behavior dataset with a fixed seed | Actual behavior volume is still too small for later LSTM preparation | Provides reproducible training-like inputs without faking model work |
| 2026-04-28 | 3 | Export PNG charts in addition to CSV/JSON/Markdown | Updated prompt emphasizes stronger visual evidence artifacts | Improves report quality for Chapter 3 evidence |
| 2026-04-28 | 3 | Create sequence, split, and vocab artifacts early | These are prerequisite inputs for Phase 6 model training | Reduces rework in later ML phases |

## Phase 4 entries

| Date | Phase | Decision | Reason | Impact |
| --- | --- | --- | --- | --- |
| 2026-04-28 | 4 | Store only `User` and `Product` nodes plus interaction and `SIMILAR` edges | Matches the master prompt graph scope without adding premature graph complexity | Keeps graph schema focused and reviewable |
| 2026-04-28 | 4 | Rebuild the graph from source-of-truth data on each sync | Simpler and safer than incremental reconciliation at this project stage | Makes graph state deterministic and reproducible |
| 2026-04-28 | 4 | Use heuristic `SIMILAR` scoring from category, detail type, price, and keyword overlap | Prompt requires real graph similarity but not yet a learned metric | Produces explainable graph edges for recommendation demos |
| 2026-04-28 | 4 | Export a Mermaid graph snapshot plus PNG charts | Prompt asks for graph screenshot or snapshot plus visual evidence | Provides portable graph evidence in a headless environment |

## Open questions for later phases

| Topic | Current default |
| --- | --- |
| AI DB engine | Prefer PostgreSQL for JSON/time-series friendliness, unless Compose simplicity favors MySQL |
| Behavior event emission source of `buy` | Prefer frontend checkout success plus optional server-side verification |
| Search events | Add lightweight frontend search UI or capture future query input field |
| Embedding method for RAG | Start with deterministic local embedding/fallback design compatible with FAISS |
