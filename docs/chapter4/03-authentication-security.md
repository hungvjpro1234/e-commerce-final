# Chapter 4 Phase 3 Authentication and Security

## 1. Purpose

This phase standardizes the authentication and authorization model across the system and makes the trust boundaries explicit in both code and documentation.

The objective is not to introduce a brand-new auth mechanism. The codebase already had a working JWT model. This phase formalizes it for Chapter 4 by:

- confirming where tokens are issued
- confirming where tokens are validated
- making protected and internal routes explicit
- clarifying RBAC behavior
- making internal service authentication auditable

## 2. Deliverables

### Files added

- `docs/chapter4/03-authentication-security.md`

### Files updated

- `product-service/app/views.py`
- `cart-service/app/views.py`
- `order-service/app/views.py`
- `payment-service/app/views.py`
- `shipping-service/app/views.py`

### Security-focused evidence

- `user-service/app/serializers.py`
- `user-service/app/views.py`
- `user-service/config/settings.py`
- `product-service/app/auth.py`
- `cart-service/app/auth.py`
- `order-service/app/auth.py`
- `payment-service/app/auth.py`
- `shipping-service/app/auth.py`
- `gateway/nginx.conf`

## 3. Authentication architecture

### 3.1 User authentication flow

The current user authentication flow is:

1. client submits credentials to `user-service`
2. `user-service` validates credentials using `LoginSerializer`
3. `user-service` issues a JWT access token
4. token is sent by the client as a bearer token
5. gateway forwards the `Authorization` header unchanged
6. downstream Django services validate the JWT using the shared signing key

### 3.2 Service-to-service authentication flow

The current service-to-service flow is intentionally separate from user JWT:

1. `order-service` generates a short-lived internal token
2. token includes:
   - `iss`
   - `aud`
   - `service`
   - `exp`
3. internal downstream services validate that token using:
   - `INTERNAL_SERVICE_JWT_SECRET`
   - `INTERNAL_SERVICE_JWT_ALGORITHM`
   - `INTERNAL_SERVICE_ISSUER`
   - service-specific `INTERNAL_SERVICE_AUDIENCE`

This keeps internal orchestration distinct from end-user authentication.

## 4. Token issuance

### 4.1 Where user tokens are issued

User JWT tokens are issued in `user-service`:

- login endpoint: `user-service/app/views.py`
- serializer: `user-service/app/serializers.py`

The login serializer extends `TokenObtainPairSerializer` and adds the claims:

- `role`
- `user_id`
- `id`

This means downstream services do not need to query `user-service` during every request just to identify the acting user and role.

### 4.2 Where internal tokens are issued

Internal service tokens are issued in:

- `order-service/app/auth.py`

Function:

- `build_internal_service_token(audience)`

Current internal caller:

- `order-service`

Current internal targets:

- `cart-service`
- `product-service`
- `payment-service`
- `shipping-service`

## 5. Token validation

### 5.1 Validation of user JWT

User JWT validation is performed by each Django business service via:

- `rest_framework_simplejwt.authentication.JWTStatelessUserAuthentication`

Configured in:

- `user-service/config/settings.py`
- `product-service/config/settings.py`
- `cart-service/config/settings.py`
- `order-service/config/settings.py`
- `payment-service/config/settings.py`
- `shipping-service/config/settings.py`

Signing trust:

- all these services use the shared `JWT_SIGNING_KEY`

### 5.2 Validation of internal service tokens

Internal token validation is performed by custom `InternalServiceAuthentication` classes in:

- `product-service/app/auth.py`
- `cart-service/app/auth.py`
- `payment-service/app/auth.py`
- `shipping-service/app/auth.py`

Validation checks include:

- bearer header shape
- token signature
- expected algorithm
- issuer
- audience
- presence of `service` claim

## 6. Gateway security strategy

The gateway security strategy implemented in `gateway/nginx.conf` is:

- forward `Authorization` as received
- preserve or create `X-Correlation-ID`
- attach basic security headers
- block public access to internal route families

The gateway does not validate JWT signatures in this phase. Downstream services remain the verification authority.

This is a deliberate choice because:

- the services already enforce JWT validation and RBAC
- duplicating full JWT validation in Nginx would add complexity without improving project-level evidence proportionally
- service-to-service internal endpoints must remain inaccessible from public routes regardless of user token state

## 7. RBAC model

### 7.1 Supported roles

The current role model remains:

- `admin`
- `staff`
- `customer`

### 7.2 RBAC intent

| Role | Main capability |
| --- | --- |
| `admin` | full operational and administrative access |
| `staff` | order and shipping operational access |
| `customer` | customer-facing shopping and order tracking access |

