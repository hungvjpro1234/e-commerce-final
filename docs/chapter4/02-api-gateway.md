# Chapter 4 Phase 2 API Gateway

## 1. Purpose

This phase introduces the dedicated API gateway layer required by Chapter 4. The implementation is based on Nginx and is designed to become the primary backend entry point for the microservices system.

The gateway is intentionally aligned with the existing codebase instead of forcing disruptive route rewrites. It therefore supports:

- a canonical Chapter 4 route contract
- header forwarding for authentication and traceability
- explicit blocking of internal-only orchestration routes
- compatibility aliases for the current frontend integration pattern

## 2. Deliverables

### Files added

- `gateway/nginx.conf`
- `gateway/Dockerfile`
- `docs/chapter4/02-api-gateway.md`

### Primary evidence

- `gateway/nginx.conf`
- `gateway/Dockerfile`

## 3. Gateway role in the architecture

The gateway sits between external clients and the backend services. Its responsibilities in this project are:

- expose a single backend ingress point
- map stable public route prefixes to the correct service
- forward JWT bearer tokens to downstream services
- preserve or generate `X-Correlation-ID`
- attach basic security headers
- produce access and error logs
- prevent public access to internal orchestration endpoints

The gateway does not perform JWT signature validation itself in this phase. The selected strategy is JWT header passthrough plus downstream validation, because the current services already implement JWT validation and RBAC in code.

## 4. Route map

### 4.1 Canonical Chapter 4 routes

| Public gateway route | Downstream service | Rewritten backend route |
| --- | --- | --- |
| `/api/users/auth/*` | `user-service` | `/auth/*` |
| `/api/users/*` | `user-service` | `/*` |
| `/api/products/*` | `product-service` | `/*` |
| `/api/cart/*` | `cart-service` | `/cart/*` |
| `/api/orders/*` | `order-service` | `/orders/*` |
| `/api/payments/*` | `payment-service` | `/payment/*` |
| `/api/shipping/*` | `shipping-service` | `/shipping/*` |
| `/api/ai/*` | `ai-service` | `/*` |

### 4.2 Compatibility aliases

To avoid breaking the currently implemented frontend transition path, the gateway also supports compatibility aliases:

| Compatibility route | Downstream service | Rewritten backend route |
| --- | --- | --- |
| `/api/auth/*` | `user-service` | `/auth/*` |
| `/api/categories/*` | `product-service` | `/categories/*` |
| `/api/payment/*` | `payment-service` | `/payment/*` |

These aliases allow the repository to move toward the dedicated gateway without requiring an immediate full rewrite of client-side API conventions.

## 5. Internal route protection

The following route families are intentionally blocked from public access through the gateway:

- `/api/products/internal/*`
- `/api/cart/internal/*`
- `/api/orders/internal/*`
- `/api/payments/internal/*`
- `/api/shipping/internal/*`
- `/api/ai/internal/*`

Behavior:

- gateway returns `403`
- response body explains that internal routes are not publicly accessible

This is important because current internal endpoints are designed only for service-to-service orchestration, mainly by `order-service`.

## 6. Proxy and forwarding strategy

### 6.1 Forwarded headers

The gateway forwards:

- `Host`
- `X-Real-IP`
- `X-Forwarded-For`
- `X-Forwarded-Proto`
- `X-Correlation-ID`
- `Authorization`

### 6.2 Correlation ID strategy

If the client sends `X-Correlation-ID`, the gateway forwards it unchanged.

If the client does not send one, the gateway generates a fallback value using Nginx `$request_id` and forwards that value downstream as `X-Correlation-ID`.

This matches the current order orchestration pattern, where correlation IDs are already meaningful in logs.

### 6.3 JWT header flow

Authentication strategy in this phase:

1. client logs in through `user-service`
2. client receives JWT token
3. client sends bearer token to gateway
4. gateway forwards the `Authorization` header unchanged
5. downstream services validate JWT and enforce RBAC

This preserves the current trust model and avoids duplicating authentication logic in the gateway.

## 7. Security headers and basic hardening

The current Nginx configuration adds:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `X-XSS-Protection: 1; mode=block`

It also enables:

- `server_tokens off`
- `client_max_body_size 10m`
- proxy connect timeout `5s`
- proxy read/send timeout `60s`
- disabled response buffering for simpler API behavior

This is sufficient for the project phase while leaving room for later additions such as rate limiting or explicit CORS handling if required.

## 8. Logging strategy

The gateway now defines:

- access log: `/var/log/nginx/access.log`
- error log: `/var/log/nginx/error.log`

The access log format includes:

- request metadata
- upstream address
- upstream status
- request time
- upstream response time
- correlation ID

This is the minimum logging structure needed for Chapter 4 evidence and later troubleshooting.

## 9. Health endpoint

The gateway exposes:

- `GET /health`

Current response:

```json
{"service":"gateway","status":"ok"}
```

This endpoint verifies the gateway container itself, not the health of all downstream services.

## 10. How to test the gateway

Once the gateway container is wired into Docker Compose in a later phase, the following checks should be used.

### 10.1 Gateway health

```bash
curl http://localhost/health
```

### 10.2 Login through gateway

```bash
curl -X POST http://localhost/api/users/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"customer\",\"password\":\"password123\"}"
```

### 10.3 Public product access through gateway

```bash
curl http://localhost/api/products/products
```

### 10.4 Cart access through gateway with JWT

```bash
curl http://localhost/api/cart/ \
  -H "Authorization: Bearer <token>"
```

### 10.5 Internal route should be blocked

```bash
curl http://localhost/api/payments/internal/payment/pay
```

Expected result: HTTP `403`.

## 11. Phase 2 assessment

### Chapter 4 criteria addressed

- dedicated `gateway/` component now contains real executable configuration
- Nginx route mapping is defined for all primary services
- forwarding headers and JWT passthrough strategy are explicit
- gateway logging strategy now exists
- basic security headers now exist
- internal route exposure policy is defined in code

### Remaining gaps after Phase 2

- gateway has not yet been wired into `docker-compose.yml`
- frontend is not yet switched to use the Nginx gateway as the main backend ingress
- no runtime logs or screenshots have been collected yet
- no gateway-specific smoke test script exists yet

These items will be addressed in later phases, especially the Docker and end-to-end phases.
