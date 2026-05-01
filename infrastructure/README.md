# Infrastructure Component

This directory groups deployment-oriented artifacts for the Chapter 4 system view.

## Scope

At the current stage, the authoritative runtime definition is still the repository root [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml). This directory is introduced in Phase 1 to make the deployment boundary explicit and to provide a stable home for future infrastructure files without moving working runtime assets prematurely.

Expected future contents may include:

- gateway-related deployment notes
- compose variants or overrides if needed
- monitoring configuration
- health-check or smoke-test helpers
- environment templates or deployment manifests

## Current deployment topology

The current compose stack already contains:

- business services:
  - `user-service`
  - `product-service`
  - `cart-service`
  - `order-service`
  - `payment-service`
  - `shipping-service`
  - `ai-service`
- frontend:
  - `frontend`
- databases and dependencies:
  - `user-db`
  - `product-db`
  - `cart-db`
  - `order-db`
  - `payment-db`
  - `shipping-db`
  - `ai-db`
  - `neo4j`

## Architecture note

This directory is intentionally lightweight in Phase 1. The goal is to normalize repository structure without disrupting the already working compose setup. Concrete infrastructure configuration will be added incrementally in later phases where those artifacts become executable and verifiable.
