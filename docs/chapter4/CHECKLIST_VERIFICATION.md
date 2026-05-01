# Chapter 4 Checklist Verification

This document verifies Section 5 of the Chapter 4 master prompt against code, runtime behavior, logs, JSON outputs, and screenshots captured from the current repository state.

Verification rule used in this file:

- an item is checked only when there is enough evidence to reproduce or inspect it
- evidence links point to the actual code, docs, script, log, output, or screenshot used for verification
- limitations are recorded separately and do not silently invalidate checked items unless they directly break the checklist requirement

## 5.1 Functional and architecture checklist

- [x] There is a `gateway/` or equivalent API Gateway component.
Evidence: [gateway/README.md](/d:/CHAP2_E-COMMERCE/gateway/README.md), [gateway/Dockerfile](/d:/CHAP2_E-COMMERCE/gateway/Dockerfile), [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf)

- [x] There is a real working Nginx configuration file.
Evidence: [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf), [docs/chapter4/logs/compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt), [docs/chapter4/screenshots/gateway-health.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/gateway-health.png)

- [x] Gateway routes reach the main services.
Evidence: [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf), [docs/chapter4/evidence/health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json), [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json), [docs/chapter4/evidence/ai-gateway-demo.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/ai-gateway-demo.json)

- [x] The system clearly expresses a microservices architecture.
Evidence: [docs/chapter4/01-system-architecture.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/01-system-architecture.md), [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml), [docs/chapter4/logs/compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt)

- [x] Each service has a clear responsibility boundary.
Evidence: [docs/chapter4/01-system-architecture.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/01-system-architecture.md), [docs/chapter4/00-gap-analysis.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/00-gap-analysis.md)

- [x] There is no cross-service database access.
Evidence: [docs/chapter4/01-system-architecture.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/01-system-architecture.md), [order-service/app/service_clients.py](/d:/CHAP2_E-COMMERCE/order-service/app/service_clients.py), [ai-service/app/clients/product_client.py](/d:/CHAP2_E-COMMERCE/ai-service/app/clients/product_client.py), [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml)
Verification note: service-to-service interaction is implemented through HTTP clients and internal APIs, not direct database queries into another service's database.

- [x] There is service communication between business components.
Evidence: [order-service/app/service_clients.py](/d:/CHAP2_E-COMMERCE/order-service/app/service_clients.py), [docs/chapter4/04-service-communication.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/04-service-communication.md), [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json)

## 5.2 Security checklist

- [x] JWT auth works.
Evidence: [user-service/app/views.py](/d:/CHAP2_E-COMMERCE/user-service/app/views.py), [user-service/app/serializers.py](/d:/CHAP2_E-COMMERCE/user-service/app/serializers.py), [docs/chapter4/evidence/auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json)

- [x] Login returns a token.
Evidence: [docs/chapter4/evidence/auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json), [docs/chapter4/03-authentication-security.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/03-authentication-security.md)

- [x] Protected routes require a token.
Evidence: [docs/chapter4/evidence/auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json)
Verification note: unauthenticated `GET /api/cart/` returned `401`.

- [x] RBAC still works.
Evidence: [docs/chapter4/evidence/auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json), [docs/chapter4/03-authentication-security.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/03-authentication-security.md), [user-service/app/auth.py](/d:/CHAP2_E-COMMERCE/user-service/app/auth.py)
Verification note: customer token received `403` on admin user listing; admin token received `200`.

- [x] The gateway and/or services handle headers/auth appropriately.
Evidence: [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf), [docs/chapter4/03-authentication-security.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/03-authentication-security.md), [docs/chapter4/evidence/auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json)

## 5.3 Containerization checklist

- [x] Main services have Dockerfiles or an equivalent containerization strategy.
Evidence: [user-service/Dockerfile](/d:/CHAP2_E-COMMERCE/user-service/Dockerfile), [product-service/Dockerfile](/d:/CHAP2_E-COMMERCE/product-service/Dockerfile), [cart-service/Dockerfile](/d:/CHAP2_E-COMMERCE/cart-service/Dockerfile), [order-service/Dockerfile](/d:/CHAP2_E-COMMERCE/order-service/Dockerfile), [payment-service/Dockerfile](/d:/CHAP2_E-COMMERCE/payment-service/Dockerfile), [shipping-service/Dockerfile](/d:/CHAP2_E-COMMERCE/shipping-service/Dockerfile), [ai-service/Dockerfile](/d:/CHAP2_E-COMMERCE/ai-service/Dockerfile), [frontend/Dockerfile](/d:/CHAP2_E-COMMERCE/frontend/Dockerfile), [gateway/Dockerfile](/d:/CHAP2_E-COMMERCE/gateway/Dockerfile)

- [x] There is a `docker-compose.yml`.
Evidence: [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml)

- [x] Compose can build and run the system validly.
Evidence: [docs/chapter4/logs/compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt), [docs/chapter4/evidence/health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json)

