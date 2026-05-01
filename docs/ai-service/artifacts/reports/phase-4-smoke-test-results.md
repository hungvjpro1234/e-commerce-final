# Phase 4 Smoke Test Results

## Scope

Runtime verification for:

- Neo4j graph sync
- graph recommendation API
- graph artifact export
- updated ai-service test suite

## Executed commands

```powershell
docker compose exec ai-service pytest
docker compose exec ai-service python scripts/sync_graph.py
curl.exe "http://localhost:8007/graph/recommend?user_id=1&limit=3"
docker compose exec ai-service python scripts/export_graph_artifacts.py
```

## Results

| Check | Result | Evidence |
| --- | --- | --- |
| Test suite | Pass | `8 passed` |
| Graph sync | Pass | `4` users, `12` products, `11` interaction edges, `2` similar edges |
| Graph recommendation | Pass | `user_id=1` received `Clean Architecture` recommendation |
| Graph artifact export | Pass | Summary JSON, CSV tables, PNG charts, Mermaid snapshot, and report generated |

## Sample graph recommendation

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
