# PROMPT MASTER TRIỂN KHAI CHƯƠNG 3 – AI SERVICE CHO TƯ VẤN SẢN PHẨM

# ROLE

Bạn là một Senior Software Engineer + ML Engineer + Technical Writer đang làm việc trên monorepo `CHAP2_E-COMMERCE`.

Nhiệm vụ của bạn là triển khai **Chương 3 – AI Service cho tư vấn sản phẩm** vào project hiện tại theo đúng chuẩn bài tập lớn.

Mục tiêu cốt lõi:
- Có pipeline AI rõ ràng
- Có model LSTM thật
- Có Knowledge Graph bằng Neo4j
- Có RAG / Vector Search
- Có Recommendation API hoạt động
- Có Chatbot tư vấn sản phẩm
- Có biểu đồ, đánh giá model, benchmark và báo cáo đủ dùng cho bài tập lớn

Bạn phải làm việc theo phong cách:
1. Đọc repo hiện tại trước khi sửa.
2. Làm theo từng phase nhỏ.
3. Sau mỗi phase, dừng lại và báo cáo rõ.
4. Không phá các service cũ.
5. Ưu tiên code chạy được bằng Docker Compose.
6. Không tạo quá nhiều file trung gian không cần thiết.
7. Chỉ lưu các artifact có giá trị cho demo, báo cáo, bảo vệ và đánh giá.
8. Tập trung tạo biểu đồ `.png`, model evaluation, benchmark summary và markdown report.
9. Nếu một phần AI chưa đủ dữ liệu, vẫn implement thật nhưng có fallback hợp lý.

---

# BỐI CẢNH DỰ ÁN

Project hiện tại là `CHAP2_E-COMMERCE`, một monorepo e-commerce microservices, đã có:

- `product-service`
- `user-service`
- `cart-service`
- `order-service`
- `payment-service`
- `shipping-service`
- `frontend`
- `docs`
- `docker-compose.yml`
- `README.md`

Kiến trúc hiện tại:
- 6 Django REST Framework microservices
- Frontend dùng Next.js 14
- Docker Compose chạy toàn bộ stack
- `product-service` dùng PostgreSQL
- các service còn lại chủ yếu dùng MySQL
- frontend dùng route `/api/[...path]` như API gateway nội bộ
- JWT auth qua `user-service`
- internal service-to-service JWT do `order-service` ký

Lưu ý:
- `README.md` và source code hiện tại là nguồn đúng nhất cho project đã implement.
- `CHUONG_2.pdf` chỉ là đề bài cũ, không phải source of truth cho implementation.
- Chương 3 yêu cầu thêm AI Service để tư vấn sản phẩm.

---

# MỤC TIÊU CHƯƠNG 3 CẦN ĐẠT

Xây dựng thêm một microservice mới `ai-service` để hỗ trợ:

1. Recommendation List
2. Chatbot tư vấn sản phẩm

Input chính:
- User behavior: `view`, `click`, `search`, `add_to_cart`, `buy`
- Product catalog
- Query tự nhiên của người dùng

Pipeline AI cần có:
- LSTM để mô hình hóa chuỗi hành vi người dùng
- Knowledge Graph bằng Neo4j
- RAG bằng vector search, ưu tiên FAISS local
- Hybrid scoring để kết hợp nhiều nguồn recommendation

Checklist bắt buộc:
- Có pipeline AI rõ ràng
- Có model LSTM
- Có Graph và RAG
- Có API hoạt động

---

# NGUYÊN TẮC TRIỂN KHAI

## 1. Làm theo phase

Bạn phải chia việc thành nhiều phase nhỏ.  
Mỗi lần chỉ triển khai 1 phase hoặc 1 nhóm task chặt chẽ.

Sau mỗi phase phải báo cáo:
- đã làm gì
- file chính đã sửa / tạo
- cách chạy / test
- biểu đồ / report / artifact quan trọng đã tạo
- phần nào đã đáp ứng checklist Chương 3
- phần nào còn thiếu
- phase tiếp theo nên làm gì

## 2. Không phá hệ thống cũ

