# Phase 5 Smoke Test Results

## Commands run

```bash
cd ai-service
$env:DOCS_ARTIFACTS_DIR='d:\CHAP2_E-COMMERCE\docs\ai-service\artifacts'
$env:ARTIFACTS_DIR='d:\CHAP2_E-COMMERCE\ai-service\artifacts'
python scripts/rebuild_rag_index.py
```

```bash
python - <<'PY'
import sys
sys.path.append(r'd:\CHAP2_E-COMMERCE\ai-service')
from app.services.rag import retrieve_products
for item in retrieve_products('programming architecture book', top_k=3):
    print(item.model_dump_json())
PY
```

## Results

| Check | Status | Notes |
| --- | --- | --- |
| RAG index rebuild | Pass | `12` documents indexed with method `tfidf-cosine` |
| Retrieval sanity query | Pass | Top result was `Clean Architecture` with score `0.3555` |
| Runtime artifacts | Pass | `tfidf_cosine_index.pkl`, `tfidf_cosine_documents.json`, `tfidf_cosine_metadata.json` created |
| Documentation artifacts | Pass | `phase-5-rag-report.md` plus four Phase 5 PNG plots created |

## Notes

- This local verification used the persisted Phase 3 product snapshot/corpus fallback, so it did not require a live `product-service` container.
- `pytest` could not be executed in this shell because the active Python environment does not have the `pytest` module installed.
