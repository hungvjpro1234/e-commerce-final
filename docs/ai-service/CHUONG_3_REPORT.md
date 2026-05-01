# CHUONG 3. AI SERVICE CHO TU VAN SAN PHAM

## 3.1 Muc tieu

Muc tieu cua AI Service trong he thong e-commerce la bo sung lop tri tue nhan tao cho hai dau ra nghiep vu chinh: (i) danh sach san pham de xuat theo ngu canh nguoi dung, va (ii) chatbot tu van san pham theo cau hoi tu nhien. Trong codebase hien tai, hai dau ra nay duoc hien thuc hoa boi endpoint `GET /recommend` va `POST /chatbot`, dong thoi duoc tich hop vao frontend thong qua proxy `/api/ai/*`.

He thong duoc to chuc thanh microservice rieng (`ai-service`) de dam bao tinh dong goi va kha nang mo rong doc lap voi cac service thuong mai dien tu san co.

**Code evidence:**
- `ai-service/app/main.py`
- `ai-service/app/routers/recommend.py`
- `ai-service/app/routers/chatbot.py`
- `frontend/app/api/[...path]/route.ts`

**Artifact evidence:**
- `docs/ai-service/reports/final-ai-service-summary.md`
- `docs/ai-service/screenshots/recommendation-ui.png`
- `docs/ai-service/screenshots/chatbot-ui.png`

## 3.2 Kien truc AI Service

`ai-service` duoc xay dung bang FastAPI va khoi tao CSDL ngay trong `lifespan`, sau do dang ky cac router cho health, behavior, graph, rag, recommend, chatbot. Pipeline tong quat theo huong:

`behavior -> xu ly du lieu -> LSTM / Graph / RAG -> hybrid scoring -> API response`

Muc do tich hop he thong:
- Nhan behavior tu frontend va luu trong AI DB.
- Dong bo va truy van tri thuc bo sung tu `product-service`.
- Truy van graph qua Neo4j.
- Cung cap ket qua cho frontend thong qua API gateway noi bo cua Next.js.

[HINH 3.1 - Kien truc tong quan AI Service, chen tu: docs/ai-service/screenshots/behavior-tracking-demo.png]

**Code evidence:**
- `ai-service/app/main.py`
- `ai-service/app/config.py`
- `ai-service/app/services/recommend.py`
- `frontend/app/api/[...path]/route.ts`
- `docker-compose.yml`

**Artifact evidence:**
- `docs/ai-service/ai-recommendation-pipeline.md`
- `docs/ai-service/reports/final-ai-service-summary.md`
- `docs/ai-service/ai-service-smoke-test.md`

## 3.3 Thu thap du lieu

### 3.3.1 Du lieu hanh vi nguoi dung

Du lieu hanh vi duoc mo hinh hoa boi bang `behavior_events` gom cac truong `user_id`, `product_id`, `action`, `query_text`, `timestamp`. Tap hanh dong hop le bao gom: `view`, `click`, `search`, `add_to_cart`, `buy`. Validation payload duoc thuc hien o schema:
- voi `search`: bat buoc co `query_text`
- voi hanh dong khac: bat buoc co `product_id`

Hai API chinh:
- `POST /behavior`: ghi nhan su kien hanh vi
- `GET /behavior/user/{user_id}`: truy xuat lich su hanh vi theo user

[SCREENSHOT 3.1 - Demo behavior tracking tren giao dien/frontend flow, chen tu: docs/ai-service/screenshots/behavior-tracking-demo.png]

**Code evidence:**
- `ai-service/app/models/behavior.py`
- `ai-service/app/schemas/behavior.py`
- `ai-service/app/routers/behavior.py`
- `ai-service/app/services/behavior.py`
- `frontend/lib/ai.ts`

**Artifact evidence:**
- `docs/ai-service/ai-service-smoke-test.md`
- `docs/ai-service/artifacts/reports/phase-9-smoke-test-results.md`

### 3.3.2 Du lieu san pham va du lieu phuc vu recommendation

AI Service lay catalog tu `product-service` thong qua `ProductServiceClient`, sau do tao cac bo du lieu phuc vu huan luyen va retrieval:
- product snapshot
- product document corpus
- cleaned behavior dataset
- synthetic behavior dataset
- sequence dataset va train/val/test split

Trong bo evidence hien co, cac file dataset cua Phase 3 van ton tai day du.

