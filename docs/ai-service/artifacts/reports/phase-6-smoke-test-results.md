# Phase 6 Smoke Test Results

## Commands run

```bash
cd ai-service
$env:DOCS_ARTIFACTS_DIR='d:\CHAP2_E-COMMERCE\docs\ai-service\artifacts'
$env:ARTIFACTS_DIR='d:\CHAP2_E-COMMERCE\ai-service\artifacts'
$env:LSTM_DEFAULT_EPOCHS='10'
python scripts/train_lstm.py
```

## Results

| Check | Status | Notes |
| --- | --- | --- |
| LSTM training pipeline | Pass | 3 experiment configs evaluated and best config selected as `seq4-emb24-h48` |
| Runtime artifact export | Pass | `best_lstm_model.pt` and `lstm_metadata.json` created in `ai-service/artifacts/lstm/` |
| Evaluation summary | Pass | `phase-6-lstm-summary.json` exported with full metric payload |
| Visualization bundle | Pass | 12 required Phase 6 PNG plots created in `docs/ai-service/plots/lstm/` |
| Markdown report | Pass | `phase-6-lstm-evaluation.md` created with dataset, config, metrics, baselines, and evidence links |

## Key metrics

- Accuracy: `0.1739`
- Top-3 accuracy: `0.6522`
- Top-5 accuracy: `0.7391`
- MRR: `0.3964`
- NDCG@5: `0.4827`
- Mean inference latency: `0.0477 ms`

## Notes

- This verification used the persisted Phase 3 dataset artifacts and did not require a live `product-service` container.
- `pytest` still could not be executed in this shell because the active Python environment does not currently have the `pytest` module installed.