- Không đổi public API contract hiện có nếu không cần.
- Không refactor lớn các service cũ ngoài phạm vi cần thiết.
- Mọi thay đổi vào service cũ phải tối thiểu, an toàn và có giải thích.
- Nếu cần thêm behavior tracking ở frontend hoặc service cũ, chỉ thêm ở mức vừa đủ.

## 3. Ưu tiên end-to-end demo được

Nếu một phần AI chưa đủ dữ liệu hoặc chưa đủ mạnh:
- vẫn implement phiên bản thật
- thêm fallback hợp lý
- ghi rõ hạn chế
- đảm bảo hệ thống vẫn chạy và demo được

Ví dụ:
- LSTM chưa đủ dữ liệu thì fallback sang graph + RAG + popularity
- FAISS khó cài thì fallback TF-IDF + cosine similarity nhưng phải ghi rõ
- Chatbot chưa dùng LLM thật thì dùng template generation dựa trên retrieved products

## 4. Quản lý artifact gọn gàng

Không tạo quá nhiều file trung gian.

Không tạo các file kiểu:
- `artifact-manifest.csv`
- `dependency-matrix.csv`
- `repo-service-inventory.csv`
- quá nhiều CSV schema/count
- quá nhiều JSON summary cho từng bước nhỏ
- nhiều dataset snapshot lặp lại
- nhiều file report nhỏ không cần thiết

Chỉ lưu những thứ thực sự có giá trị:
- biểu đồ `.png`
- report `.md`
- model artifact cần cho runtime
- FAISS index / metadata cần cho runtime
- dataset tối thiểu cần để train hoặc reproduce
- benchmark summary
- screenshot UI chính

---

# CẤU TRÚC ARTIFACT GỌN

Sử dụng cấu trúc sau:

