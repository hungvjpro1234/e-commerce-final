# Chapter 4 Phase 4 Service Communication

## 1. Purpose

This phase standardizes service-to-service communication according to the Chapter 4 master prompt. The goal is to make the communication model explicit, keep the existing orchestration working, and add minimum best-practice hardening for:

- timeout control
- retry strategy at a reasonable level
- clearer error handling
- communication logging
- environment-based endpoint configuration

The implementation remains intentionally pragmatic. The project does not introduce a full message broker or circuit breaker layer in this phase.

## 2. Deliverables

### Files added

- `docs/chapter4/04-service-communication.md`

### Files updated

- `order-service/app/service_clients.py`
- `order-service/config/settings.py`
- `order-service/.env.example`
- `ai-service/app/config.py`
- `ai-service/.env.example`
- `ai-service/app/clients/product_client.py`

## 3. Current communication model

### 3.1 Synchronous communication in the business flow

The checkout pipeline currently uses synchronous REST calls orchestrated by `order-service`.

Flow:

1. `order-service` fetches cart content from `cart-service`
2. `order-service` validates product data against `product-service`
3. `order-service` creates payment in `payment-service`
4. `order-service` creates shipment in `shipping-service`
5. `order-service` clears the cart in `cart-service`

This is the main Chapter 4 business communication path.

### 3.2 AI integration communication

The AI subsystem currently communicates primarily with `product-service`.

Current behavior:

- `ai-service` reads product catalog data through `ProductServiceClient`
- recommendation, RAG, dataset generation, and chatbot flows all depend on product catalog context
- `ORDER_SERVICE_URL` is already configured in `ai-service`, but in the current codebase it is not yet the main synchronous dependency in the core request path

This means AI integration is real and connected to the system, but the strongest active runtime dependency today is `ai-service -> product-service`.

## 4. Hardening implemented in this phase

### 4.1 `order-service` request wrapper

`order-service/app/service_clients.py` now uses a shared `_send_request(...)` helper instead of open-coded calls.

Benefits:

- common timeout handling
- common retry behavior
- common logging
- common error translation to `ServiceClientError`

### 4.2 Retry policy

The retry strategy is intentionally selective.

#### Retried operations

- `GET /internal/cart/<user_id>/`
- `GET /internal/products/<product_id>/`
- `DELETE /internal/cart/<user_id>/clear`

These operations are read-only or effectively idempotent in the current design, so limited retry is acceptable.

#### Non-retried operations

- `POST /internal/payment/pay`
- `POST /internal/shipping/create`

These are not retried automatically because duplicate POST submission could create duplicate payment or shipment records. In this project phase, avoiding duplicate side effects is more important than aggressive automatic recovery.

### 4.3 Timeout policy

`order-service` now reads timeout and retry settings from environment variables:

- `SERVICE_CLIENT_TIMEOUT_SECONDS`
- `SERVICE_CLIENT_GET_RETRIES`
- `SERVICE_CLIENT_DELETE_RETRIES`

This keeps the communication layer configurable without code edits.

### 4.4 Logging

`order-service` client calls now log:

- start of the downstream call
- success of the downstream call
- retryable connection or timeout errors
- non-retryable request exceptions

This improves debugging and evidence collection for later phases.

### 4.5 AI product client hardening

`ai-service/app/clients/product_client.py` now includes:

- retry attempts for transient network failures
- logging for start, success, and retryable failure
- environment-based retry configuration through `PRODUCT_SERVICE_MAX_RETRIES`

This is the main AI-side communication hardening required by the prompt.

## 5. Environment-based endpoint and retry configuration

### 5.1 `order-service`

Relevant configuration:

- `CART_SERVICE_URL`
- `PRODUCT_SERVICE_URL`
- `PAYMENT_SERVICE_URL`
- `SHIPPING_SERVICE_URL`
- `SERVICE_CLIENT_TIMEOUT_SECONDS`
- `SERVICE_CLIENT_GET_RETRIES`
- `SERVICE_CLIENT_DELETE_RETRIES`

### 5.2 `ai-service`

Relevant configuration:

- `PRODUCT_SERVICE_URL`
- `PRODUCT_SERVICE_TIMEOUT_SECONDS`
- `PRODUCT_SERVICE_MAX_RETRIES`
- `ORDER_SERVICE_URL`

This satisfies the prompt requirement that service endpoint configuration should be environment-driven.

## 6. Order to payment communication

### 6.1 Implementation path

The order-to-payment call is implemented in:

- caller: `order-service/app/views.py`
- client wrapper: `order-service/app/service_clients.py`
- receiver route: `payment-service/app/urls.py`
- receiver handler: `payment-service/app/views.py`

### 6.2 Runtime sequence

