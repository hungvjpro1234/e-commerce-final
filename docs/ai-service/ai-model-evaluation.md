# AI Model Evaluation Plan

## Scope

This document defines how Chapter 3 recommendation quality will be evaluated once Phase 6 and Phase 7 are implemented.

## Evaluation targets

| System | Metrics |
| --- | --- |
| Popularity baseline | precision@k, recall@k, hit rate@k |
| LSTM-only | precision@k, recall@k, hit rate@k, MRR, NDCG@k |
| Graph-only | precision@k, recall@k, hit rate@k |
| RAG-only | retrieval relevance examples, precision proxy |
| Hybrid | precision@k, recall@k, hit rate@k, MRR, NDCG@k, latency |

## Planned experiment outputs

- loss curves
- metric tables by `k`
- ablation comparisons
- latency tables
- best-hyperparameter table
- qualitative case studies

## Baseline comparison plan

| Variant | Description | Why included |
| --- | --- | --- |
| Popularity | most interacted products | minimum viable baseline |
| LSTM-only | sequence signal only | validates sequential modeling value |
| Graph-only | graph structure only | validates relational recommendation value |
| RAG-only | query similarity only | validates natural-language retrieval value |
| Hybrid | weighted blend | target production/demo strategy |

## Planned artifact outputs

- `artifacts/eval/*.csv`
- `artifacts/plots/*.png`
- `artifacts/tables/*.csv`
- markdown report updates with linked evidence

## Risks

- Seed-only datasets may overstate simple baselines.
- Synthetic data must be clearly labeled and reproducible.
- Evaluation splits must avoid leakage from repeated user-product sequences.
