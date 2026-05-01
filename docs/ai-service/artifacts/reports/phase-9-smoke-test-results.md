# Phase 9 Smoke Test Results

## Scope

- frontend proxy `/api/ai/*`
- recommendation block on homepage
- chatbot page `/chatbot`
- behavior tracking for `search`, `click`, `view`, `add_to_cart`, `buy`

## Commands and checks

| Check | Result | Notes |
| --- | --- | --- |
| `npm run build` in `frontend/` | Pass | Next.js production build succeeded; only existing `img` optimization warnings remained |
| `docker compose up -d --build ai-service frontend` | Pass | Rebuilt runtime stack with frontend AI integration and `phase-9` health marker |
| `GET http://localhost:8007/health` | Pass | Returned `version: phase-9` |
| Focused pytest in `ai-service` | Pass | `9 passed` for `test_health`, `test_behavior`, `test_recommend_service`, `test_chatbot_service` |

## Browser verification

Environment:
- frontend: `http://localhost:3000`
- ai-service: `http://localhost:8007`
- verified on April 30, 2026

Observed requests from Chrome DevTools:

| Flow | Request | Result |
| --- | --- | --- |
| Homepage recommendation load | `GET /api/ai/recommend?user_id=15&limit=4` | `200` |
| Search refresh | `POST /api/ai/behavior` then `GET /api/ai/recommend?...&query=...` | `201`, `200` |
| Chatbot | `POST /api/ai/chatbot` | `200` |
| Product detail open | `POST /api/ai/behavior` with `click`, then `view` | `201`, `201` |
| Add to cart | `POST /api/cart/add`, then `POST /api/ai/behavior` with `add_to_cart` | `201`, `201` |
| Checkout success | `POST /api/orders`, then `POST /api/ai/behavior` with `buy` | `201`, `201` |

Behavior history evidence:

- `GET /behavior/user/15` returned `10` tracked events.
- Confirmed actions included `search`, `click`, `view`, `add_to_cart`, and `buy`.

## Screenshots

- [recommendation-ui.png](/d:/CHAP2_E-COMMERCE/docs/ai-service/screenshots/recommendation-ui.png)
- [chatbot-ui.png](/d:/CHAP2_E-COMMERCE/docs/ai-service/screenshots/chatbot-ui.png)
- [behavior-tracking-demo.png](/d:/CHAP2_E-COMMERCE/docs/ai-service/screenshots/behavior-tracking-demo.png)
