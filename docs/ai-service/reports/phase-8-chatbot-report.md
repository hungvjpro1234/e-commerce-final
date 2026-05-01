# Phase 8 Chatbot Report

## Chatbot pipeline

- Receive `user_id` and natural-language `message`.
- Classify lightweight intent from the message.
- Retrieve real products from the RAG index.
- Optionally boost ranking with personalized recommendation scores when `user_id` is available.
- Generate a grounded template answer from the retrieved product context.

## Input / output examples

- `toi can laptop gia re` -> top product: `Laptop Pro 14`
- `goi y sach hoc lap trinh` -> top product: `Clean Architecture`
- `tim san pham thoi trang` -> top product: `Classic Hoodie`
- `san pham nao phu hop de lam qua` -> top product: `Laptop Pro 14`

## Case studies

- `toi can laptop gia re`
- `goi y sach hoc lap trinh`
- `tim san pham thoi trang`
- `san pham nao phu hop de lam qua`

## Limitations

- The response generation is template-based rather than LLM-based, so phrasing is controlled and concise.
- Query understanding is heuristic; richer NLP can improve intent extraction later.
- Retrieval quality still depends on the small current product corpus.

## Why template generation is used now

- It keeps the chatbot grounded in retrieved catalog data and avoids fabricated product claims.
- It is sufficient for the Chapter 3 MVP without introducing an external LLM dependency.

## Evidence

- `docs/ai-service/plots/rag/chatbot_latency.png`
- `docs/ai-service/plots/rag/query_type_distribution.png`
- `docs/ai-service/plots/rag/chatbot_retrieval_score_distribution.png`
- `docs/ai-service/plots/rag/chatbot_top_product_categories.png`
