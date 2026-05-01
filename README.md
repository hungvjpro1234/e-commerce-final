# E-Commerce Microservices Monorepo

Monorepo nay chua day du stack MVP cho he thong e-commerce gom:

- 6 Django REST Framework microservice
- 1 frontend Next.js 14
- Docker Compose de chay toan bo he thong
- Seed data va smoke test script cho luong mua hang

## Trang thai project

Trang thai hien tai: `MVP integration complete`

Repo da co source cho:

- `product-service`: quan ly category va product schema-driven voi 10 `detail_type`
- `user-service`: dang ky, dang nhap, phan quyen `admin` / `staff` / `customer`
- `cart-service`: them, cap nhat, xoa va xem gio hang
- `order-service`: tao don, xem danh sach, xem chi tiet, cap nhat trang thai, dieu phoi goi sang payment va shipping
- `payment-service`: tao payment noi bo, tra cuu trang thai, ho tro `simulate_failure`
- `shipping-service`: tao shipment noi bo, tra cuu va cap nhat trang thai giao hang
- `frontend`: giao dien catalog, auth, cart, checkout, order tracking, dashboard cho admin va staff

## Kien truc hien tai

- Moi service la mot Django project doc lap.
- Moi service co database rieng, khong co `ForeignKey` xuyen service.
- `product-service` dung PostgreSQL va luu detail san pham ngay tren `Product.detail` (`JSONField`).
- `user-service`, `cart-service`, `order-service`, `payment-service`, `shipping-service` dung MySQL rieng.
- Frontend su dung Next.js App Router va route `/api/[...path]` lam API gateway noi bo.
- Xac thuc nguoi dung dung JWT cua `user-service`.
- Goi service-to-service dung internal JWT do `order-service` ky.

## Cau truc repo

```text
.
|-- docker-compose.yml
|-- docs/
|-- frontend/
|-- product-service/
|-- user-service/
|-- cart-service/
|-- order-service/
|-- payment-service/
`-- shipping-service/
```

## Trang thai theo thanh phan

### Backend

Da hien thuc:

- model, serializer, view, url va migration cho ca 6 service
- `product-service` da chuyen tu 3 bang detail co dinh sang contract thong nhat:
  - `detail_type: string`
  - `detail: Record<string, string | number | boolean>`
- lenh `seed_data` cho tung service
- JWT auth cho user va phan quyen theo role
- luong order goi sang cart, product, payment, shipping
- migration bo sung `user_id` ownership cho `payment-service` va `shipping-service`
- test file cho tung service trong `app/tests.py`

Can xac nhan khi nghiem thu runtime:

- chay `docker compose up --build` thanh cong tren may dich
- smoke test luong secure order/payment/shipping
- frontend build/lint trong moi truong local khong bi gioi han sandbox

### Frontend

Da hien thuc:

- landing page va product detail
- register / login / logout
- cart, checkout, order list, order tracking
- dashboard `admin`: users, products, categories, orders, shipping
- dashboard `staff`: orders, shipping
- proxy `/api/...` de dinh tuyen request den tung microservice

Han che hien tai:

- can backend dang chay thi frontend moi hoat dong day du
- hinh anh san pham la placeholder de phuc vu demo
- he thong o muc MVP, chua co payment gateway that, queue/event bus, hay observability hoan chinh

## Chay bang Docker Compose

```bash
docker compose up --build
```

Sau khi stack len:

- Frontend: `http://localhost:3000`
- Product Service: `http://localhost:8001`
- User Service: `http://localhost:8002`
- Cart Service: `http://localhost:8003`
- Order Service: `http://localhost:8004`
- Payment Service: `http://localhost:8005`
- Shipping Service: `http://localhost:8006`

Compose hien tai tu dong:

- khoi tao database
- chay `migrate`
- chay `seed_data`
- start cac service

## Bien moi truong quan trong

Stack dang dung chung cac bien bao mat sau:

- `JWT_SIGNING_KEY`
- `INTERNAL_SERVICE_JWT_SECRET`
- `INTERNAL_SERVICE_JWT_ALGORITHM`
- `INTERNAL_SERVICE_ISSUER`
- `INTERNAL_SERVICE_AUDIENCE`
- `INTERNAL_SERVICE_NAME`

Neu chay bang Docker Compose, cac bien nay da duoc wire san trong [docker-compose.yml](/d:/CHAP2_E-COMMERCE/docker-compose.yml).

## Chay thu cong tung phan

Vi du voi `product-service`:

```bash
cd product-service
python manage.py migrate
python manage.py seed_data
python manage.py runserver 0.0.0.0:8001
```

Lam tuong tu cho cac service con lai voi cong tuong ung.

Frontend local:

```bash
cd frontend
npm install
npm run dev
```

## Luong end-to-end hien co

1. Dang ky hoac dang nhap qua `user-service`
2. Xem san pham qua `product-service`
3. Them vao gio qua `cart-service`
4. Checkout qua `order-service`
5. `order-service` lay gio hang, doi chieu san pham, tao payment, tao shipping
6. Frontend theo doi `order`, `payment`, `shipping` tren man hinh order tracking

## Product catalog contract

Product API public va internal hien tra ve mot shape thong nhat:

```json
{
  "id": 1,
  "name": "Django for APIs",
  "price": 29.99,
  "stock": 20,
  "category": 1,
  "category_data": { "id": 1, "name": "Books" },
  "detail_type": "book",
  "detail": {
    "author": "William S. Vincent",
    "publisher": "WelcomeToCode",
    "isbn": "9781735467221"
  }
}
```

Danh sach `detail_type` hien tai:

- `book`
- `electronics`
- `fashion`
- `home-living`
- `beauty`
- `sports`
- `toys`
- `grocery`
- `office`
- `pet-supplies`

`order-service` va `cart-service` chi phu thuoc vao cac field base nhu `id`, `price`, `stock`, nen luong mua hang khong doi sau refactor nay.

## Tai lieu va smoke test

- Huong dan secure flow: [docs/secure-flow-smoke-test.md](/d:/CHAP2_E-COMMERCE/docs/secure-flow-smoke-test.md)
- Script smoke test: [docs/secure-flow-smoke-test.ps1](/d:/CHAP2_E-COMMERCE/docs/secure-flow-smoke-test.ps1)
- Tong quan UI: [docs/frontend-ui-overview.md](/d:/CHAP2_E-COMMERCE/docs/frontend-ui-overview.md)

## Ket luan trang thai

Project dang o muc co the demo duoc full flow cua mot he thong e-commerce microservices tren Docker Compose. Phan kien truc, source code va giao dien da co du; buoc tiep theo de dua sang muc on dinh hon la chay smoke test/thuc nghiem runtime tren moi truong local hoac server dich, sau do bo sung CI, monitoring va hardening cho production.
