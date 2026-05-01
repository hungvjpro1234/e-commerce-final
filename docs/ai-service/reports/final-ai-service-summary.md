# Final AI Service Summary (Phase 10)

## Kết quả tổng thể

Chương 3 đã hoàn tất end-to-end với `ai-service` FastAPI tích hợp Docker Compose và frontend Next.js.  
Phase 10 tập trung vào cleanup artifact trung gian và chuẩn hóa bộ tài liệu nộp/bảo vệ.

## Kiến trúc AI Service

- Behavior tracking: `POST /behavior`, `GET /behavior/user/{user_id}`
- LSTM next-product: train/infer bằng PyTorch
- Neo4j graph: sync user-product interactions + `SIMILAR`
- RAG retrieval: TF-IDF + cosine, lưu index local cho runtime
- Hybrid recommendation: hợp nhất `lstm + graph + rag + popularity fallback`
- Chatbot tư vấn: retrieval-grounded template generation
- Frontend integration: `/api/ai/*`, block recommendation, trang chatbot

## Runtime artifacts giữ lại

- `ai-service/artifacts/lstm/best_lstm_model.pt`
- `ai-service/artifacts/lstm/lstm_metadata.json`
- `ai-service/artifacts/rag/tfidf_cosine_index.pkl`
- `ai-service/artifacts/rag/tfidf_cosine_documents.json`
- `ai-service/artifacts/rag/tfidf_cosine_metadata.json`

## Evidence chính theo phase

- Phase 3: `docs/ai-service/reports/phase-3-product-dataset-report.md`
- Phase 4: `docs/ai-service/reports/phase-4-graph-report.md`
- Phase 5: `docs/ai-service/reports/phase-5-rag-report.md`
- Phase 6: `docs/ai-service/reports/phase-6-lstm-evaluation.md`
- Phase 7: `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`
- Phase 8: `docs/ai-service/reports/phase-8-chatbot-report.md`
- Smoke test final: `docs/ai-service/ai-service-smoke-test.md`
- Screenshots:
  - `docs/ai-service/screenshots/recommendation-ui.png`
  - `docs/ai-service/screenshots/chatbot-ui.png`
  - `docs/ai-service/screenshots/behavior-tracking-demo.png`

## Mapping yêu cầu Chương 3 -> implementation

| Yêu cầu | Đã implement | File code chính | Evidence |
| --- | --- | --- | --- |
| LSTM model thật | Training + inference + fallback | `ai-service/app/ml/lstm_model.py`, `ai-service/app/ml/train_lstm.py`, `ai-service/app/services/lstm_service.py` | `docs/ai-service/reports/phase-6-lstm-evaluation.md`, `docs/ai-service/plots/lstm/` |
| Knowledge Graph Neo4j | Sync graph + query recommend | `ai-service/app/services/graph.py`, `ai-service/app/routers/graph.py`, `ai-service/scripts/sync_graph.py` | `docs/ai-service/reports/phase-4-graph-report.md` |
| RAG / Vector Search | Rebuild index + retrieve sản phẩm thật | `ai-service/app/services/rag.py`, `ai-service/app/routers/rag.py`, `ai-service/scripts/rebuild_rag_index.py` | `docs/ai-service/reports/phase-5-rag-report.md`, `docs/ai-service/plots/rag/` |
| Recommendation API hybrid | Hợp nhất nhiều nguồn + lý do | `ai-service/app/services/recommend.py`, `ai-service/app/routers/recommend.py` | `docs/ai-service/reports/phase-7-hybrid-recommendation-report.md`, `docs/ai-service/plots/hybrid/` |
| Chatbot tư vấn sản phẩm | Query tự nhiên -> retrieval-grounded answer | `ai-service/app/services/chatbot.py`, `ai-service/app/routers/chatbot.py` | `docs/ai-service/reports/phase-8-chatbot-report.md`, `docs/ai-service/screenshots/chatbot-ui.png` |
| Behavior tracking | Lưu + truy xuất events | `ai-service/app/services/behavior.py`, `ai-service/app/routers/behavior.py` | `docs/ai-service/ai-service-smoke-test.md` |
| API hoạt động & tích hợp FE | Proxy `/api/ai/*`, recommendation + chatbot UI | `frontend/app/api/[...path]/route.ts`, `frontend/app/chatbot/page.tsx` | `docs/ai-service/screenshots/recommendation-ui.png`, `docs/ai-service/screenshots/behavior-tracking-demo.png` |

## Cleanup đã thực hiện ở Phase 10

- Xóa nhóm artifact trung gian không cần thiết:
  - `docs/ai-service/artifacts/tables/*`
  - `docs/ai-service/artifacts/eval/*.json`
  - các report implementation/index trung gian trong `docs/ai-service/artifacts/reports/`
- Giữ lại source code, runtime artifacts, plots, reports, screenshots và smoke-test doc.

## Hạn chế hiện tại

- Hybrid weight vẫn heuristic, chưa học online từ feedback thật.
- Chatbot chưa tích hợp LLM ngoài, hiện dùng template-grounded generation.
- Chất lượng retrieval và sequence modeling phụ thuộc quy mô catalog/behavior hiện tại.

## Hướng phát triển

- Bổ sung dense vector retrieval (FAISS embedding) cho semantic recall tốt hơn.
- Tối ưu hybrid weighting bằng học trọng số từ conversion signals.
- Mở rộng intent parsing và response style cho chatbot.