[BIEU DO 3.1 - Phan bo category du lieu, chen tu: docs/ai-service/artifacts/plots/phase-3-category-distribution.png]  
[BIEU DO 3.2 - Phan bo detail_type du lieu, chen tu: docs/ai-service/artifacts/plots/phase-3-detail-type-distribution.png]  
[BIEU DO 3.3 - Phan bo do dai sequence, chen tu: docs/ai-service/artifacts/plots/phase-3-sequence-length-distribution.png]

**Code evidence:**
- `ai-service/app/clients/product_client.py`
- `ai-service/app/services/catalog.py`
- `ai-service/scripts/build_phase3_datasets.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-3-product-dataset-report.md`
- `docs/ai-service/artifacts/datasets/phase-3-product-snapshot.json`
- `docs/ai-service/artifacts/datasets/phase-3-product-document-corpus.jsonl`
- `docs/ai-service/artifacts/datasets/phase-3-sequence-dataset.json`

## 3.4 Mo hinh LSTM

### 3.4.1 Y tuong

Bai toan duoc dat ra la du doan san pham tiep theo tu chuoi tuong tac san pham cua nguoi dung theo thu tu thoi gian. Cac su kien `search` khong duoc dung lam target du doan trong sequence modeling.

**Code evidence:**
- `ai-service/app/ml/train_lstm.py`
- `ai-service/app/services/lstm_service.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-6-lstm-evaluation.md`

### 3.4.2 Thiet ke model

Model `NextProductLSTM` duoc dinh nghia bang PyTorch voi cac thanh phan:
- `Embedding`
- `LSTM`
- `Dropout`
- `Linear` output de du doan logit tren khong gian product token

Model dung `pack_padded_sequence` de xu ly chuoi co do dai khac nhau.

**Code evidence:**
- `ai-service/app/ml/lstm_model.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-6-lstm-evaluation.md`

### 3.4.3 Huan luyen va danh gia

Pipeline train/eval thuc hien trong `train_and_evaluate_lstm`:
- tai du lieu hanh vi + sequence
- split train/val/test
- chay nhieu cau hinh (sequence length, embedding dim, hidden dim)
- danh gia metrics: accuracy, top-k accuracy, precision@k, recall@k, hit rate@k, MRR, NDCG@k
- so sanh baseline `random`, `popularity`

Runtime artifact sau huan luyen:
- `ai-service/artifacts/lstm/best_lstm_model.pt`
- `ai-service/artifacts/lstm/lstm_metadata.json`

Co che fallback trong infer:
- neu thieu model artifact hoac lich su user qua ngan, service fallback sang ranking theo popularity.

[BIEU DO 3.4 - Training loss curve, chen tu: docs/ai-service/plots/lstm/training_loss_curve.png]  
[BIEU DO 3.5 - Validation loss curve, chen tu: docs/ai-service/plots/lstm/validation_loss_curve.png]  
[BIEU DO 3.6 - Top-k accuracy comparison, chen tu: docs/ai-service/plots/lstm/topk_accuracy_comparison.png]  
[BIEU DO 3.7 - Precision/Recall@k, chen tu: docs/ai-service/plots/lstm/precision_recall_at_k.png]  
[BIEU DO 3.8 - Baseline vs LSTM, chen tu: docs/ai-service/plots/lstm/baseline_vs_lstm.png]

**Code evidence:**
- `ai-service/app/ml/train_lstm.py`
- `ai-service/scripts/train_lstm.py`
- `ai-service/app/services/lstm_service.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-6-lstm-evaluation.md`
- `ai-service/artifacts/lstm/best_lstm_model.pt`
- `ai-service/artifacts/lstm/lstm_metadata.json`
- `docs/ai-service/plots/lstm/`

## 3.5 Knowledge Graph voi Neo4j

### 3.5.1 Mo hinh do thi

Mo hinh do thi hien thuc:
- Node: `User`, `Product`
- Edge tuong tac: `VIEW`, `CLICK`, `ADD_TO_CART`, `BUY`
- Edge tuong dong: `SIMILAR`

`SIMILAR` duoc tao boi to hop heuristic: cung category, cung `detail_type`, gia gan nhau, giao nhau tu khoa.

**Code evidence:**
- `ai-service/app/services/graph.py`
- `ai-service/app/graph/store.py`
- `ai-service/app/schemas/graph.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-4-graph-report.md`

### 3.5.2 Cach dong bo du lieu vao graph