- [x] Services run on the same network.
Evidence: [docs/chapter4/logs/network-inspect.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/network-inspect.json), [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml)

- [x] Environment variables are organized clearly.
Evidence: [.env.example](/d:/CHAP2_E-COMMERCE/.env.example), [user-service/.env.example](/d:/CHAP2_E-COMMERCE/user-service/.env.example), [product-service/.env.example](/d:/CHAP2_E-COMMERCE/product-service/.env.example), [cart-service/.env.example](/d:/CHAP2_E-COMMERCE/cart-service/.env.example), [order-service/.env.example](/d:/CHAP2_E-COMMERCE/order-service/.env.example), [payment-service/.env.example](/d:/CHAP2_E-COMMERCE/payment-service/.env.example), [shipping-service/.env.example](/d:/CHAP2_E-COMMERCE/shipping-service/.env.example), [ai-service/.env.example](/d:/CHAP2_E-COMMERCE/ai-service/.env.example)

## 5.4 Business flow checklist

- [x] There is a login -> browse product -> add cart -> create order -> payment -> shipping flow.
Evidence: [scripts/e2e_checkout_flow.ps1](/d:/CHAP2_E-COMMERCE/scripts/e2e_checkout_flow.ps1), [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json), [docs/chapter4/06-end-to-end-flow.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/06-end-to-end-flow.md)

- [x] Order can call payment.
Evidence: [order-service/app/service_clients.py](/d:/CHAP2_E-COMMERCE/order-service/app/service_clients.py), [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json), [docs/chapter4/evidence/e2e-checkout-payment-failure.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-payment-failure.json)

- [x] Payment success leads to shipping flow.
Evidence: [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json)
Verification note: successful checkout produced `payment_status=Success`, `order_status=Shipping`, and `shipping_status=Processing`.

- [x] Status is updated reasonably across services.
Evidence: [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json), [docs/chapter4/evidence/e2e-checkout-payment-failure.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-payment-failure.json)
Verification note: failure flow produced `payment_status=Failed` and `order_status=Cancelled`.

## 5.5 AI integration checklist

- [x] AI service exists as an independent service.
Evidence: [ai-service/app/main.py](/d:/CHAP2_E-COMMERCE/ai-service/app/main.py), [ai-service/Dockerfile](/d:/CHAP2_E-COMMERCE/ai-service/Dockerfile), [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml)

- [x] There is an AI route through the gateway or another clear architecture entry path.
Evidence: [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf), [docs/chapter4/screenshots/ai-recommend-api.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/ai-recommend-api.png), [docs/chapter4/07-ai-integration.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/07-ai-integration.md)

- [x] Recommendation or chatbot works.
Evidence: [docs/chapter4/evidence/ai-gateway-demo.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/ai-gateway-demo.json)
Verification note: the demo returned both recommendation results and chatbot-grounded output.

- [x] AI service is usable in an end-to-end demo.
Evidence: [scripts/ai_gateway_demo.ps1](/d:/CHAP2_E-COMMERCE/scripts/ai_gateway_demo.ps1), [docs/chapter4/evidence/ai-gateway-demo.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/ai-gateway-demo.json)

## 5.6 Observability checklist

- [x] There is basic logging for the gateway.
Evidence: [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf), [docs/chapter4/logs/runtime-logs.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/runtime-logs.txt)

- [x] There is basic logging for the main services.
Evidence: [user-service/config/settings.py](/d:/CHAP2_E-COMMERCE/user-service/config/settings.py), [product-service/config/settings.py](/d:/CHAP2_E-COMMERCE/product-service/config/settings.py), [cart-service/config/settings.py](/d:/CHAP2_E-COMMERCE/cart-service/config/settings.py), [order-service/config/settings.py](/d:/CHAP2_E-COMMERCE/order-service/config/settings.py), [payment-service/config/settings.py](/d:/CHAP2_E-COMMERCE/payment-service/config/settings.py), [shipping-service/config/settings.py](/d:/CHAP2_E-COMMERCE/shipping-service/config/settings.py), [ai-service/app/main.py](/d:/CHAP2_E-COMMERCE/ai-service/app/main.py), [docs/chapter4/logs/runtime-logs.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/runtime-logs.txt)

- [x] There is a health check or status endpoint.
Evidence: [docs/chapter4/evidence/health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json), [scripts/health_check.ps1](/d:/CHAP2_E-COMMERCE/scripts/health_check.ps1)

- [x] There is at least a skeleton structure for monitoring if there is no full stack.
Evidence: [infrastructure/monitoring/prometheus.yml](/d:/CHAP2_E-COMMERCE/infrastructure/monitoring/prometheus.yml), [infrastructure/monitoring/README.md](/d:/CHAP2_E-COMMERCE/infrastructure/monitoring/README.md), [docs/chapter4/08-observability.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/08-observability.md)

## 5.7 Evidence checklist

