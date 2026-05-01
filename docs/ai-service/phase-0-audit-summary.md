# Phase 0 Audit Summary

## 1. Current repository summary

`CHAP2_E-COMMERCE` is a microservices monorepo with:

- 6 Django REST Framework backend services
- 1 Next.js 14 frontend
- Docker Compose orchestration
- JWT-based auth through `user-service`
- internal JWT calls between services, especially from `order-service`
- schema-driven `product-service` using `detail_type` and `detail`

## 2. Service inventory

| Service | Stack | DB | Primary responsibility | Existing AI-relevant signals |
| --- | --- | --- | --- | --- |
| `product-service` | Django + DRF | PostgreSQL | Categories, products, product detail payloads | Product catalog, category, detail_type, detail metadata |
| `user-service` | Django + DRF | MySQL | Register, login, users, roles | User identity and role |
| `cart-service` | Django + DRF | MySQL | Cart and cart item management | Add-to-cart events can be emitted here or from frontend |
| `order-service` | Django + DRF | MySQL | Checkout and order orchestration | Successful purchases, order completion |
| `payment-service` | Django + DRF | MySQL | Payment processing | Payment completion status |
| `shipping-service` | Django + DRF | MySQL | Shipping lifecycle | Not primary for recommendation |
| `frontend` | Next.js 14 | N/A | Catalog, auth, cart, checkout, admin dashboards | View, click, search, add_to_cart, buy interaction capture point |

## 3. Existing integration shape

### Backend

- Services are isolated and database-independent.
- Cross-service references use logical IDs, not foreign keys.
- `order-service` is the main orchestrator for checkout.
- `product-service` already exposes a normalized product API useful for AI ingestion.

### Frontend

- The frontend calls only `/api/[...path]`.
- The internal Next.js proxy maps route prefixes to backend services.
- This proxy is the correct low-risk integration point for `/api/ai/*` later.

## 4. Existing product contract relevant to AI

The current product response shape is already suitable for AI retrieval/document creation:

```json
{
  "id": 10,
  "name": "Organic Granola",
  "price": 8.5,
  "stock": 60,
  "category": 9,
  "category_data": {
    "id": 9,
    "name": "Grocery"
  },
  "detail_type": "grocery",
  "detail": {
    "organic": true,
    "expiry_days": 180,
    "weight_grams": 500
  }
}
```

This reduces AI ingestion complexity significantly because:

- no per-type serializer branching is needed
- `detail_type` can act as a taxonomy feature
- `detail` can be converted to searchable product documents

## 5. Key integration points for AI Service

| Area | Current source | Planned AI use |
| --- | --- | --- |
| Product catalog | `product-service` public/internal API | RAG documents, graph product nodes, metadata features |
| User identity | JWT and `user-service` | attach behavior to `user_id`, personalize recommendations |
| Product detail page | `frontend/app/products/[id]/page.tsx` | emit `view` events |
| Product card/list interactions | `frontend/app/page.tsx`, `frontend/components/product-card.tsx` | emit `click` events |
| Cart actions | product detail and cart flows | emit `add_to_cart` |
| Checkout success | frontend checkout or `order-service` confirmation | emit `buy` |
| Search | currently missing dedicated search UI | future source for `search` events |

## 6. Audit findings

### Strengths

- The monorepo already has good service separation.
- Docker Compose is established and can host `ai-service`, `ai-db`, and `neo4j`.
- Product catalog is normalized and AI-friendly.
- Frontend proxy pattern reduces AI integration risk.

### Gaps relative to Chapter 3

- No `ai-service` exists yet.
- No behavior-tracking persistence exists.
- No search event model exists in current UI.
- No graph database is present.
- No vector index or retrieval layer is present.
- No ML training pipeline or model artifact workflow exists.
- No AI-specific artifact/report folder exists until this phase.

## 7. Files most likely to be changed in later phases

### New paths

- `ai-service/`
- `docs/ai-service/`

### Existing files likely to change

- [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml)
- [frontend/app/api/[...path]/route.ts](/d:/CHAP2_E-COMMERCE/frontend/app/api/[...path]/route.ts)
- [frontend/app/page.tsx](/d:/CHAP2_E-COMMERCE/frontend/app/page.tsx)
- [frontend/app/products/[id]/page.tsx](/d:/CHAP2_E-COMMERCE/frontend/app/products/[id]/page.tsx)
- [frontend/app/cart/page.tsx](/d:/CHAP2_E-COMMERCE/frontend/app/cart/page.tsx)
- [frontend/app/checkout/page.tsx](/d:/CHAP2_E-COMMERCE/frontend/app/checkout/page.tsx)
- [README.md](/d:/CHAP2_E-COMMERCE/README.md)

### Existing files that should remain minimally touched

- service business logic in `cart-service`, `payment-service`, `shipping-service`
- `product-service` public contract
- `order-service` checkout flow except for minimal event integration if required

## 8. Phase 0 output

Phase 0 has produced:

- audit summary
- phase roadmap
- architecture design docs
- pipeline design docs
- draft API contract
- artifact manifest
- dependency and touchpoint tables

No runtime AI component is implemented in this phase.
