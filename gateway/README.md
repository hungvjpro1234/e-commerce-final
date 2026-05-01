# Gateway Component

This directory is reserved for the Chapter 4 API Gateway implementation.

## Role in the system

The gateway is the canonical backend entry point for the microservices architecture. It exists to make the system legible and testable as a complete Chapter 4 deployment, instead of relying on the frontend proxy as the de facto integration layer.

Target responsibilities:

- expose a single public API entry point
- route requests to the correct downstream service
- preserve `Authorization` and forwarding headers
- centralize basic security headers
- centralize access and error logging
- keep internal orchestration routes non-public

## Planned public route prefixes

- `/api/users/*`
- `/api/products/*`
- `/api/cart/*`
- `/api/orders/*`
- `/api/payments/*`
- `/api/shipping/*`
- `/api/ai/*`

## Planned internal route policy

These routes must remain private to service-to-service communication:

- `product-service`: `/internal/products/*`
- `cart-service`: `/internal/cart/*`
- `payment-service`: `/internal/payment/*`
- `shipping-service`: `/internal/shipping/*`

## Next implementation step

Phase 2 will add:

- `gateway/nginx.conf`
- concrete upstream mapping
- gateway logging and security-header configuration
- gateway integration into Docker Compose