- [x] There is markdown documentation summarizing the result.
Evidence: [docs/chapter4/00-gap-analysis.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/00-gap-analysis.md), [docs/chapter4/01-system-architecture.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/01-system-architecture.md), [docs/chapter4/02-api-gateway.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/02-api-gateway.md), [docs/chapter4/03-authentication-security.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/03-authentication-security.md), [docs/chapter4/04-service-communication.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/04-service-communication.md), [docs/chapter4/05-docker-deployment.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/05-docker-deployment.md), [docs/chapter4/06-end-to-end-flow.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/06-end-to-end-flow.md), [docs/chapter4/07-ai-integration.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/07-ai-integration.md), [docs/chapter4/08-observability.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/08-observability.md), [docs/chapter4/09-system-evaluation.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/09-system-evaluation.md)

- [x] There are instructions for running the system.
Evidence: [docs/chapter4/05-docker-deployment.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/05-docker-deployment.md), [README.md](/d:/CHAP2_E-COMMERCE/README.md)

- [x] There is test evidence for the flow.
Evidence: [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json), [docs/chapter4/evidence/e2e-checkout-payment-failure.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-payment-failure.json), [docs/chapter4/evidence/auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json), [docs/chapter4/evidence/ai-gateway-demo.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/ai-gateway-demo.json), [docs/chapter4/evidence/health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json), [docs/chapter4/evidence/basic-system-eval.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/basic-system-eval.json)

- [x] There is output/log/screenshot evidence for important parts.
Evidence: [docs/chapter4/logs/compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt), [docs/chapter4/logs/network-inspect.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/network-inspect.json), [docs/chapter4/logs/runtime-logs.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/runtime-logs.txt), [docs/chapter4/screenshots/storefront-home.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/storefront-home.png), [docs/chapter4/screenshots/gateway-health.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/gateway-health.png), [docs/chapter4/screenshots/ai-recommend-api.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/ai-recommend-api.png)

- [x] There is mapping from Chapter 4 requirements to the corresponding code files and deliverables.
Evidence: this file and [docs/chapter4/09-system-evaluation.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/09-system-evaluation.md)

## Requirement to deliverable mapping

| Chapter 4 requirement | Primary code/config | Primary document | Runtime evidence |
| --- | --- | --- | --- |
| System architecture | [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml) | [01-system-architecture.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/01-system-architecture.md) | [compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt) |
| API Gateway | [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf) | [02-api-gateway.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/02-api-gateway.md) | [health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json) |
| JWT and RBAC | [user-service/app/views.py](/d:/CHAP2_E-COMMERCE/user-service/app/views.py), [user-service/app/serializers.py](/d:/CHAP2_E-COMMERCE/user-service/app/serializers.py) | [03-authentication-security.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/03-authentication-security.md) | [auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json) |
| Service communication | [order-service/app/service_clients.py](/d:/CHAP2_E-COMMERCE/order-service/app/service_clients.py), [ai-service/app/clients/product_client.py](/d:/CHAP2_E-COMMERCE/ai-service/app/clients/product_client.py) | [04-service-communication.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/04-service-communication.md) | [e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json) |
| Docker deployment | [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml), [.env.example](/d:/CHAP2_E-COMMERCE/.env.example) | [05-docker-deployment.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/05-docker-deployment.md) | [compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt), [network-inspect.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/network-inspect.json) |
| End-to-end checkout | [scripts/e2e_checkout_flow.ps1](/d:/CHAP2_E-COMMERCE/scripts/e2e_checkout_flow.ps1) | [06-end-to-end-flow.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/06-end-to-end-flow.md) | [e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json), [e2e-checkout-payment-failure.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-payment-failure.json) |
| AI integration | [scripts/ai_gateway_demo.ps1](/d:/CHAP2_E-COMMERCE/scripts/ai_gateway_demo.ps1), [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf) | [07-ai-integration.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/07-ai-integration.md) | [ai-gateway-demo.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/ai-gateway-demo.json), [ai-recommend-api.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/ai-recommend-api.png) |
| Observability | [gateway/nginx.conf](/d:/CHAP2_E-COMMERCE/gateway/nginx.conf), [infrastructure/monitoring/prometheus.yml](/d:/CHAP2_E-COMMERCE/infrastructure/monitoring/prometheus.yml) | [08-observability.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/08-observability.md) | [health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json), [runtime-logs.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/runtime-logs.txt) |
| System evaluation | [scripts/basic_system_eval.ps1](/d:/CHAP2_E-COMMERCE/scripts/basic_system_eval.ps1) | [09-system-evaluation.md](/d:/CHAP2_E-COMMERCE/docs/chapter4/09-system-evaluation.md) | [basic-system-eval.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/basic-system-eval.json) |

## Recorded limitations

- Frontend `Orders` page currently shows `Failed to fetch orders` during browser verification, even though the gateway-backed order APIs and the end-to-end checkout script pass. This is recorded as a runtime UI issue to fix before any final polish phase, but it does not invalidate the checklist items above because the Chapter 4 requirements are currently satisfied through the verified service and gateway flows.
