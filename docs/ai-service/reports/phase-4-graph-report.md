# Phase 4 Graph Report

## Graph model

- Node types: `User`, `Product`
- Edge types: `VIEW`, `CLICK`, `ADD_TO_CART`, `BUY`, `SIMILAR`
- Source data: product snapshot + persisted behavior events

## SIMILAR construction

`SIMILAR` is built by combining:

- same category
- same `detail_type`
- close price band
- keyword overlap from product text fields

## APIs

- `POST /graph/sync`
- `GET /graph/recommend?user_id=...`

## Recommendation behavior

- Primary path: traverse user interaction history into similar and co-connected products.
- Fallback path: graph popularity when user edges are too sparse.

## Evidence

- `docs/ai-service/artifacts/plots/phase-4-node-edge-counts.png`
- `docs/ai-service/artifacts/plots/phase-4-degree-distribution.png`
- `docs/ai-service/artifacts/plots/phase-4-relationship-distribution.png`
