# Implementation Context

This repository now uses a schema-driven product catalog instead of separate OneToOne detail tables for `Book`, `Electronics`, and `Fashion`.

## Product service

- Database: PostgreSQL
- Core models:
  - `Category`
  - `Product`
- `Product` fields:
  - `name`
  - `price`
  - `stock`
  - `category`
  - `detail_type`
  - `detail` (`JSONField`)

The product API now exposes one normalized contract for both public and internal consumers:

```json
{
  "id": 1,
  "name": "Hydrating Serum",
  "price": 27.0,
  "stock": 40,
  "category": 5,
  "category_data": { "id": 5, "name": "Beauty" },
  "detail_type": "beauty",
  "detail": {
    "brand": "GlowLab",
    "skin_type": "Dry",
    "volume_ml": 30
  }
}
```

## Supported product types

- `book`
- `electronics`
- `fashion`
- `home-living`
- `beauty`
- `sports`
- `toys`
- `grocery`
- `office`
- `pet-supplies`

Each `detail_type` is validated against a registry in `product-service/app/product_types.py`. That registry is the source of truth for:

- allowed type keys
- allowed detail fields
- field types
- required fields

## Frontend contract

- `frontend/types/index.ts` now models `Product.detail_type` and `Product.detail` directly.
- Product detail rendering is schema-driven.
- Admin product form is schema-driven.
- Catalog list keeps using base product fields and `category_data`.

## Cross-service compatibility

- `order-service` still relies only on base product fields such as `id`, `price`, and `stock`.
- `cart-service` continues to reference products only by `product_id`.
- No cross-service foreign keys are introduced.

## Seed behavior

`product-service` seed data now creates:

- 10 categories
- sample products for all 10 product types
- detail payloads that match the registry schema

The seed command is idempotent and updates existing seeded products by name.