### 7.3 RBAC enforcement examples

| Service | Enforcement example | Behavior |
| --- | --- | --- |
| `user-service` | `IsAdmin` on user management routes | only admin may list/create/update/delete users |
| `product-service` | `IsAdmin` on create/update/delete product and category routes | public browse, admin-only catalog mutation |
| `order-service` | `is_staff_or_admin()` on broader order visibility and status updates | customer sees own orders only; staff/admin may manage more broadly |
| `payment-service` | `is_staff_or_admin()` for broader status visibility | customer sees own payment records only |
| `shipping-service` | `is_staff_or_admin()` for broader status visibility and updates | customer sees own shipment status only |

## 8. Public versus protected route matrix

### 8.1 Public routes

| Route | Service | Access |
| --- | --- | --- |
| `/auth/register` | `user-service` | public |
| `/auth/login` | `user-service` | public |
| `GET /products*` | `product-service` | public |
| `GET /categories*` | `product-service` | public |

### 8.2 Protected user-JWT routes

| Route family | Service | Access |
| --- | --- | --- |
| `/users/*` | `user-service` | authenticated, admin-only by permission class |
| `/cart/*` | `cart-service` | authenticated |
| `/orders/*` | `order-service` | authenticated |
| `/payment/status*` | `payment-service` | authenticated |
| `/shipping/status*` | `shipping-service` | authenticated |
| mutating `/products*` and `/categories*` | `product-service` | authenticated, admin-only |

### 8.3 Internal-token routes

| Route family | Service | Access |
| --- | --- | --- |
| `/internal/products/*` | `product-service` | internal service token only |
| `/internal/cart/*` | `cart-service` | internal service token only |
| `/internal/payment/*` | `payment-service` | internal service token only |
| `/internal/shipping/*` | `shipping-service` | internal service token only |

## 9. Code normalization completed in this phase

To make the protection model explicit and auditable, protected views now declare authentication intent more clearly instead of relying only on global defaults.

### 9.1 Explicit protection added

- `product-service/app/views.py`
  - `InternalProductViewSet` now explicitly requires `IsAuthenticated`
- `cart-service/app/views.py`
  - internal cart endpoints now explicitly require `IsAuthenticated`
- `order-service/app/views.py`
  - order list/create and retrieve/update views now explicitly require `IsAuthenticated`
- `payment-service/app/views.py`
  - internal payment processing and payment status views now explicitly require `IsAuthenticated`
- `shipping-service/app/views.py`
  - internal shipment creation and shipment status views now explicitly require `IsAuthenticated`

This does not change the intended security model. It makes the model visible in the view layer, which is important for Chapter 4 review and maintenance.

## 10. Frontend token behavior

The current frontend behavior is:

- login calls `/auth/login`
- access token is stored in client auth state
- API calls attach `Authorization: Bearer <token>` through the Axios interceptor in `frontend/lib/api.ts`

This is compatible with the current gateway strategy because the gateway simply forwards bearer headers to downstream services.

## 11. How to test the auth flow end to end

### 11.1 Obtain token

```bash
curl -X POST http://localhost/api/users/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"customer\",\"password\":\"password123\"}"
```

Expected result:

- HTTP `200`
- response contains `access`
- response contains `user`

### 11.2 Access a protected customer route

```bash
curl http://localhost/api/cart/ \
  -H "Authorization: Bearer <token>"
```

Expected result:

- authenticated response for the token owner

### 11.3 Attempt admin-only action with customer token

```bash
curl -X POST http://localhost/api/products/products \
  -H "Authorization: Bearer <customer-token>" \
  -H "Content-Type: application/json" \
  -d "{\"name\":\"Test\",\"price\":1,\"stock\":1,\"category\":1,\"detail_type\":\"book\",\"detail\":{\"author\":\"A\",\"publisher\":\"B\",\"isbn\":\"123\"}}"
```

Expected result:

- permission denied

### 11.4 Attempt internal route through gateway

```bash
curl http://localhost/api/payments/internal/payment/pay
```

Expected result:

- HTTP `403` at gateway level

## 12. Phase 3 assessment

### Chapter 4 criteria addressed

- JWT auth flow is now explicitly documented from issuance to verification
- protected routes are now clearly separated from public routes
- RBAC model is now documented and mapped to code
- internal service authentication is now documented and tied to concrete files
- gateway auth header strategy is aligned with downstream verification

### Remaining gaps after Phase 3

- no centralized gateway-side JWT validation
- no refresh-token handling workflow documented for frontend/browser UX
- no runtime evidence bundle yet for token-based tests through the gateway

These are acceptable at this stage because the project already has a functional auth architecture and the remaining work is mainly integration evidence and deployment hardening.
