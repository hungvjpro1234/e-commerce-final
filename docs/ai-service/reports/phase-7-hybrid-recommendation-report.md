# Phase 7 Hybrid Recommendation Report

## Scoring formula

- Base weights: `lstm=0.4`, `graph=0.3`, `rag=0.3`, `popularity=0.2`.
- For each request, only available sources are kept and the weights are normalized back to sum to `1.0`.
- Popularity participates as a fallback source when the richer signals are absent or sparse.

## Fallback logic

- Short history or missing model artifact: fallback from LSTM to popularity.
- Missing query: RAG is skipped and its weight is redistributed.
- Graph connection/runtime failure: graph source is dropped and the response still returns hybrid results from the remaining sources.

## Sample summary

- Sample request count: `4`
- Hybrid items exported: `19`
- Average latency: `57.6404 ms`

## Request / response examples

- See the exported sample table for grounded responses across query and cold-start cases.

## Why hybrid is stronger than a single source

- LSTM captures next-item sequence preference from interaction order.
- Graph captures structural similarity and neighbor traversal from the Neo4j layer.
- RAG captures explicit natural-language intent when a query is provided.
- Popularity keeps the endpoint usable under sparse or degraded conditions.

## Evidence

- `docs/ai-service/plots/hybrid/source_score_comparison.png`
- `docs/ai-service/plots/hybrid/final_score_distribution.png`
- `docs/ai-service/plots/hybrid/model_ablation_comparison.png`
- `docs/ai-service/plots/hybrid/baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid.png`
- `docs/ai-service/plots/hybrid/recommendation_latency.png`
- `docs/ai-service/plots/hybrid/top_recommended_products.png`
