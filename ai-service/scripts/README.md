# Scripts

Phase 1 keeps this directory as a placeholder for later operational scripts such as:

- behavior export
- product sync
- graph sync
- vector index rebuild
- training and evaluation helpers
## Available scripts

- `seed_behavior_sample.py`: inserts deterministic Phase 2 sample behavior events when the table is empty.
- `export_behavior_artifacts.py`: exports Phase 2 dataset snapshots, summary tables, and markdown chart/report files.
- `sync_product_catalog.py`: fetches the live catalog from `product-service`.
- `generate_synthetic_behavior.py`: produces deterministic synthetic behavior records from the current catalog.
- `build_phase3_datasets.py`: generates Phase 3 snapshot, corpus, cleaned behavior, synthetic behavior, sequence, split, chart, and report artifacts.
- `sync_graph.py`: syncs products and behavior events into Neo4j and builds `SIMILAR` edges.
- `export_graph_artifacts.py`: rebuilds the graph and exports Phase 4 graph stats, tables, plots, and snapshot/report files.
- `rebuild_rag_index.py`: rebuilds the Phase 5 TF-IDF RAG index, runtime metadata, plots, and markdown report artifacts.
- `train_lstm.py`: trains the Phase 6 PyTorch LSTM, exports the best model artifact, metrics summary, plots, and evaluation report.
- `export_phase7_recommendations.py`: runs sample hybrid recommendation requests and exports the Phase 7 summary, plots, sample table, and markdown report.
- `export_phase8_chatbot.py`: runs sample chatbot case studies and exports the Phase 8 summary, plots, case-study table, and markdown report.
