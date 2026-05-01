# Hướng dẫn chèn hình cho Chương 3

## 1. Danh sách hình/screenshot cần chèn

### 1.1. Nhóm screenshot giao diện

- **Hình 3.1. Minh họa luồng behavior tracking**
  - File: `docs/ai-service/screenshots/behavior-tracking-demo.png`
  - Chèn vào: mục `3.2` hoặc `3.3.1`
  - Ý nghĩa: chứng minh luồng tích hợp frontend -> AI service.

- **Hình 3.2. Recommendation UI**
  - File: `docs/ai-service/screenshots/recommendation-ui.png`
  - Chèn vào: mục `3.8.1`
  - Ý nghĩa: chứng minh block “Gợi ý cho bạn” hiển thị từ API hybrid.

- **Hình 3.3. Chatbot UI**
  - File: `docs/ai-service/screenshots/chatbot-ui.png`
  - Chèn vào: mục `3.8.2`
  - Ý nghĩa: chứng minh giao diện chatbot và kết quả tư vấn grounded.

### 1.2. Nhóm screenshot truy vấn Neo4j (đã chạy thực tế)

- **Hình 3.4. Kết quả query thống kê node theo label**
  - File: `docs/ai-service/screenshots/neo4j/query-01-node-counts.png`
  - Chèn vào: mục `3.5.3` (phần truy vấn thực thi trực tiếp)
  - Ý nghĩa: cho thấy số lượng node `Product` và `User`.

- **Hình 3.5. Kết quả query thống kê relationship theo type**
  - File: `docs/ai-service/screenshots/neo4j/query-02-relationship-counts.png`
  - Chèn vào: mục `3.5.3`
  - Ý nghĩa: xác nhận các quan hệ `VIEW`, `CLICK`, `ADD_TO_CART`, `BUY`, `SIMILAR`.

- **Hình 3.6. Kết quả query top sản phẩm có nhiều tương tác**
  - File: `docs/ai-service/screenshots/neo4j/query-03-top-products-by-interactions.png`
  - Chèn vào: mục `3.5.3`
  - Ý nghĩa: minh họa tín hiệu phổ biến trên đồ thị.

- **Hình 3.7. Kết quả query cạnh SIMILAR**
  - File: `docs/ai-service/screenshots/neo4j/query-04-similar-edges.png`
  - Chèn vào: mục `3.5.3`
  - Ý nghĩa: chứng minh cơ chế similarity đã được ghi vào graph.

- **Hình 3.8. Kết quả query dấu vết tương tác user**
  - File: `docs/ai-service/screenshots/neo4j/query-05-user-interaction-trace.png`
  - Chèn vào: mục `3.5.3`
  - Ý nghĩa: thể hiện ví dụ user-centric view phục vụ recommendation.

- **Hình 3.9. Kết quả query dạng mạng node-edge (graph view)**
  - File: `docs/ai-service/screenshots/neo4j/query-06-user-product-graph-network.png`
  - Chèn vào: mục `3.5.3`
  - Ý nghĩa: minh họa trực tiếp network graph giữa node `User` và `Product` với các cạnh tương tác.

- **Hình 3.10. Kết quả query toàn mạng (nhiều node/edge liên kết chằng chịt)**
  - File: `docs/ai-service/screenshots/neo4j/query-07-full-network-graph.png`
  - Chèn vào: mục `3.5.3`
  - Ý nghĩa: minh họa snapshot gần toàn bộ graph với mức độ liên kết dày hơn để phục vụ trình bày trực quan.

- **Hình 3.11. Kết quả query mạng dày nhất theo toàn bộ loại quan hệ**
  - File: `docs/ai-service/screenshots/neo4j/query-08-dense-network-all-relationships.png`
  - Chèn vào: mục `3.5.3`
  - Ý nghĩa: ảnh graph dense dùng toàn bộ edge type hiện có (`VIEW`, `CLICK`, `ADD_TO_CART`, `BUY`, `SIMILAR`) để thể hiện rõ tính liên kết mạng.

## 2. Danh sách biểu đồ cần chèn

### 2.1. Biểu đồ dữ liệu (Phase 3)

- `docs/ai-service/artifacts/plots/phase-3-category-distribution.png`
- `docs/ai-service/artifacts/plots/phase-3-detail-type-distribution.png`
- `docs/ai-service/artifacts/plots/phase-3-sequence-length-distribution.png`

