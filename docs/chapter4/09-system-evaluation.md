# Chapter 4 Phase 9 System Evaluation

## 1. Purpose

This phase evaluates the implemented Chapter 4 system using reproducible project-level measurements and runtime evidence. The goal is not to claim production benchmarking. The goal is to provide honest, inspectable numbers and architectural conclusions for the current Docker Compose deployment.

## 2. Evaluation scope

The following areas were evaluated:

- gateway reachability and baseline response time
- product catalog read path through the gateway
- AI recommendation path through the gateway
- end-to-end checkout behavior across order, payment, and shipping
- authentication and RBAC behavior through the gateway
- container runtime health and network topology

## 3. Evaluation artifacts

### Scripts

- [scripts/basic_system_eval.ps1](/d:/CHAP2_E-COMMERCE/scripts/basic_system_eval.ps1)
- [scripts/e2e_checkout_flow.ps1](/d:/CHAP2_E-COMMERCE/scripts/e2e_checkout_flow.ps1)
- [scripts/ai_gateway_demo.ps1](/d:/CHAP2_E-COMMERCE/scripts/ai_gateway_demo.ps1)
- [scripts/health_check.ps1](/d:/CHAP2_E-COMMERCE/scripts/health_check.ps1)
- [scripts/auth_rbac_check.ps1](/d:/CHAP2_E-COMMERCE/scripts/auth_rbac_check.ps1)

### JSON evidence

- [docs/chapter4/evidence/basic-system-eval.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/basic-system-eval.json)
- [docs/chapter4/evidence/e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json)
- [docs/chapter4/evidence/e2e-checkout-payment-failure.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-payment-failure.json)
- [docs/chapter4/evidence/ai-gateway-demo.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/ai-gateway-demo.json)
- [docs/chapter4/evidence/health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json)
- [docs/chapter4/evidence/auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json)

### Logs and screenshots

- [docs/chapter4/logs/compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt)
- [docs/chapter4/logs/network-inspect.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/network-inspect.json)
- [docs/chapter4/logs/runtime-logs.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/runtime-logs.txt)
- [docs/chapter4/screenshots/storefront-home.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/storefront-home.png)
- [docs/chapter4/screenshots/gateway-health.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/gateway-health.png)
- [docs/chapter4/screenshots/ai-recommend-api.png](/d:/CHAP2_E-COMMERCE/docs/chapter4/screenshots/ai-recommend-api.png)

## 4. Response time and lightweight throughput

Measurements below come from 12 single-client iterations against the running Compose stack.

| Path | Average | P95 | Approx. single-client RPS | Evidence |
| --- | --- | --- | --- | --- |
| `GET /health` via gateway | `10.31 ms` | `114.79 ms` | `96.99` | [basic-system-eval.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/basic-system-eval.json) |
| `GET /api/products/products` via gateway | `13.78 ms` | `19.62 ms` | `72.57` | [basic-system-eval.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/basic-system-eval.json) |
| `GET /api/ai/recommend` via gateway | `75.57 ms` | `134.32 ms` | `13.23` | [basic-system-eval.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/basic-system-eval.json) |

Interpretation:

- the gateway and plain catalog read path are fast enough for an academic MVP deployment
- AI recommendation is slower than catalog reads, which is expected because it aggregates recommendation logic and product context
- the first request in each sequence is visibly slower than warm requests, so these numbers should be read as lightweight runtime indicators, not formal load-test results

## 5. Functional evaluation

### 5.1 Checkout flow

Successful checkout evidence:

- [e2e-checkout-success.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-success.json)

Observed result:

- login through gateway succeeded
- product lookup succeeded
- cart add and cart read succeeded
- order creation succeeded
- payment reached `Success`
- order status reached `Shipping`
- shipping status reached `Processing`

Failure-path evidence:

- [e2e-checkout-payment-failure.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/e2e-checkout-payment-failure.json)

Observed result:

- when payment was simulated to fail, payment status became `Failed`
- order status became `Cancelled`
- this confirms cross-service state updates are not hardcoded to the success path

### 5.2 Security and RBAC

Evidence:

- [auth-rbac-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/auth-rbac-check.json)

Observed result:

- login returned both access and refresh tokens
- unauthenticated access to a protected cart route returned `401`
- customer access to the admin user route returned `403`
- admin access to the same route returned `200`

### 5.3 AI integration

Evidence:

- [ai-gateway-demo.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/ai-gateway-demo.json)

Observed result:

- recommendation returned real product output
- chatbot result aligned with product context and returned `Laptop Pro 14`
- AI access worked through the same gateway-based system path used for the rest of the architecture

### 5.4 Health and runtime topology

Evidence:

- [health-check.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/evidence/health-check.json)
- [compose-ps.txt](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/compose-ps.txt)
- [network-inspect.json](/d:/CHAP2_E-COMMERCE/docs/chapter4/logs/network-inspect.json)

Observed result:

- gateway, all business services, and AI service were healthy
- Compose brought up the full service set consistently
- services shared the declared internal Docker network

## 6. Architectural strengths

- clear service boundaries are visible in both folder layout and runtime container topology
- the gateway is now a real architecture component rather than only a documentation placeholder
- auth flow is coherent: token issuance at `user-service`, token forwarding at gateway, token validation at downstream services
- order orchestration correctly coordinates payment and shipping instead of collapsing all logic into a single service
- AI is integrated into the main architecture and not treated as an isolated side experiment

## 7. Current limitations

- the response-time measurement is intentionally lightweight and single-client only; it should not be presented as a full concurrency benchmark
- monitoring is still a skeleton stage and does not yet include running Prometheus or Grafana containers in Compose
- centralized log aggregation is not implemented
- browser verification showed the frontend `Orders` page returning `Failed to fetch orders`, even though the underlying order APIs and end-to-end checkout evidence are passing through the gateway
- gateway security is intentionally pass-through for JWT verification; signature validation remains in downstream services rather than in Nginx

## 8. Scalability outlook

Within the current architecture, the system can scale in the following ways:

- stateless API services can be replicated independently behind the gateway
- the AI service can evolve separately because it already has its own deployment unit and dependencies
- read-heavy catalog traffic is naturally separable from write-heavy order and payment traffic
- observability can be upgraded incrementally because health and logging foundations already exist

The main scaling risks in the current phase are:

- synchronous orchestration in the checkout path
- lack of queue/event-driven decoupling for payment and shipping
- lack of production-grade monitoring and alerting

## 9. Conclusion

Phase 9 evaluation shows that the Chapter 4 system is functioning as a real integrated microservices deployment, not only as static code. The mandatory architecture, gateway, JWT, service communication, Docker deployment, checkout flow, AI integration, and baseline observability requirements have all been backed by runtime evidence.

The repository is close to Phase 10 readiness from a Chapter 4 acceptance standpoint. The main remaining concern before any final wrap-up is not the Section 5 checklist itself, but the runtime frontend issue on the `Orders` page, which should be fixed if the final deliverable is expected to present a smoother UI demo.
