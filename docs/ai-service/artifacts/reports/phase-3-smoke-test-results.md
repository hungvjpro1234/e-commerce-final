# Phase 3 Smoke Test Results

## Scope

Runtime verification for:

- product catalog sync from `product-service`
- synthetic behavior generation
- full Phase 3 dataset build
- updated ai-service test suite

## Executed commands

```powershell
docker compose exec ai-service pytest
docker compose exec ai-service python scripts/sync_product_catalog.py
docker compose exec ai-service python scripts/generate_synthetic_behavior.py
docker compose exec ai-service python scripts/build_phase3_datasets.py
```

## Results

| Check | Result | Evidence |
| --- | --- | --- |
| Test suite | Pass | `6 passed` |
| Product sync smoke | Pass | Live catalog fetch returned `12` products |
| Synthetic generation smoke | Pass | Deterministic generator returned `180` events |
| Phase 3 build pipeline | Pass | Snapshot, corpus, datasets, tables, reports, and PNG charts generated |

## Key outputs

| Artifact | Result |
| --- | --- |
| Product snapshot | `12` products |
| Product document corpus | `12` documents |
| Cleaned actual behavior dataset | `13` events |
| Synthetic behavior dataset | `180` events |
| Sequence dataset | `25` sequences |
| Train/val/test split | `17 / 4 / 4` |

## Notes

- The product snapshot was fetched from the live `product-service` API rather than a hard-coded fixture.
- The synthetic dataset uses a fixed `SYNTHETIC_BEHAVIOR_SEED`, so reruns are reproducible unless the catalog itself changes.