Qua trinh sync:
1. Lay product catalog
2. Lay behavior events tu AI DB
3. Xoa graph cu, upsert node moi
4. Tao interaction edges (bo qua `search`)
5. Tinh va tao `SIMILAR` edges

API va script lien quan:
- `POST /graph/sync`
- `scripts/sync_graph.py`

**Code evidence:**
- `ai-service/app/routers/graph.py`
- `ai-service/app/services/graph.py`
- `ai-service/scripts/sync_graph.py`

**Artifact evidence:**
- `docs/ai-service/ai-service-smoke-test.md`
- `docs/ai-service/reports/phase-4-graph-report.md`

### 3.5.3 Truy van goi y

Graph recommendation duoc trien khai thong qua `GET /graph/recommend?user_id=...`, uu tien khai thac neighborhood tu lich su user; neu khong co ket qua thi fallback ve graph popularity.

[BIEU DO 3.9 - Node/edge counts cua graph, chen tu: docs/ai-service/artifacts/plots/phase-4-node-edge-counts.png]  
[BIEU DO 3.10 - Relationship distribution, chen tu: docs/ai-service/artifacts/plots/phase-4-relationship-distribution.png]

**Code evidence:**
- `ai-service/app/services/graph.py`
- `ai-service/app/routers/graph.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-4-graph-report.md`
- `docs/ai-service/artifacts/plots/phase-4-node-edge-counts.png`
- `docs/ai-service/artifacts/plots/phase-4-relationship-distribution.png`

## 3.6 RAG / Retrieval

### 3.6.1 Pipeline retrieval

Pipeline RAG gom:
1. Nap product documents (uu tien corpus phase 3)
2. Build TF-IDF matrix + cosine retrieval
3. Persist runtime index
4. Retrieve top-k theo query
5. Ground response bang product payload that

Endpoint quan trong: `POST /rag/rebuild-index`.

**Code evidence:**
- `ai-service/app/services/rag.py`
- `ai-service/app/routers/rag.py`
- `ai-service/scripts/rebuild_rag_index.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-5-rag-report.md`

### 3.6.2 Vector / index storage

Cong nghe retrieval dang dung trong repo la `TF-IDF + cosine similarity` (khong phai FAISS runtime). Day la quyet dinh ky thuat de uu tien tinh on dinh va de deploy local trong pham vi bai tap lon.

Runtime artifacts:
- `ai-service/artifacts/rag/tfidf_cosine_index.pkl`
- `ai-service/artifacts/rag/tfidf_cosine_documents.json`
- `ai-service/artifacts/rag/tfidf_cosine_metadata.json`

[BIEU DO 3.11 - Retrieval latency, chen tu: docs/ai-service/plots/rag/retrieval_latency.png]  
[BIEU DO 3.12 - Top-k score distribution, chen tu: docs/ai-service/plots/rag/topk_score_distribution.png]  
[BIEU DO 3.13 - Index build time, chen tu: docs/ai-service/plots/rag/index_build_time.png]

**Code evidence:**
- `ai-service/app/services/rag.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-5-rag-report.md`
- `ai-service/artifacts/rag/tfidf_cosine_index.pkl`
- `ai-service/artifacts/rag/tfidf_cosine_metadata.json`

### 3.6.3 Ung dung cho chatbot va recommendation

RAG duoc dung o 2 lop:
- recommendation: bo sung candidate theo query text
- chatbot: retrieval grounded cho answer generation

Trong recommendation service, candidate RAG duoc hop nhat cung LSTM/Graph/Popularity. Trong chatbot service, ket qua RAG duoc rerank theo personalized score (neu co user) truoc khi tao cau tra loi template.

**Code evidence:**
- `ai-service/app/services/recommend.py`
- `ai-service/app/services/chatbot.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`
- `docs/ai-service/reports/phase-8-chatbot-report.md`

## 3.7 Ket hop Hybrid Model

Hybrid recommendation duoc xay dung de tranh phu thuoc vao mot nguon don le:
- LSTM: signal theo thu tu hanh vi
- Graph: signal cau truc quan he
- RAG: signal truy van tu nhien
- Popularity: fallback khi thieu du lieu/nguon

Trong implementation, base weights duoc dat:
- `lstm=0.4`, `graph=0.3`, `rag=0.3`, `popularity=0.2`

Sau do he thong chuan hoa lai trong so theo cac nguon thuc su kha dung o moi request.