**Vị trí đề xuất:** mục `3.3.2`.

### 2.2. Biểu đồ LSTM (Phase 6)

- `docs/ai-service/plots/lstm/training_loss_curve.png`
- `docs/ai-service/plots/lstm/validation_loss_curve.png`
- `docs/ai-service/plots/lstm/topk_accuracy_comparison.png`
- `docs/ai-service/plots/lstm/precision_recall_at_k.png`
- `docs/ai-service/plots/lstm/baseline_vs_lstm.png`

**Vị trí đề xuất:** mục `3.4.3`.

### 2.3. Biểu đồ Graph (Phase 4)

- `docs/ai-service/artifacts/plots/phase-4-node-edge-counts.png`
- `docs/ai-service/artifacts/plots/phase-4-relationship-distribution.png`

**Vị trí đề xuất:** mục `3.5.3`.

### 2.4. Biểu đồ RAG (Phase 5, 8)

- `docs/ai-service/plots/rag/retrieval_latency.png`
- `docs/ai-service/plots/rag/topk_score_distribution.png`
- `docs/ai-service/plots/rag/index_build_time.png`
- `docs/ai-service/plots/rag/chatbot_latency.png`
- `docs/ai-service/plots/rag/query_type_distribution.png`
- `docs/ai-service/plots/rag/chatbot_retrieval_score_distribution.png`
- `docs/ai-service/plots/rag/chatbot_top_product_categories.png`

**Vị trí đề xuất:** mục `3.6` và `3.8.2`.

### 2.5. Biểu đồ Hybrid (Phase 7)

- `docs/ai-service/plots/hybrid/source_score_comparison.png`
- `docs/ai-service/plots/hybrid/model_ablation_comparison.png`
- `docs/ai-service/plots/hybrid/baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid.png`
- `docs/ai-service/plots/hybrid/final_score_distribution.png`
- `docs/ai-service/plots/hybrid/recommendation_latency.png`
- `docs/ai-service/plots/hybrid/top_recommended_products.png`

**Vị trí đề xuất:** mục `3.7`.

## 3. Mục cần chụp thủ công (nếu muốn tăng tính trực quan)

- **Ảnh trực tiếp từ Neo4j Browser** hiện **chưa có file PNG** trong repo.
  - File hiện có chỉ là markdown snapshot: `docs/ai-service/artifacts/screenshots/phase-4-graph-snapshot.md`
  - Nếu cần ảnh đẹp để chèn báo cáo Word, nên mở Neo4j Browser và chụp thủ công.

## 4. Lệnh tái tạo hình/biểu đồ khi cần

Chạy ở thư mục gốc repo:

```bash
docker compose exec ai-service python scripts/build_phase3_datasets.py
docker compose exec ai-service python scripts/sync_graph.py
docker compose exec ai-service python scripts/rebuild_rag_index.py
docker compose exec ai-service python scripts/train_lstm.py
docker compose exec ai-service python scripts/export_phase7_recommendations.py
docker compose exec ai-service python scripts/export_phase8_chatbot.py
```

Lưu ý:
- Một số script có thể tạo lại artifact trung gian trong `docs/ai-service/artifacts/`.
- Nếu chỉ cần hình cho báo cáo, nên sao lưu trạng thái docs trước khi regenerate hàng loạt.

## 5. Cách lấy screenshot frontend/API minh họa

### 5.1. Frontend

1. Khởi động dịch vụ:
```bash
docker compose up -d --build ai-service frontend
```
2. Mở trình duyệt:
   - `http://localhost:3000/` (chụp recommendation UI)
   - `http://localhost:3000/chatbot` (chụp chatbot UI)
3. Thao tác thêm search/click để có màn hình behavior rõ ràng.

### 5.2. API

```bash
curl http://localhost:8007/health
curl -X POST http://localhost:8007/rag/rebuild-index
curl "http://localhost:8007/recommend?user_id=1&query=budget%20laptop&limit=5"
curl -X POST http://localhost:8007/chatbot -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"tôi cần laptop giá rẻ\"}"
```

Kết quả các lệnh này có thể dùng làm hình phụ lục (ảnh terminal) hoặc bảng minh họa response.
