# Secure Flow Smoke Test

Script: `docs/secure-flow-smoke-test.ps1`

## Preconditions

- Docker Desktop va compose stack da chay.
- Cac service expose tren localhost:
  - `8002` user-service
  - `8003` cart-service
  - `8004` order-service
  - `8005` payment-service
  - `8006` shipping-service
- Seed data da duoc nap boi compose startup.

## What it verifies

- Login bang seeded customer.
- Customer cart/order flow khong gui `user_id` tu client.
- Payment va shipping duoc tao qua secure order flow.
- Customer B khong doc duoc order/payment/shipping cua Customer A.
- Co the chay them path payment failure voi `-SimulatePaymentFailure`.

## Run

```powershell
powershell -ExecutionPolicy Bypass -File .\docs\secure-flow-smoke-test.ps1
```

Payment failure path:

```powershell
powershell -ExecutionPolicy Bypass -File .\docs\secure-flow-smoke-test.ps1 -SimulatePaymentFailure
```

## Expected result

- Script in ra tung step.
- Ket thuc voi JSON summary gom `order_id`, `order_status`, `payment_status`, va neu co, `shipping_status`.
- Neu bat ky ownership check hoac secure flow nao sai, script se stop voi exception.