[BIEU DO 3.14 - Source score comparison, chen tu: docs/ai-service/plots/hybrid/source_score_comparison.png]  
[BIEU DO 3.15 - Model ablation comparison, chen tu: docs/ai-service/plots/hybrid/model_ablation_comparison.png]  
[BIEU DO 3.16 - Baseline vs LSTM vs Graph vs RAG vs Hybrid, chen tu: docs/ai-service/plots/hybrid/baseline_vs_lstm_vs_graph_vs_rag_vs_hybrid.png]

**Code evidence:**
- `ai-service/app/services/recommend.py`
- `ai-service/app/routers/recommend.py`

**Artifact evidence:**
- `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`
- `docs/ai-service/plots/hybrid/`

## 3.8 Hai dang AI Service

### 3.8.1 Recommendation List

Use case: tra ve danh sach san pham de xuat cho user theo query tuy chon, kem score va ly do.

API:
- `GET /recommend?user_id=...&query=optional&limit=...`

Response schema tra ve:
- `items[]` gom `id`, `name`, `price`, `category`, `detail_type`, `score`, `reason`, `source_scores`
- `sources_used` de truy vet nguon de xuat

[SCREENSHOT 3.2 - Recommendation UI, chen tu: docs/ai-service/screenshots/recommendation-ui.png]

**Code evidence:**
- `ai-service/app/routers/recommend.py`
- `ai-service/app/schemas/recommend.py`
- `ai-service/app/services/recommend.py`
- `frontend/app/page.tsx`

**Artifact evidence:**
- `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`
- `docs/ai-service/screenshots/recommendation-ui.png`

### 3.8.2 Chatbot tu van

Luong xu ly:
1. Nhan `user_id` (optional) va `message`
2. Phan loai query type heuristic
3. Retrieve top-k products tu RAG
4. Rerank voi personalized score neu co user
5. Sinh `answer` bang template grounded tren context retrieve duoc

API:
- `POST /chatbot`

Schema response:
- `answer`
- `products`
- `retrieved_context`
- `query_type`

[SCREENSHOT 3.3 - Chatbot UI, chen tu: docs/ai-service/screenshots/chatbot-ui.png]

**Code evidence:**
- `ai-service/app/routers/chatbot.py`
- `ai-service/app/schemas/chatbot.py`
- `ai-service/app/services/chatbot.py`
- `frontend/app/chatbot/page.tsx`

**Artifact evidence:**
- `docs/ai-service/reports/phase-8-chatbot-report.md`
- `docs/ai-service/screenshots/chatbot-ui.png`
- `docs/ai-service/plots/rag/chatbot_latency.png`

## 3.9 Trien khai AI Service

### 3.9.1 Tech stack

Cong nghe su dung that trong repo:
- Backend API: FastAPI
- ORM/DB access: SQLAlchemy
- AI model: PyTorch (LSTM)
- Graph database: Neo4j
- Retrieval: local TF-IDF + cosine
- Frontend integration: Next.js proxy `/api/ai/*`
- Orchestration: Docker Compose

**Code evidence:**
- `ai-service/app/main.py`
- `ai-service/app/ml/lstm_model.py`
- `ai-service/app/services/rag.py`
- `frontend/app/api/[...path]/route.ts`
- `docker-compose.yml`

**Artifact evidence:**
- `docs/ai-service/reports/final-ai-service-summary.md`

### 3.9.2 Kien truc trien khai va tich hop he thong

Trong `docker-compose.yml`, `ai-service` duoc khai bao phu thuoc vao `ai-db`, `neo4j`, `product-service`, `order-service`, va mount `docs/ai-service` vao container de ghi artifacts. Frontend goi AI thong qua prefix `ai` trong gateway route.

Smoke test doc xac nhan cac endpoint cot loi va luong frontend proxy.

**Code evidence:**
- `docker-compose.yml`
- `frontend/app/api/[...path]/route.ts`
- `ai-service/app/config.py`

**Artifact evidence:**
- `docs/ai-service/ai-service-smoke-test.md`
- `docs/ai-service/artifacts/reports/phase-9-smoke-test-results.md`

## 3.10 Ket qua thuc hien

### Bang 3.1. Mapping yeu cau Chuong 3 -> implementation

