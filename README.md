# E-Commerce Microservices with Django/DRF

Monorepo nay trien khai 6 microservice Django REST Framework theo bounded context:

- `product-service`
- `user-service`
- `cart-service`
- `order-service`
- `payment-service`
- `shipping-service`

## Kien truc

- Moi service la mot Django project/app doc lap.
- Moi service co database rieng.
- `product-service` dung PostgreSQL `product_db`.
- `user-service`, `cart-service`, `order-service`, `payment-service`, `shipping-service` dung MySQL rieng.
- Khong co `ForeignKey` xuyen service.
- Giao tiep lien service thong qua REST API.

## Cau truc repo

```text
.
|-- docker-compose.yml
|-- product-service/
|-- user-service/
|-- cart-service/
|-- order-service/
|-- payment-service/
`-- shipping-service/
```

## Chay bang Docker Compose

```bash
docker compose up --build
```

Stack hien tai can dung chung cac bien bao mat sau:

- `JWT_SIGNING_KEY`: key ky/xac minh access token phat hanh boi `user-service`
- `INTERNAL_SERVICE_JWT_SECRET`: secret ky/xac minh internal JWT cho service-to-service
- `INTERNAL_SERVICE_JWT_ALGORITHM`: thuat toan internal JWT, hien la `HS256`
- `INTERNAL_SERVICE_ISSUER`: issuer noi bo, hien la `order-service`
- `INTERNAL_SERVICE_AUDIENCE`: bat buoc tren `cart-service`, `product-service`, `payment-service`, `shipping-service`
- `INTERNAL_SERVICE_NAME`: bat buoc tren `order-service`

Sau khi chay:

- Product Service: `http://localhost:8001`
- User Service: `http://localhost:8002`
- Cart Service: `http://localhost:8003`
- Order Service: `http://localhost:8004`
- Payment Service: `http://localhost:8005`
- Shipping Service: `http://localhost:8006`

## Migrate va seed thu cong

Vi du voi `product-service`:

```bash
cd product-service
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8001
```

Lam tuong tu cho cac service con lai voi cong tuong ung.

Luu y: `payment-service` va `shipping-service` da co them migration moi de luu `user_id` ownership. Khi cap nhat code, can restart stack hoac chay lai `python manage.py migrate` cho 2 service nay truoc khi smoke test luong order.

## Bien moi truong

Moi service co file `.env.example` rieng. Doi ten thanh `.env` neu muon tuy chinh cau hinh khi chay local khong dung Docker.
Neu chay bang Docker Compose, cac bien JWT/internal JWT da duoc wire san trong `docker-compose.yml`.

## Endpoint chinh

### Product Service

- `GET /products/`
- `POST /products/`
- `GET /products/{id}/`
- `GET /categories/`
- `POST /categories/`

### User Service

- `POST /auth/register`
- `POST /auth/login`
- `GET /users/`

### Cart Service

- `POST /cart/add`
- `GET /cart/`
- `PUT /cart/update`
- `DELETE /cart/remove`

### Order Service

- `POST /orders/`
- `GET /orders/`
- `GET /orders/{id}/`

### Payment Service

- `GET /payment/status`
- `GET /payment/status/{order_id}`

### Shipping Service

- `GET /shipping/status`
- `GET /shipping/status/{order_id}`

## Luong end-to-end

1. Dang ky/dang nhap user qua `user-service`
2. Lay danh sach san pham tu `product-service`
3. Them san pham vao gio qua `cart-service`
4. Tao don bang `order-service`
5. `order-service` goi:
   - `cart-service` de lay gio
   - `product-service` de kiem tra gia va ton kho
   - `payment-service` de thanh toan
   - `shipping-service` de tao shipment khi payment thanh cong

## Seed data

- `product-service`: category + product + book/electronics/fashion mau
- `user-service`: admin/staff/customer mau
- `cart-service`: cart va cart item mau
- `order-service`, `payment-service`, `shipping-service`: ban ghi mau de test nhanh

## Ghi chu

- JWT duoc phat hanh boi `user-service` bang `simplejwt`
- `order-service` su dung synchronous REST, khong dung Kafka/RabbitMQ
- Payment co ho tro `simulate_failure=true` de test nhanh kich ban loi

## Smoke test secure flow

- Script san co: `docs/secure-flow-smoke-test.ps1`
- Huong dan: `docs/secure-flow-smoke-test.md`
