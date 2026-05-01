# Chapter 4 Phase 8 Observability

## 1. Purpose

This phase adds the minimum observability layer required by the Chapter 4 master prompt:

- basic logging for the gateway
- basic logging configuration for the main services
- health endpoints for service status checks
- a monitoring skeleton that is honest about the current scope

The implementation goal is practical observability for a course project, not a full production telemetry platform.

## 2. Deliverables

### Files added

- `docs/chapter4/08-observability.md`
- `scripts/health_check.ps1`
- `infrastructure/monitoring/prometheus.yml`
- `infrastructure/monitoring/README.md`

### Files updated

- `user-service/app/views.py`
- `user-service/app/urls.py`
- `user-service/config/settings.py`
- `product-service/app/views.py`
- `product-service/app/urls.py`
- `product-service/config/settings.py`
- `cart-service/app/views.py`
- `cart-service/app/urls.py`
- `cart-service/config/settings.py`
- `order-service/app/views.py`
- `order-service/app/urls.py`
- `order-service/config/settings.py`
- `payment-service/app/views.py`
- `payment-service/app/urls.py`
- `payment-service/config/settings.py`
- `shipping-service/app/views.py`
- `shipping-service/app/urls.py`
- `shipping-service/config/settings.py`
- `ai-service/app/main.py`

## 3. Logging implementation

### 3.1 Gateway logging

The gateway already logs through `gateway/nginx.conf`:

- access log: `/var/log/nginx/access.log`
- error log: `/var/log/nginx/error.log`

The access log format includes:

- request line
- status code
- upstream address
- upstream status
- request time
- upstream response time
- correlation ID

This makes the gateway the primary ingress-level observation point.

### 3.2 Django service logging

All Django business services now have explicit `LOGGING` configuration in settings.

Applied to:

- `user-service/config/settings.py`
- `product-service/config/settings.py`
- `cart-service/config/settings.py`
- `order-service/config/settings.py`
- `payment-service/config/settings.py`
- `shipping-service/config/settings.py`

Current behavior:

- log output goes to console
- format: timestamp, level, logger name, message
- root log level is controlled by `LOG_LEVEL` or defaults to `INFO`

This is enough for Compose logs, debugging, and later evidence capture.

### 3.3 AI service logging

`ai-service/app/main.py` now initializes a basic logging format for the FastAPI application layer.

This complements the request and service logs already emitted in AI-side helper code.

## 4. Health endpoints

### 4.1 Gateway health

Already implemented:

- `GET /health`

### 4.2 Business-service health

This phase adds a health endpoint to all Django services:

| Service | Route |
| --- | --- |
| `user-service` | `/health` |
| `product-service` | `/health` |
| `cart-service` | `/health` |
| `order-service` | `/health` |
| `payment-service` | `/health` |
| `shipping-service` | `/health` |
| `ai-service` | `/health` |

Each endpoint returns a simple JSON payload such as:

```json
{"service":"order-service","status":"ok"}
```

These endpoints are lightweight service liveness checks, not full dependency-deep health reports.

## 5. Health-check script

### 5.1 Script path

- `scripts/health_check.ps1`

### 5.2 What it verifies

The script checks, through the gateway:

- gateway health
- user service health
- product service health
- cart service health
- order service health
- payment service health
- shipping service health
- AI service health

### 5.3 Command

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\health_check.ps1
```

### 5.4 Save evidence

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\health_check.ps1 `
  -OutputPath .\docs\chapter4\evidence\health-check.json
```

## 6. Monitoring skeleton

The current project does not claim a complete Prometheus/Grafana implementation.

What is included:

- `infrastructure/monitoring/prometheus.yml`
- `infrastructure/monitoring/README.md`

This is intentionally described as a skeleton because:

- the services do not yet expose standardized `/metrics` endpoints
- Compose does not yet include a Prometheus container
- no Grafana dashboards are currently defined

This approach follows the master prompt requirement to be honest about the implementation scope.

## 7. Current observability scope

### Implemented now

- gateway access and error logging
- service console logging configuration
- key business event logs in order/payment/shipping paths
- health endpoints for all main services
- health-check script
- monitoring skeleton for later expansion

### Not implemented yet

- full metrics instrumentation
- Prometheus running in the Compose stack
- Grafana dashboards
- centralized log aggregation such as ELK/Loki

## 8. How this maps to the master prompt

| Prompt expectation | Status | Notes |
| --- | --- | --- |
| logging for gateway | achieved | Nginx access/error logs |
| logging for main services | achieved at basic level | explicit settings-level logging added |
| health check endpoints | achieved | all major services now expose `/health` |
| monitoring skeleton | achieved | `infrastructure/monitoring/` added honestly as skeleton |

## 9. Remaining gaps after Phase 8

- no metrics endpoint standard yet
- no live Prometheus/Grafana stack
- no persisted log shipping pipeline

These are acceptable for the project scope because the prompt explicitly allows a usable skeleton instead of a full monitoring platform, provided the limitation is documented honestly.