| Yeu cau de bai | Implementation thuc te | File code chinh | Evidence/deliverable |
| --- | --- | --- | --- |
| Behavior tracking | API ghi/lay hanh vi, validation action schema | `ai-service/app/routers/behavior.py`, `ai-service/app/services/behavior.py`, `ai-service/app/schemas/behavior.py` | `docs/ai-service/ai-service-smoke-test.md` |
| LSTM model that | Train + eval + infer + fallback | `ai-service/app/ml/lstm_model.py`, `ai-service/app/ml/train_lstm.py`, `ai-service/app/services/lstm_service.py` | `docs/ai-service/reports/phase-6-lstm-evaluation.md`, `ai-service/artifacts/lstm/best_lstm_model.pt` |
| Knowledge Graph Neo4j | Sync graph + recommend graph | `ai-service/app/services/graph.py`, `ai-service/app/routers/graph.py`, `ai-service/scripts/sync_graph.py` | `docs/ai-service/reports/phase-4-graph-report.md` |
| RAG retrieval | Build index + retrieve products | `ai-service/app/services/rag.py`, `ai-service/app/routers/rag.py`, `ai-service/scripts/rebuild_rag_index.py` | `docs/ai-service/reports/phase-5-rag-report.md`, `ai-service/artifacts/rag/tfidf_cosine_index.pkl` |
| Hybrid recommendation API | Hop nhat LSTM/Graph/RAG/Popularity | `ai-service/app/services/recommend.py`, `ai-service/app/routers/recommend.py` | `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`, `docs/ai-service/plots/hybrid/` |
| Chatbot tu van | Retrieval-grounded answer + personalization boost | `ai-service/app/services/chatbot.py`, `ai-service/app/routers/chatbot.py` | `docs/ai-service/reports/phase-8-chatbot-report.md`, `docs/ai-service/screenshots/chatbot-ui.png` |
| Frontend integration | Proxy `/api/ai/*`, recommendation block, chatbot page | `frontend/app/api/[...path]/route.ts`, `frontend/app/page.tsx`, `frontend/app/chatbot/page.tsx`, `frontend/lib/ai.ts` | `docs/ai-service/screenshots/recommendation-ui.png`, `docs/ai-service/screenshots/behavior-tracking-demo.png` |

### Bang 3.2. Thanh phan AI pipeline -> code -> artifact

| Thanh phan | File code | Artifact chung minh |
| --- | --- | --- |
| Data ingestion behavior | `ai-service/app/services/behavior.py` | `docs/ai-service/ai-service-smoke-test.md` |
| Dataset preparation | `ai-service/app/services/catalog.py`, `ai-service/scripts/build_phase3_datasets.py` | `docs/ai-service/reports/phase-3-product-dataset-report.md` |
| LSTM training | `ai-service/app/ml/train_lstm.py`, `ai-service/scripts/train_lstm.py` | `docs/ai-service/reports/phase-6-lstm-evaluation.md`, `ai-service/artifacts/lstm/` |
| Graph sync/recommend | `ai-service/app/services/graph.py`, `ai-service/scripts/sync_graph.py` | `docs/ai-service/reports/phase-4-graph-report.md`, `docs/ai-service/artifacts/plots/phase-4-*.png` |
| RAG indexing/retrieval | `ai-service/app/services/rag.py`, `ai-service/scripts/rebuild_rag_index.py` | `docs/ai-service/reports/phase-5-rag-report.md`, `ai-service/artifacts/rag/` |
| Hybrid scoring | `ai-service/app/services/recommend.py` | `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md` |
| Chatbot grounded generation | `ai-service/app/services/chatbot.py` | `docs/ai-service/reports/phase-8-chatbot-report.md` |

### Bang 3.3. API chinh cua AI Service

| Endpoint | Chuc nang | Input chinh | Output chinh |
| --- | --- | --- | --- |
| `GET /health` | Kiem tra trang thai service | none | `service`, `status`, `version`, `dependencies` |
| `POST /behavior` | Ghi su kien hanh vi | `user_id`, `action`, `product_id/query_text`, `timestamp` | behavior event persisted |
| `GET /behavior/user/{user_id}` | Lay lich su hanh vi theo user | path `user_id` | danh sach events theo thu tu thoi gian |
| `POST /graph/sync` | Dong bo du lieu vao graph | none (lay tu DB va catalog) | so luong node/edge da sync |
| `GET /graph/recommend` | Goi y tu graph | `user_id`, `limit` | danh sach graph recommendations |
| `POST /rag/rebuild-index` | Rebuild retrieval index | none | method, document_count, artifact_paths |
| `GET /recommend` | Hybrid recommendation | `user_id`, `query`, `limit` | items + source_scores + reasons |
| `POST /chatbot` | Tu van query tu nhien | `user_id` (optional), `message` | `answer`, `products`, `retrieved_context` |

