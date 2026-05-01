# Phase 6 LSTM Evaluation

## Dataset used for training

- Behavior events merged from Phase 3 actual + synthetic datasets: `193`
- Sequence count after preprocessing: `24`
- Train/val/test sequence split: `16` / `4` / `4`
- Train/val/test sample split for best config: `84` / `17` / `23`
- Product classes in vocabulary: `12`

## Sequence construction

- Events are sorted by `user_id`, `timestamp`, and event id.
- `search` events are excluded because the LSTM predicts the next interacted product id.
- Sliding windows up to `5` items are used as input history for next-product prediction.

## LSTM architecture and training setup

- Best config: `seq5-emb32-h64`
- Embedding dim: `32`
- Hidden dim: `64`
- Max sequence length: `5`
- Epoch budget: `18` with early stopping patience `4`
- Learning rate: `0.003`
- Batch size: `16`

## Metrics

- Accuracy: `0.2174`
- Top-3 accuracy: `0.5217`
- Top-5 accuracy: `0.7391`
- Precision@5: `0.1478`
- Recall@5: `0.7391`
- HitRate@5: `0.7391`
- MRR: `0.379`
- NDCG@5: `0.467`
- Mean inference latency: `0.04 ms`

## Baseline vs LSTM

| Model | Accuracy | Top-3 accuracy | Top-5 accuracy | MRR | NDCG@5 |
| --- | --- | --- | --- | --- | --- |
| Random | 0.0435 | 0.1304 | 0.2174 | 0.1844 | 0.1263 |
| Popularity | 0.0 | 0.0 | 0.0435 | 0.1054 | 0.0187 |
| LSTM | 0.2174 | 0.5217 | 0.7391 | 0.379 | 0.467 |

## Hyperparameter comparison

| Experiment | Seq len | Embedding dim | Hidden dim | Top-3 accuracy | NDCG@5 |
| --- | --- | --- | --- | --- | --- |
| seq3-emb16-h32 | 3 | 16 | 32 | 0.4348 | 0.3733 |
| seq4-emb24-h48 | 4 | 24 | 48 | 0.4783 | 0.4564 |
| seq5-emb32-h64 | 5 | 32 | 64 | 0.5217 | 0.467 |

## Evidence

- `ai-service/artifacts/lstm/best_lstm_model.pt`
- `ai-service/artifacts/lstm/lstm_metadata.json`
- `docs/ai-service/plots/lstm/training_loss_curve.png`
- `docs/ai-service/plots/lstm/validation_loss_curve.png`
- `docs/ai-service/plots/lstm/train_val_loss_comparison.png`
- `docs/ai-service/plots/lstm/topk_accuracy_comparison.png`
- `docs/ai-service/plots/lstm/precision_recall_at_k.png`
- `docs/ai-service/plots/lstm/hit_rate_at_k.png`
- `docs/ai-service/plots/lstm/mrr_ndcg_comparison.png`
- `docs/ai-service/plots/lstm/confusion_matrix.png`
- `docs/ai-service/plots/lstm/hyperparameter_comparison.png`
- `docs/ai-service/plots/lstm/sequence_length_comparison.png`
- `docs/ai-service/plots/lstm/inference_latency.png`
- `docs/ai-service/plots/lstm/baseline_vs_lstm.png`

## Performance notes

- The best model improves ranking quality over the random baseline and remains competitive with the popularity fallback on this small dataset.
- Because the training data is still dominated by synthetic sessions and only a small live catalog, metrics should be read as pipeline validation rather than production-quality personalization.
- A fallback remains necessary when the user history is shorter than two product interactions or the model artifact is unavailable.
