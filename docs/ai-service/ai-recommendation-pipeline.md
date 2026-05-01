# AI Recommendation Pipeline

## Pipeline overview

```mermaid
flowchart TD
    A[Frontend behavior events] --> B[ai-service behavior ingestion]
    B --> C[(ai-db behavior table)]
    C --> D[Dataset preparation]
    D --> E[LSTM sequence dataset]
    D --> F[Graph sync dataset]
    D --> G[RAG product document corpus]

    E --> H[LSTM training and inference]
    F --> I[Neo4j recommendation query]
    G --> J[FAISS retrieval]

    H --> K[Hybrid scoring]
    I --> K
    J --> K
    L[Popularity baseline] --> K
    K --> M[/recommend response]
```

## Data sources

| Source | Fields used | Downstream use |
| --- | --- | --- |
| Behavior events | `user_id`, `product_id`, `action`, `query_text`, `timestamp` | LSTM sequences, graph edges, analytics |
| Product catalog | `id`, `name`, `price`, `category_data`, `detail_type`, `detail` | product documents, graph nodes, feature engineering |
| Order completion | `user_id`, `product_id`, buy event semantics | stronger recommendation weight |

## Phase 3 data foundation

Phase 3 output used by runtime and reproducibility:

- `docs/ai-service/artifacts/datasets/phase-3-product-snapshot.json`
- `docs/ai-service/artifacts/datasets/phase-3-product-document-corpus.jsonl`
- `docs/ai-service/artifacts/datasets/phase-3-cleaned-behavior-dataset.csv`
- `docs/ai-service/artifacts/datasets/phase-3-synthetic-behavior-dataset.csv`
- `docs/ai-service/artifacts/datasets/phase-3-sequence-dataset.json`
- `docs/ai-service/artifacts/datasets/phase-3-train-val-test-split.json`
- `docs/ai-service/reports/phase-3-product-dataset-report.md`

## Phase 4 graph outputs

- `docs/ai-service/reports/phase-4-graph-report.md`
- `docs/ai-service/artifacts/plots/phase-4-node-edge-counts.png`
- `docs/ai-service/artifacts/plots/phase-4-degree-distribution.png`
- `docs/ai-service/artifacts/plots/phase-4-relationship-distribution.png`

## Hybrid scoring design

Phase 7 target scoring formula:

```text
final_score = 0.4 * lstm_score + 0.3 * graph_score + 0.3 * rag_score
```

If a component is unavailable:

- remove that component from the weighted mix
- re-normalize remaining weights
- preserve `reason` metadata in the response

## Cold-start handling

| Scenario | Primary fallback |
| --- | --- |
| New user, no behavior | RAG + popularity |
| Sparse user history | graph + popularity |
| LSTM model unavailable | graph + RAG + popularity |
| Query-driven recommendation | RAG first, then graph/category refinement |

## Required artifact outputs by later phase

### Dataset artifacts

- behavior raw export
- cleaned behavior dataset
- sequence dataset
- train/val/test splits
- product corpus

### Evaluation artifacts

- precision@k
- recall@k
- hit rate@k
- MRR
- NDCG@k
- baseline vs hybrid comparison

### Benchmark artifacts

- endpoint latency tables
- warm vs cold inference comparison
- source contribution ablation tables
