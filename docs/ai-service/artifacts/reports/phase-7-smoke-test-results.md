# Phase 7 Smoke Test Results

## Commands run

```bash
docker compose up -d --build ai-service
docker compose exec ai-service python scripts/export_phase7_recommendations.py
curl.exe "http://localhost:8007/recommend?user_id=1&query=budget%20laptop&limit=5"
curl.exe "http://localhost:8007/recommend?user_id=999&query=gift%20fashion&limit=5"
```

## Results

| Check | Status | Notes |
| --- | --- | --- |
| Service rebuild | Pass | `ai-service` rebuilt with Phase 7 code and `torch` dependency |
| Hybrid endpoint | Pass | `/recommend` returned grounded products, scores, reasons, and `sources_used` |
| Cold-start fallback | Pass | Request for `user_id=999` returned graph + RAG + popularity blended output |
| Artifact export | Pass | Summary JSON, sample CSV, 6 PNG plots, and `phase-7-hybrid-recommendation-report.md` created |

## Sample observations

- `GET /recommend?user_id=1&query=budget laptop` returned `Laptop Pro 14` as the top result with blended `lstm`, `rag`, and `popularity` signals.
- `GET /recommend?user_id=999&query=gift fashion` returned `Classic Hoodie` with a visible `rag` contribution plus fallback support from graph/popularity.

## Notes

- The endpoint excludes products the user has already interacted with when there is user history.
- Runtime verification was executed inside the Docker Compose stack because the host shell environment did not have the required Python dependencies installed.