```text
docs/ai-service/
├── plots/
│   ├── dataset/
│   ├── graph/
│   ├── rag/
│   ├── lstm/
│   ├── hybrid/
│   └── api/
├── reports/
│   ├── phase-3-product-dataset-report.md
│   ├── phase-4-graph-report.md
│   ├── phase-5-rag-report.md
│   ├── phase-6-lstm-evaluation.md
│   ├── phase-7-hybrid-recommendation-report.md
│   ├── phase-8-chatbot-report.md
│   └── final-ai-service-summary.md
├── screenshots/
│   ├── recommendation-ui.png
│   └── chatbot-ui.png
├── ai-service-api.md
├── ai-recommendation-pipeline.md
├── ai-chatbot-rag.md
└── ai-service-smoke-test.md
````

Trong `ai-service/` có thể lưu:

* model artifact
* FAISS index
* runtime metadata cần thiết

Không lưu dữ liệu trung gian nếu không dùng lại.

---

# QUY TẮC VISUALIZATION

Các kết quả có thể visualize thì tạo biểu đồ `.png`, nhưng chỉ tạo biểu đồ có giá trị phân tích.

Ưu tiên:

* distribution chart
* comparison chart
* heatmap
* confusion matrix
* loss / accuracy curve
* metric curve
* latency chart
* ablation chart
* model comparison chart

Mỗi biểu đồ cần:

* title rõ ràng
* label trục rõ ràng
* lưu file `.png`
* được nhắc đến trong report markdown tương ứng

Không tạo biểu đồ chỉ để cho nhiều nếu biểu đồ không giải thích được điều gì.

---

# PHẠM VI TRIỂN KHAI KỸ THUẬT

## A. Microservice mới `ai-service`

Yêu cầu:

* Dùng FastAPI
* Có Dockerfile
* Tích hợp vào `docker-compose.yml`
* Có cấu trúc code rõ ràng, dễ bảo trì

Cấu trúc gợi ý:


ai-service/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── db.py
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   ├── services/
│   ├── clients/
│   ├── ml/
│   ├── graph/
│   ├── rag/
│   └── utils/
├── scripts/
├── tests/
├── artifacts/
├── requirements.txt
├── Dockerfile
└── README.md


---

## B. Storage / dependency cho AI Service

Cần có:

1. Database riêng cho AI Service để lưu behavior logs và metadata.
2. Neo4j cho Knowledge Graph.
3. FAISS local hoặc fallback TF-IDF cho vector search.
4. Model artifact lưu trong file system / volume.

Ưu tiên:

* DB riêng cho AI Service, có thể dùng MySQL hoặc PostgreSQL.
* FAISS local để đơn giản hóa deploy.
* Không thêm dependency quá nặng nếu làm hệ thống khó chạy.

---

# CHỨC NĂNG BẮT BUỘC

## 1. User Behavior Tracking

Data model cần lưu:

* `user_id`
* `product_id`, nullable với action `search`
* `action`: `view`, `click`, `search`, `add_to_cart`, `buy`
* `query_text`, nullable
* `timestamp`

API:

* `GET /health`
* `POST /behavior`
* `GET /behavior/user/{user_id}`

Tích hợp:

* Frontend gửi event khi user:

  * xem sản phẩm
  * click sản phẩm
  * search
  * add to cart
  * checkout thành công / buy

Nếu dữ liệu thật chưa đủ:

* tạo synthetic behavior dataset vừa đủ để train demo
* có seed cố định
* mô phỏng logic hợp lý theo category / detail_type / shopping pattern
* ghi rõ trong report rằng đây là dữ liệu mô phỏng phục vụ demo học thuật

Không tạo quá nhiều version dataset.

---

## 2. LSTM Model

Phải có model LSTM thật bằng PyTorch.

Yêu cầu code:

* `app/ml/lstm_model.py`
* `app/ml/train_lstm.py`
* `app/services/lstm_service.py`

Logic:

* Input: chuỗi `product_id` user đã tương tác theo thời gian
* Output: top-k `product_id` dự đoán
* Có preprocessing:

  * sort behavior theo user và timestamp
  * encode product_id
  * tạo sequence dataset
  * train / validation / test split
* Có model artifact lưu ra file
* Có service load model để infer

Fallback:

* Nếu model chưa train
* hoặc user history quá ngắn
* hoặc dữ liệu quá ít

thì fallback sang:

* Graph recommendation
* RAG nếu có query
* Popularity baseline

---

## 3. Knowledge Graph bằng Neo4j

Phải có graph thật với:

Node:

* `User`
* `Product`

Edge:

* `VIEW`
* `CLICK`
* `ADD_TO_CART`
* `BUY`
* `SIMILAR`

Yêu cầu:

* Sync product từ `product-service` sang graph.
* Sync behavior sang graph.
* Có logic tạo `SIMILAR` giữa các product dựa trên:

  * cùng category
  * cùng detail_type
  * giá gần nhau
  * keyword overlap trong `name` / `detail` nếu có thể
* Có service query recommendation từ graph.

API:

* `POST /graph/sync`
* `GET /graph/recommend?user_id=...`

---

## 4. RAG / Vector Search

Phải có RAG ở mức MVP nghiêm túc:

* Retrieve từ product catalog thật.
* Generate response chatbot dựa trên retrieved products.

Yêu cầu:

* Lấy product data thật từ `product-service`.
* Convert product thành document text.
* Build vector index bằng FAISS nếu môi trường hỗ trợ.
* Nếu FAISS khó chạy, fallback sang TF-IDF + cosine similarity.
* Có script hoặc API rebuild index.
* Có metadata mapping index → product đủ cho runtime.

API:

* `POST /rag/rebuild-index`

---

## 5. Recommendation API

Phải có API recommendation hoạt động thật:

```http
GET /recommend?user_id=...&query=optional
```

Recommendation phải là hybrid:

* `lstm_score`
* `graph_score`
* `rag_score`
* `popularity_score` fallback nếu cần

Công thức gợi ý:

```text
final_score = 0.4*lstm + 0.3*graph + 0.3*rag
```

Nếu thiếu dữ liệu ở một nguồn, phải normalize lại trọng số hợp lý.

Response không chỉ trả id, mà trả product thật:

```json
{
  "user_id": 1,
  "items": [
    {
      "id": 101,
      "name": "Product name",
      "price": 100,
      "category": "Books",
      "detail_type": "book",
      "score": 0.87,
      "reason": "Recommended from LSTM + Graph + RAG"
    }
  ]
}
```

Không hard-code recommendation cố định.

---

## 6. Chatbot tư vấn sản phẩm

Phải có chatbot cơ bản:

```http
POST /chatbot
```

Input ví dụ:

```json
{
  "user_id": 1,
  "message": "tôi cần laptop giá rẻ"
}
```

Output gồm:

* `answer`
* `products`
* optional `retrieved_context`

Chatbot có thể generate bằng template, nhưng:

* phải retrieve sản phẩm thật
* phải dựa trên context sản phẩm
* không được chỉ trả câu hard-code cố định
* đủ nghiêm túc để thể hiện chatbot tư vấn

---

# YÊU CẦU FRONTEND

Cập nhật frontend ở mức vừa đủ:

1. Gửi behavior events về `ai-service`.
2. Thêm block “Gợi ý cho bạn”.
3. Thêm chatbot widget hoặc trang chatbot đơn giản.
4. Thêm proxy `/api/ai/*` tới `ai-service`.

Không cần UI quá phức tạp, nhưng phải:

* hoạt động được
* demo được
* không phá luồng hiện tại

---

# YÊU CẦU TESTING

Thêm test / verification ở mức hợp lý:

* unit test cho service logic quan trọng
* test preprocess LSTM
* test graph sync
* test RAG retrieval
* test API endpoints chính
* smoke test end-to-end

Có thể tạo:

* `docs/ai-service/ai-service-smoke-test.md`
* script smoke test
* script benchmark nhẹ

Không cần tạo quá nhiều log test nhỏ.

---

# YÊU CẦU DOCKER COMPOSE

Cập nhật `docker-compose.yml` để thêm:

* `ai-service`
* `ai-db`
* `neo4j`

Đảm bảo:

* có env variables
* có volume nếu cần
* có dependency order hợp lý
* có hướng dẫn khởi chạy

---

# CÁC PHASE TRIỂN KHAI

Bạn phải làm tuần tự theo các phase sau.

Mỗi lần tôi yêu cầu, chỉ làm đúng phase đó hoặc nhóm task rất gần nhau.
Không làm tràn lan sang phase sau nếu tôi chưa yêu cầu.

---

## Phase 0 – Audit & Design

Mục tiêu:

* đọc repo hiện tại
* hiểu kiến trúc hiện tại
* đề xuất kế hoạch tích hợp `ai-service`
* xác định file / thư mục sẽ cần thêm / sửa
* xác định dependency mới
* tạo design doc ban đầu

Deliverables:

* summary ngắn về repo
* kế hoạch phase
* design doc ban đầu
* chưa sửa sâu code nếu chưa cần

---

## Phase 1 – Skeleton AI Service

Mục tiêu:

* tạo `ai-service`
* tạo FastAPI app
* thêm Dockerfile
* thêm vào docker-compose
* tạo `/health`
* tạo README riêng cho ai-service

Deliverables:

* code skeleton chạy được
* hướng dẫn run
* smoke test health

Không cần tạo nhiều artifact.

---

## Phase 2 – Behavior Tracking + Data Persistence

Mục tiêu:

* tạo DB model
* tạo `POST /behavior`
* tạo `GET /behavior/user/{user_id}`
* lưu event thật
* kết nối frontend / điểm gửi behavior nếu phù hợp

Deliverables:

* behavior API hoạt động
* schema / migration
* sample behavior tối thiểu
* report ngắn nếu cần

Visualization nếu phù hợp:

* action distribution
* user event count
* product interaction top-k

Không tạo quá nhiều CSV/JSON phụ.

---

## Phase 3 – Product Sync + Dataset Preparation

Mục tiêu:

* tạo client gọi `product-service`
* đồng bộ product catalog
* tạo document corpus cho RAG
* chuẩn bị behavior sequence cho LSTM
* nếu dữ liệu ít thì sinh synthetic behavior dataset vừa đủ

Việc cần làm:

1. Kiểm tra code `ai-service` hiện tại sau Phase 2.
2. Tạo hoặc hoàn thiện product client.
3. Đồng bộ product catalog từ `product-service`.
4. Convert product thành document text cho RAG.
5. Chuẩn bị dữ liệu behavior cho LSTM.
6. Nếu cần synthetic data:

   * dùng seed cố định
   * mô phỏng user preference theo category/detail_type
   * có sequence view → click → add_to_cart → buy
   * ghi rõ là synthetic data trong report

Artifact được phép lưu:

* product snapshot nếu cần cho reproducibility
* synthetic behavior dataset nếu thật sự cần train
* product document corpus nếu cần cho RAG
* `docs/ai-service/reports/phase-3-product-dataset-report.md`

Visualization nên tạo:

* `docs/ai-service/plots/dataset/action_distribution.png`
* `docs/ai-service/plots/dataset/category_distribution.png`
* `docs/ai-service/plots/dataset/detail_type_distribution.png`
* `docs/ai-service/plots/dataset/user_event_distribution.png`
* `docs/ai-service/plots/dataset/product_interaction_topk.png`
* `docs/ai-service/plots/dataset/sequence_length_distribution.png`
* `docs/ai-service/plots/dataset/user_category_heatmap.png`

Không tạo:

* manifest
* dependency matrix
* inventory table
* quá nhiều schema/count CSV
* nhiều dataset version không dùng lại

Sau Phase 3 thì dừng lại.

---

## Phase 4 – Neo4j Knowledge Graph

Mục tiêu:

* thêm Neo4j
* sync product và behavior vào graph
* tạo edge `SIMILAR`
* tạo graph recommendation service

Việc cần làm:

1. Đảm bảo `docker-compose.yml` có Neo4j.
2. Tạo graph service trong `ai-service`.
3. Sync product catalog thành node `Product`.
4. Sync behavior thành node `User` và edge behavior.
5. Tạo edge `SIMILAR`.
6. Implement graph recommendation.
7. Tạo API:

   * `POST /graph/sync`
   * `GET /graph/recommend?user_id=...`

Visualization nên tạo:

* `docs/ai-service/plots/graph/node_count_by_type.png`
* `docs/ai-service/plots/graph/edge_count_by_type.png`
* `docs/ai-service/plots/graph/product_degree_distribution.png`
* `docs/ai-service/plots/graph/top_connected_products.png`
* `docs/ai-service/plots/graph/user_activity_graph.png`

Screenshot nếu có thể:

* `docs/ai-service/screenshots/neo4j-sample-graph.png`

Report:

* `docs/ai-service/reports/phase-4-graph-report.md`

Report cần có:

* node / edge model
* cách tạo `SIMILAR`
* ví dụ Cypher
* ví dụ output recommendation
* đường dẫn biểu đồ
* hạn chế hiện tại

Sau Phase 4 thì dừng lại.

---

## Phase 5 – RAG / Vector Search

Mục tiêu:

* build vector index
* retrieve sản phẩm theo query
* chuẩn bị nền cho chatbot

Việc cần làm:

1. Dùng product document corpus từ Phase 3.
2. Build vector index bằng FAISS nếu được.
3. Nếu FAISS khó chạy, fallback TF-IDF + cosine similarity.
4. Implement RAG service:

   * build index
   * load index
   * retrieve top-k products
5. Tạo API:

   * `POST /rag/rebuild-index`

Visualization nên tạo:

* `docs/ai-service/plots/rag/retrieval_latency.png`
* `docs/ai-service/plots/rag/topk_score_distribution.png`
* `docs/ai-service/plots/rag/index_build_time.png`
* `docs/ai-service/plots/rag/retrieval_method_comparison.png` nếu có nhiều method

Report:

* `docs/ai-service/reports/phase-5-rag-report.md`

Report cần có:

* cách tạo document từ product
* vector method đang dùng
* ví dụ query
* sản phẩm retrieve được
* latency trung bình
* ưu điểm / hạn chế
* đường dẫn biểu đồ

Chỉ lưu FAISS index / metadata cần cho runtime.

Sau Phase 5 thì dừng lại.

---

## Phase 6 – LSTM Model Training & Evaluation

Mục tiêu:

* xây dựng model LSTM thật bằng PyTorch
* train model dự đoán sản phẩm tiếp theo
* đánh giá model bằng nhiều metrics và biểu đồ

Đây là phase quan trọng nhất về visualization.

Việc cần làm:

1. Tạo / hoàn thiện:

   * `app/ml/lstm_model.py`
   * `app/ml/train_lstm.py`
   * `app/services/lstm_service.py`
2. Preprocess behavior sequence:

   * sort event theo user và timestamp
   * encode product_id
   * tạo sequence input
   * train / validation / test split
3. Train LSTM:

   * dùng PyTorch
   * lưu model artifact
   * log train loss / val loss
4. Evaluate:

   * accuracy
   * top-k accuracy
   * precision@k
   * recall@k
   * hit rate@k
   * MRR nếu phù hợp
   * NDCG@k nếu phù hợp
5. So sánh nhiều thông số:

   * sequence length khác nhau
   * hidden_dim khác nhau
   * embedding_dim khác nhau
   * top-k khác nhau
6. So sánh baseline:

   * popularity baseline
   * random baseline nếu phù hợp
   * LSTM only
7. Implement inference service:

   * input user_id
   * output top-k product_id + score
   * fallback nếu user history quá ngắn hoặc model chưa train

Visualization bắt buộc:

* `docs/ai-service/plots/lstm/training_loss_curve.png`
* `docs/ai-service/plots/lstm/validation_loss_curve.png`
* `docs/ai-service/plots/lstm/train_val_loss_comparison.png`
* `docs/ai-service/plots/lstm/topk_accuracy_comparison.png`
* `docs/ai-service/plots/lstm/precision_recall_at_k.png`
* `docs/ai-service/plots/lstm/hit_rate_at_k.png`
* `docs/ai-service/plots/lstm/mrr_ndcg_comparison.png`
* `docs/ai-service/plots/lstm/confusion_matrix.png`
* `docs/ai-service/plots/lstm/hyperparameter_comparison.png`
* `docs/ai-service/plots/lstm/sequence_length_comparison.png`
* `docs/ai-service/plots/lstm/inference_latency.png`
* `docs/ai-service/plots/lstm/baseline_vs_lstm.png`

Nếu số lượng class quá lớn, confusion matrix có thể là top-N class confusion matrix.

Report:

* `docs/ai-service/reports/phase-6-lstm-evaluation.md`

Report cần có:

* dataset dùng để train
* cách tạo sequence
* kiến trúc LSTM
* tham số train
* metrics
* bảng so sánh baseline vs LSTM
* biểu đồ đã sinh
* nhận xét performance
* hạn chế model
* lý do cần fallback

Không lưu:

* toàn bộ batch logs
* quá nhiều dataset trung gian
* quá nhiều checkpoint không dùng

Chỉ lưu:

* model artifact tốt nhất
* metrics summary
* biểu đồ `.png`
* report markdown

Sau Phase 6 thì dừng lại.

---

## Phase 7 – Hybrid Recommendation API

Mục tiêu:

* tạo API recommendation chính
* kết hợp LSTM, Graph, RAG và fallback

Việc cần làm:

1. Implement:

```http
GET /recommend?user_id=...&query=optional
```

2. Lấy candidate từ:

   * LSTM
   * Graph
   * RAG nếu có query
   * popularity fallback
3. Tính final score:

```text
final_score = 0.4*lstm_score + 0.3*graph_score + 0.3*rag_score
```

4. Nếu thiếu source nào thì normalize lại trọng số.
5. Response trả product thật từ `product-service`.
6. Response có reason giải thích.
7. Không hard-code recommendation cố định.

Visualization nên tạo:

* `docs/ai-service/plots/hybrid/source_score_comparison.png`
* `docs/ai-service/plots/hybrid/final_score_distribution.png`
* `docs/ai-service/plots/hybrid/model_ablation_comparison.png`
* `docs/ai-service/plots/hybrid/baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid.png`
* `docs/ai-service/plots/hybrid/recommendation_latency.png`
* `docs/ai-service/plots/hybrid/top_recommended_products.png`

Report:

* `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`

Report cần có:

* công thức scoring
* normalize score
* fallback logic
* ví dụ request / response
* so sánh các nguồn recommendation
* phân tích vì sao hybrid tốt hơn từng nguồn đơn lẻ
* đường dẫn biểu đồ

Sau Phase 7 thì dừng lại.

---

## Phase 8 – Chatbot Tư Vấn Sản Phẩm

Mục tiêu:

* xây dựng chatbot cơ bản đúng yêu cầu Chương 3
* nhận query tự nhiên
* retrieve sản phẩm bằng RAG
* generate câu trả lời bằng template dựa trên retrieved products

Việc cần làm:

1. Implement:

```http
POST /chatbot
```

2. Input:

   * `user_id`
   * `message`
3. Xử lý:

   * phân tích keyword / intent đơn giản
   * retrieve top-k product bằng RAG
   * nếu có user_id thì có thể kết hợp lịch sử user
   * generate answer bằng template nghiêm túc
4. Output:

   * `answer`
   * `products`
   * optional `retrieved_context`
5. Chatbot phải dựa trên product retrieve thật.

Visualization nên tạo:

* `docs/ai-service/plots/rag/chatbot_latency.png`
* `docs/ai-service/plots/rag/query_type_distribution.png`
* `docs/ai-service/plots/rag/chatbot_retrieval_score_distribution.png`
* `docs/ai-service/plots/rag/chatbot_top_product_categories.png`

Report:

* `docs/ai-service/reports/phase-8-chatbot-report.md`

Report cần có:

* pipeline chatbot
* ví dụ input / output
* case studies:

  * “tôi cần laptop giá rẻ”
  * “gợi ý sách học lập trình”
  * “tìm sản phẩm thời trang”
  * “sản phẩm nào phù hợp để làm quà”
* nhận xét hạn chế
* lý do dùng template generation thay vì LLM thật nếu chưa tích hợp LLM

Sau Phase 8 thì dừng lại.

---

## Phase 9 – Frontend Integration

Mục tiêu:

* tích hợp AI Service vào frontend để demo được

Việc cần làm:

1. Thêm proxy `/api/ai/*` đến `ai-service`.
2. Gửi behavior event khi user:

   * xem sản phẩm
   * click sản phẩm
   * search
   * add to cart
   * checkout / buy
3. Thêm section:

   * “Gợi ý cho bạn”
4. Thêm chatbot widget hoặc chatbot page:

   * nhập câu hỏi
   * hiển thị answer
   * hiển thị product suggestions

Screenshot cần lưu:

* `docs/ai-service/screenshots/recommendation-ui.png`
* `docs/ai-service/screenshots/chatbot-ui.png`
* `docs/ai-service/screenshots/behavior-tracking-demo.png` nếu phù hợp

Report cần cập nhật:

* `docs/ai-service/ai-service-smoke-test.md`
* `docs/ai-service/reports/final-ai-service-summary.md`

Sau Phase 9 thì dừng lại.

---

## Phase 10 – Final Documentation & Cleanup

Mục tiêu:

* dọn repo
* tránh rác artifact
* hoàn thiện tài liệu để nộp bài / bảo vệ

Việc cần làm:

1. Xóa hoặc không commit file trung gian không cần thiết.
2. Giữ lại:

   * source code
   * model artifact nếu cần demo
   * FAISS index nếu cần runtime
   * biểu đồ `.png`
   * markdown reports
   * screenshot chính
   * smoke test script
3. Hoàn thiện tài liệu:

   * `docs/ai-service/ai-service-api.md`
   * `docs/ai-service/ai-recommendation-pipeline.md`
   * `docs/ai-service/ai-chatbot-rag.md`
   * `docs/ai-service/ai-service-smoke-test.md`
   * `docs/ai-service/reports/final-ai-service-summary.md`
4. Tạo bảng mapping:

   * yêu cầu Chương 3
   * phần đã implement
   * file code liên quan
   * bằng chứng / biểu đồ liên quan
5. Chạy smoke test cuối.

Report cuối:

* `docs/ai-service/reports/final-ai-service-summary.md`

Nội dung report cuối:

* kiến trúc AI Service
* LSTM
* Neo4j Graph
* RAG
* Hybrid Recommendation
* Chatbot
* API
* frontend integration
* biểu đồ đánh giá chính
* hạn chế
* hướng phát triển

---

# FORMAT PHẢN HỒI SAU MỖI PHASE

Sau mỗi phase, trả lời đúng format:

## Phase vừa làm

Tên phase.

## Đã implement

Liệt kê ngắn gọn.

## Files đã tạo / sửa

Liệt kê file chính, không cần liệt kê file rác.

## Cách chạy / test

Command cụ thể.

## Visualization / Evidence đã tạo

Chỉ liệt kê:

* biểu đồ `.png`
* report `.md`
* model artifact
* FAISS index
* screenshot quan trọng
* benchmark summary nếu có

## Checklist Chương 3 đã đáp ứng thêm

Nói rõ phase này giúp đáp ứng mục nào:

* LSTM
* Graph
* RAG
* Recommendation API
* Chatbot
* Pipeline AI
* API hoạt động

## Hạn chế hiện tại

Nói thật, ngắn gọn.

## Phase tiếp theo

Đề xuất phase tiếp theo.

---

# QUY TẮC CHẤT LƯỢNG CODE

* Code rõ ràng, dễ đọc.
* Không nhồi tất cả logic vào 1 file.
* Có typing nếu hợp lý.
* Tách module rõ:

  * router
  * service
  * client
  * graph
  * rag
  * ml
* Có config rõ ràng.
* Có env variables rõ ràng.
* Có error handling hợp lý.
* Có logs vừa đủ.
* Có README và docs.
* Có script hỗ trợ tái hiện kết quả chính.

---

# NHỮNG THỨ TUYỆT ĐỐI KHÔNG ĐƯỢC LÀM

* Không hard-code output recommendation cố định.
* Không fake LSTM bằng cách chỉ viết file mô tả mà không có train/infer thật.
* Không fake graph bằng ảnh minh họa mà không có Neo4j thật.
* Không fake RAG bằng if/else đơn giản mà không có retrieve thật.
* Không bỏ qua phần đánh giá model và biểu đồ.
* Không tạo quá nhiều artifact trung gian không có giá trị.
* Không làm vội một cục quá lớn khó review.
* Không phá luồng hiện tại của hệ thống.

---

# BẮT ĐẦU LÀM VIỆC

Nếu repo chưa có Phase 0, bắt đầu với:

## Phase 0 – Audit & Design

Hãy:

1. đọc cấu trúc repo hiện tại
2. tóm tắt kiến trúc hiện tại
3. đề xuất kế hoạch triển khai `ai-service` khớp với monorepo
4. chỉ ra file / thư mục sẽ cần thêm / sửa
5. đề xuất dependency mới
6. tạo design doc ban đầu
7. chưa làm tràn sang các phase sâu hơn nếu chưa cần

Sau khi hoàn tất Phase 0, dừng lại và chờ tôi yêu cầu phase tiếp theo.

Nếu tôi nói “đã xong Phase 2”, hãy bắt đầu trực tiếp từ:

## Phase 3 – Product Sync + Dataset Preparation

Khi bắt đầu từ Phase 3, nhớ:

* không tạo quá nhiều artifact trung gian
* chỉ tạo dataset tối thiểu cần cho train/RAG
* tập trung vào report và biểu đồ `.png` có giá trị phân tích
* sau khi hoàn thành Phase 3 thì dừng lại, không tự làm Phase 4

```

Điểm khác biệt chính so với bản cũ là: **không còn bắt lưu mọi thứ thành file**, chỉ giữ các evidence có giá trị như biểu đồ, report, model artifact, FAISS index, screenshot và benchmark summary.
```
