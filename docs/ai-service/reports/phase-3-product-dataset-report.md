# Phase 3 Product Dataset Report

## Scope

- Synced product catalog from `product-service`.
- Prepared behavior data for both RAG and LSTM downstream phases.
- Generated synthetic behavior with deterministic seed for demo reproducibility.

## Deliverables kept for reproducibility

- `docs/ai-service/artifacts/datasets/phase-3-product-snapshot.json`
- `docs/ai-service/artifacts/datasets/phase-3-product-document-corpus.jsonl`
- `docs/ai-service/artifacts/datasets/phase-3-cleaned-behavior-dataset.csv`
- `docs/ai-service/artifacts/datasets/phase-3-synthetic-behavior-dataset.csv`
- `docs/ai-service/artifacts/datasets/phase-3-sequence-dataset.json`
- `docs/ai-service/artifacts/datasets/phase-3-train-val-test-split.json`

## Key notes

- Behavior events are normalized and sorted chronologically by user.
- Sequence dataset excludes `search` as prediction target and focuses on product interaction transitions.
- Synthetic sessions follow realistic flow `view -> click -> add_to_cart -> buy`.

## Evidence

- `docs/ai-service/artifacts/plots/phase-3-actual-vs-synthetic-events.png`
- `docs/ai-service/artifacts/plots/phase-3-category-distribution.png`
- `docs/ai-service/artifacts/plots/phase-3-detail-type-distribution.png`
- `docs/ai-service/artifacts/plots/phase-3-sequence-length-distribution.png`
- `docs/ai-service/artifacts/plots/phase-3-user-category-heatmap.png`
