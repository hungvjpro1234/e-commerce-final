# Chapter 4 Phase 7 AI Integration

## 1. Purpose

This phase integrates the AI subsystem into the Chapter 4 system view as a first-class service, not as an isolated Chapter 3 artifact.

The master prompt requires the AI service to appear inside the complete architecture and to be demonstrable through the main access path. This phase therefore focuses on:

- exposing AI through the gateway
- documenting what data AI reads from the system
- providing a runnable AI demo script through the Chapter 4 route structure
- linking AI output back to real catalog and user-context data

## 2. Deliverables

### Files added

- `scripts/ai_gateway_demo.ps1`
- `docs/chapter4/07-ai-integration.md`

### Existing implementation reused

- `gateway/nginx.conf`
- `ai-service/app/routers/recommend.py`
- `ai-service/app/routers/chatbot.py`
- `ai-service/app/routers/behavior.py`
- `ai-service/app/services/recommend.py`
- `ai-service/app/services/chatbot.py`
- `ai-service/app/clients/product_client.py`
- `frontend/lib/ai.ts`
- `frontend/app/chatbot/page.tsx`

## 3. AI role in the full system

The AI subsystem already exists as an independent service and now participates in the Chapter 4 architecture through the gateway route family:

- `/api/ai/*`

This makes AI reachable in the same integration style as the rest of the system.

### 3.1 AI capabilities currently implemented

The AI service currently exposes:

- recommendation API
- chatbot API
- behavior tracking API
- graph APIs
- RAG maintenance API
- health API

For Chapter 4 system demonstration, the most relevant runtime capabilities are:

- recommendations grounded in the product catalog and user behavior context
- chatbot answers grounded in retrieved product context

## 4. Gateway exposure

### 4.1 Public AI route path

The gateway exposes AI via:

- `/api/ai/recommend`
- `/api/ai/chatbot`
- `/api/ai/behavior`
- `/api/ai/graph/*`
- `/api/ai/rag/*`

### 4.2 Mapping strategy

`gateway/nginx.conf` maps:

- `/api/ai/*` -> `ai-service`

This means AI is now accessed through the same main backend entry point as the rest of the Chapter 4 system.

## 5. AI input data sources

### 5.1 Product data source

The AI service reads product catalog context from `product-service` through `ProductServiceClient`.

This affects:

- recommendation candidate construction
- RAG retrieval fallback and indexing
- chatbot grounded suggestions
- dataset export and evaluation artifacts

### 5.2 User behavior source

The AI service stores and reads behavior events in its own database.

This affects:

- popularity fallback scoring
- recommendation personalization
- sequence-model inputs
- graph-based relationship building

### 5.3 Graph and retrieval context

The AI service also uses:

- Neo4j for graph relations
- local AI artifacts for RAG and LSTM runtime support

This means the AI layer is not generating generic answers detached from the system; it is working from project-specific product and behavior context.

## 6. AI flow inside the system

### 6.1 Recommendation flow

Current recommendation flow:

1. client calls `/api/ai/recommend`
2. gateway routes request to `ai-service`
3. `ai-service` loads product context
4. `ai-service` combines available signals:
   - LSTM if available
   - graph recommendations if available
   - RAG query match if query exists
   - popularity fallback when needed
5. response returns real product payloads and scoring reasons

### 6.2 Chatbot flow

Current chatbot flow:

1. client calls `/api/ai/chatbot`
2. gateway routes request to `ai-service`
3. chatbot classifies the user query
4. RAG retrieval gets real catalog candidates
5. recommendation diagnostics may boost ranking if `user_id` is supplied
6. chatbot returns:
   - grounded answer
   - product suggestions
   - retrieved context

### 6.3 Behavior flow

Current behavior flow:

1. client calls `/api/ai/behavior`
2. `ai-service` stores the event
3. those events later influence recommendation and analytics pipelines

## 7. Frontend integration evidence

Frontend integration already exists:

- AI client utilities in `frontend/lib/ai.ts`
- chatbot UI in `frontend/app/chatbot/page.tsx`

Current frontend AI calls:

- `GET /api/ai/recommend`
- `POST /api/ai/chatbot`
- `POST /api/ai/behavior`

This is important evidence that the AI service is not only a backend experiment; it is wired into the user-facing application.

## 8. Demo script

### 8.1 Script path

- `scripts/ai_gateway_demo.ps1`

### 8.2 What it does

The script:

1. checks gateway health
2. sends a behavior event through `/api/ai/behavior`
3. requests recommendations through `/api/ai/recommend`
4. requests a chatbot response through `/api/ai/chatbot`
5. returns a compact JSON summary

### 8.3 Command to run

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\ai_gateway_demo.ps1
```

### 8.4 Save output as evidence

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\ai_gateway_demo.ps1 `
  -OutputPath .\docs\chapter4\evidence\ai-gateway-demo.json
```

### 8.5 Output fields

The script summary includes:

- `gateway_status`
- `behavior_event_id`
- `recommendation_user_id`
- `recommendation_query`
- `recommendation_total`
- `top_recommendation_product`
- `top_recommendation_category`
- `top_recommendation_score`
- `chatbot_query_type`
- `chatbot_top_product`
- `chatbot_top_product_category`
- `chatbot_context_count`

This is enough to prove that:

- AI is reachable through the gateway
- AI returns project-specific product outputs
- chatbot and recommendation outputs are linked to catalog context

## 9. Why this satisfies the Chapter 4 AI requirement

The master prompt requires AI to be part of the complete system. This phase satisfies that by showing:

- AI exists as an independent service
- AI is reachable through the system gateway
- AI reads real project product data
- AI can use user-linked context through `user_id`
- AI outputs are consumable by the frontend and demo scripts

Both required AI directions are effectively represented:

- recommendation
- chatbot

## 10. Relationship to the end-to-end system demo

The checkout E2E flow from Phase 6 covers the commerce path.

The AI demo from this phase complements it by covering the system intelligence path:

- product discovery assistance
- personalized or context-aware ranking
- grounded conversational advice

Together they demonstrate that Chapter 4 is not only a CRUD microservice stack, but a complete e-commerce system with an integrated AI capability.

## 11. If runtime verification is possible

Suggested evidence files:

- `docs/chapter4/evidence/ai-gateway-demo.json`
- `docs/chapter4/evidence/e2e-checkout-success.json`
- `docs/chapter4/evidence/e2e-checkout-payment-failure.json`

The same gateway-based environment can be used to generate both commerce and AI evidence.

## 12. Remaining gaps after Phase 7

- runtime evidence has not yet been generated in this turn
- no screenshot evidence has been captured yet
- AI routes are exposed and demoable, but full observability for AI calls is still limited until the observability phase

These are acceptable for now because the AI integration is real in code, routed through the gateway, and accompanied by a runnable script-based demo.
