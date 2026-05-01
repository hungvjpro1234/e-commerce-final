# Phase 1 Smoke Test Results

## Scope

Phase 1 runtime verification for:

- `docker compose run --rm ai-service pytest`
- `docker compose up -d --no-deps ai-service`
- `GET /health`

## Executed commands

```powershell
docker compose run --rm ai-service pytest
docker compose up -d --no-deps ai-service
curl.exe http://localhost:8007/health
```

## Results

| Check | Result | Evidence |
| --- | --- | --- |
| Unit smoke test | Pass | `1 passed in 0.85s` |
| Container startup | Pass | `ai-service` reached `Up` state on port `8007` |
| Health endpoint | Pass | Returned `200` with JSON payload |

## Health response

```json
{
  "service": "ai-service",
  "status": "ok",
  "version": "phase-1",
  "dependencies": {
    "ai_db": "postgresql@ai-db:5432",
    "neo4j": "bolt://neo4j:7687",
    "product_service": "http://product-service:8001"
  }
}
```

## Notes

- `Invoke-WebRequest` on this Windows environment threw a PowerShell `NullReferenceException`, so host verification used `curl.exe` instead.
- Runtime verification was intentionally limited to `/health` to stay within Phase 1 scope.
