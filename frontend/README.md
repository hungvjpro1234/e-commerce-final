## Frontend Status

Trang thai hien tai: `MVP UI complete`

Frontend nay duoc xay dung bang Next.js 14 + Tailwind CSS va da noi voi cum microservice thong qua route proxy noi bo `/api/[...path]`.

## Da hoan thanh

- landing page lay du lieu tu `product-service`
- product detail theo tung loai san pham
- dang ky, dang nhap, luu auth state
- gio hang: xem, cap nhat so luong, xoa item
- checkout va tao order
- order list va order tracking
- dashboard `admin`:
  - users
  - products
  - categories
  - orders
  - shipping
- dashboard `staff`:
  - orders
  - shipping

## Kien truc frontend

- Next.js App Router
- React Query cho fetch/mutation
- Zustand persist cho auth state phia client
- Axios wrapper de goi `/api/...`
- Route handler `app/api/[...path]/route.ts` dong vai tro API gateway nho

Proxy hien tai da map:

- `/api/auth`, `/api/users` -> `user-service`
- `/api/products`, `/api/categories` -> `product-service`
- `/api/cart` -> `cart-service`
- `/api/orders` -> `order-service`
- `/api/payment` -> `payment-service`
- `/api/shipping` -> `shipping-service`

## Dieu kien de frontend hoat dong dung

- 6 backend service phai dang chay
- bien moi truong phai tro dung toi service host/port
- JWT dang nhap phai duoc cap boi `user-service`

Neu backend khong chay, cac man hinh catalog, cart, checkout va dashboard se khong lay duoc du lieu.

## Cau hinh moi truong

Neu chay frontend rieng ben ngoai Docker, dung `.env.development` va tro den host local:

```env
USER_SERVICE_URL=http://localhost:8002
PRODUCT_SERVICE_URL=http://localhost:8001
CART_SERVICE_URL=http://localhost:8003
ORDER_SERVICE_URL=http://localhost:8004
PAYMENT_SERVICE_URL=http://localhost:8005
SHIPPING_SERVICE_URL=http://localhost:8006
```

Neu chay bang Docker Compose, file `.env.production` dang tro den ten service trong network Docker.

## Cach chay

### Cach 1: chay cung toan stack

Tu root repo:

```bash
docker compose up --build
```

Frontend se co tai `http://localhost:3000`.

### Cach 2: chay rieng frontend de dev UI

```bash
cd frontend
npm install
npm run dev
```

Frontend se chay tai `http://localhost:3000`.

## Ghi chu ve trang thai va gioi han

- Frontend hien phuc vu tot cho demo va bao cao MVP.
- Anh san pham dang la placeholder phuc vu trinh bay.
- Kiem tra auth va role chu yeu dua tren token va du lieu user tra ve tu backend.
- He thong chua co API gateway rieng, frontend dang tam dong vai tro cau noi.
- Co luong test payment failure de kiem tra nhanh qua checkout.

## Script co san

```bash
npm run dev
npm run build
npm run start
npm run lint
```

## Ket luan

Frontend da o muc co the trinh dien full flow cho customer, staff va admin, voi dependency chinh la backend stack phai khoi dong on dinh. Neu muc tieu la production, buoc tiep theo nen la bo sung test E2E, hoan thien xu ly loi, va tach API gateway thanh thanh phan rieng.