### Bang 3.4. Runtime artifacts va vai tro

| Artifact | Vai tro runtime | Trang thai |
| --- | --- | --- |
| `ai-service/artifacts/lstm/best_lstm_model.pt` | Trong so model LSTM infer | Co san |
| `ai-service/artifacts/lstm/lstm_metadata.json` | Token map, config, fallback data | Co san |
| `ai-service/artifacts/rag/tfidf_cosine_index.pkl` | Ma tran TF-IDF retrieval | Co san |
| `ai-service/artifacts/rag/tfidf_cosine_documents.json` | Mapping document -> product | Co san |
| `ai-service/artifacts/rag/tfidf_cosine_metadata.json` | Metadata index runtime | Co san |

## 3.11 Danh gia theo checklist

- Pipeline AI ro rang: **Dat**. Da co flow behavior -> dataset -> LSTM/Graph/RAG -> hybrid -> API.  
  **Evidence:** `docs/ai-service/ai-recommendation-pipeline.md`, `ai-service/app/services/recommend.py`.
- Co LSTM that: **Dat**. Co code train/eval/infer va artifact `.pt`.  
  **Evidence:** `ai-service/app/ml/train_lstm.py`, `ai-service/artifacts/lstm/best_lstm_model.pt`.
- Co Graph va RAG: **Dat**. Co API graph sync/recommend va RAG rebuild-index/retrieve.  
  **Evidence:** `ai-service/app/routers/graph.py`, `ai-service/app/routers/rag.py`, `docs/ai-service/reports/phase-4-graph-report.md`, `docs/ai-service/reports/phase-5-rag-report.md`.
- Co API hoat dong: **Dat**. Da co smoke checklist endpoint chinh va tich hop frontend proxy.  
  **Evidence:** `docs/ai-service/ai-service-smoke-test.md`, `frontend/app/api/[...path]/route.ts`.

## 3.12 Han che va huong phat trien

### Bang 3.5. Han che hien tai va huong cai tien

| Han che | Tac dong | Huong cai tien de xuat |
| --- | --- | --- |
| Hybrid weight hien la heuristic | Chua toi uu theo conversion feedback that | Hoc trong so tu du lieu click/buy theo thoi gian |
| Chatbot dung template generation | Chatbot chua linh hoat ngon ngu nhu LLM | Tich hop LLM ngoai voi grounding guardrails |
| Retrieval dang lexical (TF-IDF) | Gioi han voi synonym/semantic drift | Nang cap sang dense embedding + FAISS |
| Du lieu hanh vi/catalog quy mo con nho | Anh huong chat luong ca nhan hoa | Tang luong du lieu that va feedback loop |

Nhan xet quan trong: mot so file summary phu tro (vd. nhom `docs/ai-service/artifacts/eval/*.json`) da duoc cleanup o Phase 10, do do bang chung chinh hien tap trung vao report tong hop, runtime artifacts va plots/screenshot con lai.

**Code evidence:**
- `ai-service/app/services/recommend.py`
- `ai-service/app/services/chatbot.py`
- `ai-service/app/services/rag.py`

**Artifact evidence:**
- `docs/ai-service/reports/final-ai-service-summary.md`
- `docs/ai-service/reports/phase-5-rag-report.md`
- `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`

## 3.13 Ket luan chuong

Chuong 3 da hien thuc thanh cong mot AI microservice co the van hanh trong stack Docker Compose cua he thong e-commerce, dong thoi tao duoc hai gia tri nghiep vu truc tiep: recommendation list va chatbot tu van san pham. Giai phap ket hop LSTM, Knowledge Graph, RAG va hybrid scoring cho thay huong tiep can da mo rong vuot qua mot thuat toan don le, dap ung dong thoi muc tieu hoc thuat (co mo hinh, co danh gia, co artifact) va muc tieu thuc tien (co API, co tich hop UI, co quy trinh smoke test).

Ve mat hoc thuat, chuong nay cung cap mot khung tham chieu ro rang cho bai toan tu van san pham da nguon du lieu. Ve mat ky thuat, kien truc hien tai tao nen nen tang co kha nang nang cap tiep theo huong semantic retrieval nang cao, hoc trong so dong cho hybrid va chatbot thong minh hon.
