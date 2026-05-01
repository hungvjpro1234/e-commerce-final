# Phase 2 Smoke Test Results

## Scope

Runtime verification for:

- `pytest` in `ai-service`
- `POST /behavior`
- `GET /behavior/user/{user_id}`
- sample seed and artifact export scripts

## Executed commands

```powershell
docker compose exec ai-service pytest
docker compose exec ai-service python scripts/seed_behavior_sample.py
docker compose exec ai-service python scripts/export_behavior_artifacts.py
Invoke-RestMethod -Method Post -Uri http://localhost:8007/behavior -ContentType 'application/json' -Body '{"user_id":4,"product_id":3,"action":"view","timestamp":"2026-04-28T12:45:00Z"}'
curl.exe http://localhost:8007/behavior/user/4
```

## Results

| Check | Result | Evidence |
| --- | --- | --- |
| Test suite | Pass | `4 passed in 1.36s` |
| Seed script | Pass | Sample dataset inserted with `12` events |
| Export script | Pass | Dataset, tables, report, and chart files generated |
| `POST /behavior` | Pass | Created event `id=13` |
| `GET /behavior/user/4` | Pass | Returned `total=1` with the created event |

## Sample API outputs

### `POST /behavior`

```json
{
  "id": 13,
  "user_id": 4,
  "product_id": 3,
  "action": "view",
  "query_text": null,
  "timestamp": "2026-04-28T12:45:00Z"
}
```

### `GET /behavior/user/4`

```json
{
  "user_id": 4,
  "total": 1,
  "items": [
    {
      "id": 13,
      "user_id": 4,
      "product_id": 3,
      "action": "view",
      "query_text": null,
      "timestamp": "2026-04-28T12:45:00Z"
    }
  ]
}
```

## Notes

- The exported Phase 2 dataset/report artifacts were generated from the deterministic 12-event sample set before the separate runtime POST smoke event was added.
- No frontend behavior hooks were added in Phase 2 to avoid spilling into later integration phases.
