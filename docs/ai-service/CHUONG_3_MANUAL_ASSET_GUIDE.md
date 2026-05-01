# Manual Asset Guide for Chapter 3 Report

## 1. Danh sach hinh can chen

- Hinh 3.1. Kien truc tong quan AI Service
  - File: `docs/ai-service/screenshots/behavior-tracking-demo.png`
  - Chen vao: muc `3.2`
  - Y nghia: minh hoa luong frontend -> ai-service va behavior tracking trong demo runtime.

- Screenshot 3.1. Behavior tracking demo
  - File: `docs/ai-service/screenshots/behavior-tracking-demo.png`
  - Chen vao: muc `3.3.1`
  - Y nghia: bang chung tich hop tracking event trong giao dien.

- Screenshot 3.2. Recommendation UI
  - File: `docs/ai-service/screenshots/recommendation-ui.png`
  - Chen vao: muc `3.8.1`
  - Y nghia: bang chung recommendation list da hien thi tren storefront.

- Screenshot 3.3. Chatbot UI
  - File: `docs/ai-service/screenshots/chatbot-ui.png`
  - Chen vao: muc `3.8.2`
  - Y nghia: bang chung chatbot page da tich hop va hien thi grounding context.

## 2. Danh sach bieu do can chen

### 2.1 Dataset / Graph (Phase 3-4)

- Bieu do 3.1: `docs/ai-service/artifacts/plots/phase-3-category-distribution.png` (muc `3.3.2`)
- Bieu do 3.2: `docs/ai-service/artifacts/plots/phase-3-detail-type-distribution.png` (muc `3.3.2`)
- Bieu do 3.3: `docs/ai-service/artifacts/plots/phase-3-sequence-length-distribution.png` (muc `3.3.2`)
- Bieu do 3.9: `docs/ai-service/artifacts/plots/phase-4-node-edge-counts.png` (muc `3.5.3`)
- Bieu do 3.10: `docs/ai-service/artifacts/plots/phase-4-relationship-distribution.png` (muc `3.5.3`)

### 2.2 LSTM (Phase 6)

- Bieu do 3.4: `docs/ai-service/plots/lstm/training_loss_curve.png`
- Bieu do 3.5: `docs/ai-service/plots/lstm/validation_loss_curve.png`
- Bieu do 3.6: `docs/ai-service/plots/lstm/topk_accuracy_comparison.png`
- Bieu do 3.7: `docs/ai-service/plots/lstm/precision_recall_at_k.png`
- Bieu do 3.8: `docs/ai-service/plots/lstm/baseline_vs_lstm.png`
- Goi y chen vao: muc `3.4.3`

### 2.3 RAG + Chatbot (Phase 5, 8)

- Bieu do 3.11: `docs/ai-service/plots/rag/retrieval_latency.png`
- Bieu do 3.12: `docs/ai-service/plots/rag/topk_score_distribution.png`
- Bieu do 3.13: `docs/ai-service/plots/rag/index_build_time.png`
- Them bieu do chatbot:
  - `docs/ai-service/plots/rag/chatbot_latency.png`
  - `docs/ai-service/plots/rag/query_type_distribution.png`
  - `docs/ai-service/plots/rag/chatbot_retrieval_score_distribution.png`
  - `docs/ai-service/plots/rag/chatbot_top_product_categories.png`
- Goi y chen vao: muc `3.6` va `3.8.2`

### 2.4 Hybrid recommendation (Phase 7)

- Bieu do 3.14: `docs/ai-service/plots/hybrid/source_score_comparison.png`
- Bieu do 3.15: `docs/ai-service/plots/hybrid/model_ablation_comparison.png`
- Bieu do 3.16: `docs/ai-service/plots/hybrid/baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid.png`
- Bieu do bo sung:
  - `docs/ai-service/plots/hybrid/final_score_distribution.png`
  - `docs/ai-service/plots/hybrid/recommendation_latency.png`
  - `docs/ai-service/plots/hybrid/top_recommended_products.png`
- Goi y chen vao: muc `3.7`

## 3. Danh sach screenshot UI can chen

- Recommendation UI: `docs/ai-service/screenshots/recommendation-ui.png`
- Chatbot UI: `docs/ai-service/screenshots/chatbot-ui.png`
- Behavior tracking demo: `docs/ai-service/screenshots/behavior-tracking-demo.png`

## 4. Cach lay hinh neu can regenerate / bo sung

### 4.1 Regenerate plot/runtime artifact

Chay trong root repo:

```bash
docker compose exec ai-service python scripts/build_phase3_datasets.py
docker compose exec ai-service python scripts/sync_graph.py
docker compose exec ai-service python scripts/rebuild_rag_index.py
docker compose exec ai-service python scripts/train_lstm.py
docker compose exec ai-service python scripts/export_phase7_recommendations.py
docker compose exec ai-service python scripts/export_phase8_chatbot.py
```

Luu y: mot so script co the tao lai artifact trung gian trong `docs/ai-service/artifacts/` (bao gom file da cleanup o Phase 10).

### 4.2 Lay screenshot frontend

1. Khoi dong stack:
```bash
docker compose up -d --build ai-service frontend
```
2. Mo:
   - `http://localhost:3000/` de chup recommendation block
   - `http://localhost:3000/chatbot` de chup chatbot page
3. Thuc hien mot so thao tac search/click de co behavior flow ro rang, sau do chup man hinh.

### 4.3 Lay minh hoa API bang curl/Postman

```bash
curl http://localhost:8007/health
curl -X POST http://localhost:8007/rag/rebuild-index
curl "http://localhost:8007/recommend?user_id=1&query=budget%20laptop&limit=5"
curl -X POST http://localhost:8007/chatbot -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"toi can laptop gia re\"}"
```

### 4.4 Evidence dang thieu hoac can bo sung thu cong

- Khong co file anh graph snapshot truc tiep trong `docs/ai-service/screenshots/`; hien chi co:
  - `docs/ai-service/artifacts/screenshots/phase-4-graph-snapshot.md` (Mermaid markdown)
- Neu can hinh Neo4j Browser de dua vao bao cao in, can mo Neo4j UI (`http://localhost:7474`) va chup thu cong.

- Nhom file summary `docs/ai-service/artifacts/eval/*.json` da duoc cleanup o Phase 10, do do bao cao chuong 3 hien uu tien report markdown + runtime artifacts + plots/screenshot con ton tai.