1. `OrderListCreateView.create(...)` finishes cart and product validation
2. `create_payment(...)` sends `POST /internal/payment/pay`
3. request includes:
   - internal bearer token
   - `X-Correlation-ID`
   - order payload with `order_id`, `user_id`, `amount`, `simulate_failure`
4. `payment-service` persists the payment record
5. result is returned to `order-service`
6. `order-service` updates order status based on the payment result

### 6.3 Error handling

- downstream HTTP errors are converted into `ServiceClientError`
- orchestration returns `502 Bad Gateway`
- payment failure business result is handled separately as a valid application outcome with status `402`

## 7. Payment and shipping relationship

The system currently uses orchestration, not direct service-to-service chaining between payment and shipping.

Actual model:

- `payment-service` does not call `shipping-service`
- `order-service` calls `payment-service`
- if payment returns success, `order-service` then calls `shipping-service`

This is an important Chapter 4 clarification because the business dependency exists, but the technical dependency is mediated by `order-service`.

Sequence:

1. payment success is returned to `order-service`
2. `order-service` updates the order to `Paid`
3. `order-service` calls `shipping-service`
4. shipment creation result may advance order status to `Shipping`

## 8. AI service data dependencies

### 8.1 Data read by AI service

The AI service currently reads or uses:

- product catalog data from `product-service`
- behavior event data from its own database
- graph structure from Neo4j
- generated model artifacts from local AI artifact storage

### 8.2 Communication patterns by AI feature

| AI capability | External dependency | Pattern |
| --- | --- | --- |
| catalog sync | `product-service` | synchronous REST |
| RAG retrieval bootstrap | `product-service` or snapshot artifacts | synchronous REST or local artifact fallback |
| recommendation | product catalog + behavior DB + graph store | mixed local + synchronous product fetch |
| chatbot | RAG retrieval + recommendation diagnostics | internal service composition plus product-derived context |

### 8.3 Current limitation

Although `ORDER_SERVICE_URL` exists in config, the primary live dependency in active request flows is still `product-service`. This is acceptable for the current phase, but should be described honestly in Chapter 4 evidence.

## 9. Synchronous versus asynchronous design

### 9.1 What is implemented now

The current project uses synchronous HTTP calls for the business-critical integration paths.

Implemented:

- synchronous REST between `order-service` and other business services
- synchronous REST between `ai-service` and `product-service`

### 9.2 What is not implemented now

Not implemented in this phase:

- event bus
- queue-based orchestration
- circuit breaker
- saga coordinator beyond application-layer orchestration in `order-service`

This is within scope for a course project, as long as the limitation is made explicit.

## 10. Health-check status relative to communication

The master prompt suggests health endpoints as a recommended improvement. In the current repository state:

- `ai-service` already has `/health`
- business services still rely on startup checks and direct runtime communication
- unified health endpoints for all Django services are not implemented yet in this phase

This remains a known gap to be addressed later under observability.

## 11. Best-practice assessment against the prompt

| Prompt expectation | Current status | Notes |
| --- | --- | --- |
| synchronous REST calls | achieved | active in checkout and AI catalog access |
| timeout | achieved | explicit in `order-service` and `ai-service` clients |
| retry | partially achieved | added only where low risk of duplicate side effects |
| error handling | achieved at MVP level | request failures mapped to service-level exceptions |
| logging for service calls | improved and achieved at MVP level | explicit logs now exist in client wrappers |
| common request helper | achieved for `order-service` | shared `_send_request(...)` wrapper |
| endpoint config through env | achieved | URLs and retry/timeout settings are env-driven |
| health checks | partial | AI has it; business services still pending |

## 12. How to test communication behavior

### 12.1 Checkout path

Use the existing checkout smoke test:

- `docs/secure-flow-smoke-test.ps1`

This verifies the cross-service orchestration path.

### 12.2 Failure behavior

To validate non-happy-path orchestration:

- run the smoke test with simulated payment failure
- stop one downstream dependency and verify `502` propagation

### 12.3 AI catalog communication

Sanity checks:

```bash
curl http://localhost:8007/recommend?user_id=1&query=budget%20laptop&limit=5
curl -X POST http://localhost:8007/chatbot -H "Content-Type: application/json" -d "{\"user_id\":1,\"message\":\"toi can laptop gia re\"}"
```

These requests prove that AI flows can resolve product-derived context through the current communication layer.

## 13. Phase 4 conclusion

This phase keeps the existing architecture intact while bringing service communication closer to Chapter 4 expectations:

- request wrapper added for `order-service`
- retry policy made explicit and safe
- timeout and retry settings moved into environment configuration
- communication logs added
- AI product client hardened
- orchestration relationships documented honestly

The system still does not implement asynchronous messaging or circuit breakers, but the current level is appropriate for the project scope and now clearly evidenced in code and documentation.
