# Chapter 4 Phase 6 End-to-End Flow

## 1. Purpose

This phase packages the complete checkout workflow into a Chapter 4 deliverable that is directly testable and replayable. The target flow follows the master prompt exactly:

1. user login
2. browse product
3. add to cart
4. create order
5. payment
6. shipping

The flow is implemented as a dedicated Chapter 4 script that goes through the gateway instead of calling backend services directly.

## 2. Deliverables

### Files added

- `scripts/e2e_checkout_flow.ps1`
- `docs/chapter4/06-end-to-end-flow.md`

### Reused supporting implementation

- `gateway/nginx.conf`
- `order-service/app/views.py`
- `order-service/app/service_clients.py`
- `cart-service/app/views.py`
- `payment-service/app/views.py`
- `shipping-service/app/views.py`
- `user-service/app/views.py`
- `product-service/app/views.py`

## 3. What this phase verifies

The script verifies the full Chapter 4 checkout path through the gateway:

- gateway is reachable
- customer can log in
- product catalog is reachable
- at least one in-stock product can be selected
- selected product can be added to cart
- order can be created from the cart
- payment status is created and can be queried
- shipping status is created and can be queried
- customer ownership checks are enforced for order, payment, and shipping data
- optional payment-failure path can be simulated

## 4. Script path

- `scripts/e2e_checkout_flow.ps1`

## 5. Flow implementation details

### 5.1 Entry point

The script talks only to the gateway by default:

- base URL default: `http://localhost:8080`

This aligns the E2E verification with the Chapter 4 target architecture instead of testing isolated services only.

### 5.2 Route usage

| Step | Gateway route |
| --- | --- |
| gateway health | `/health` |
| login | `/api/users/auth/login` |
| register fallback customer B | `/api/users/auth/register` |
| browse products | `/api/products/products` |
| add to cart | `/api/cart/add` |
| view cart | `/api/cart/` |
| create order | `/api/orders/` |
| view order | `/api/orders/<order_id>/` |
| payment status | `/api/payments/status/<order_id>` |
| shipping status | `/api/shipping/status/<order_id>` |

### 5.3 Success path behavior

Expected successful path:

1. gateway returns `status=ok`
2. customer login returns JWT
3. product list is non-empty
4. one in-stock product is selected
5. cart contains the selected product
6. order is created
7. payment status is `Success`
8. shipping status is one of:
   - `Processing`
   - `Shipping`
   - `Delivered`
9. another customer cannot access the first customer's order/payment/shipping data

### 5.4 Simulated payment failure path

If the script runs with `-SimulatePaymentFailure`, expected behavior is:

- order status becomes `Cancelled`
- payment status becomes `Failed`
- shipping check is skipped because shipping should not be created as part of the successful checkout continuation path

## 6. Command to run

### 6.1 Default success path

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\e2e_checkout_flow.ps1
```

### 6.2 Save summary output as evidence

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\e2e_checkout_flow.ps1 `
  -OutputPath .\docs\chapter4\evidence\e2e-checkout-success.json
```

### 6.3 Payment failure path

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\e2e_checkout_flow.ps1 `
  -SimulatePaymentFailure `
  -OutputPath .\docs\chapter4\evidence\e2e-checkout-payment-failure.json
```

## 7. Output format

The script prints JSON at the end. Example fields:

- `gateway_status`
- `product_id`
- `product_name`
- `cart_item_quantity`
- `order_id`
- `order_status`
- `payment_status`
- `shipping_status`
- `simulated_fail`

This output is intended to be saved directly into `docs/chapter4/evidence/` as a reusable proof artifact.

## 8. Preconditions

Before running the script:

1. the full Compose stack should be up
2. the gateway should be exposed on `localhost:8080`
3. seed data should already be loaded

Recommended startup:

```bash
docker compose up -d
```

## 9. Evidence strategy

The master prompt requires not only code but evidence that the flow can be replayed. This phase contributes evidence in the following forms:

- executable script
- replay steps
- machine-readable summary output
- ownership checks for protected resources

Suggested evidence files:

- `docs/chapter4/evidence/e2e-checkout-success.json`
- `docs/chapter4/evidence/e2e-checkout-payment-failure.json`

## 10. Mapping to the Chapter 4 flow checklist

| Checklist requirement | Coverage in this phase |
| --- | --- |
| login successful | script logs in through gateway |
| get products successful | script browses `/api/products/products` |
| add cart successful | script calls `/api/cart/add` and validates cart content |
| create order successful | script creates order through `/api/orders/` |
| payment successful | script validates `/api/payments/status/<order_id>` |
| shipping initiated or updated | script validates `/api/shipping/status/<order_id>` on success path |

## 11. Remaining gaps after Phase 6

- runtime JSON evidence has not yet been generated in this turn
- no screenshot evidence has been captured yet
- no Postman collection or Python integration test variant exists yet

These are acceptable because the prompt allows a script-based replay flow, and the current deliverable now exists as real code that can be executed against the system.
