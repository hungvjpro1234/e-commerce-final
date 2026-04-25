# Báo cáo tiểu luận (phần trích)

## Chương 2. Thiết kế các thành phần hệ thống E-Commerce theo mô hình microservices

<a id="muc-thong-tin-pham-vi"></a>

**Phạm vi tài liệu:** từ mục 2.3 đến 2.8 — thiết kế chi tiết từng dịch vụ backend đã triển khai (Django REST Framework), bám theo mã nguồn và cấu hình trong kho mã (`README.md`, `docker-compose.yml`, từng thư mục `*-service/`).

**Ghi chú về cơ sở minh chứng (thống nhất trong các mục 2.3.2–2.8.2):** mỗi dịch vụ đều có **đoạn trích mã** gắn với **đường dẫn tệp** trong kho mã. Với mô hình dữ liệu, báo cáo trích **toàn bộ** lớp/model trong `app/models.py` của từng service (không bỏ sót trường khai báo trong code). Bổ sung trích dẫn tùy bối cảnh: `app/serializers.py` (User — claim JWT khi đăng nhập), `app/service_clients.py` (Order — URL và phương thức gọi dịch vụ nội bộ). Các tệp liên quan khác: `app/views.py`, `app/urls.py`, `app/auth.py` (nơi có), `config/settings.py` (CSDL, biến môi trường, JWT), và `docker-compose.yml` (tên dịch vụ DB, cổng, biến bảo mật chung).

---

### Mục lục

*Mục lục dưới đây bao trùm toàn bộ các tiểu mục từ 2.3 đến 2.8: mỗi service (Product, User, Cart, Order, Payment, Shipping) gồm mục cấp hai (2.x) và đủ hai mục cấp ba (2.x.1, 2.x.2) theo nội dung tài liệu; thêm mục bảng tổng hợp cuối chương. Có thể dùng liên kết nội bộ tương ứng anchor (`#muc-…`) khi xem dưới dạng HTML hoặc trình soạn hỗ trợ thẻ `<a>`.*

1. [Thông tin phạm vi và cơ sở minh chứng](#muc-thong-tin-pham-vi)
2. [2.3 Thiết kế Product Service](#muc-23) *(product-service)*
   - [2.3.1 Vai trò của service](#muc-231)
   - [2.3.2 Cấu trúc dữ liệu, API và cơ chế bảo mật](#muc-232)
3. [2.4 Thiết kế User Service](#muc-24) *(user-service)*
   - [2.4.1 Vai trò của service](#muc-241)
   - [2.4.2 Cấu trúc dữ liệu, API và cơ chế bảo mật](#muc-242)
4. [2.5 Thiết kế Cart Service](#muc-25) *(cart-service)*
   - [2.5.1 Vai trò của service](#muc-251)
   - [2.5.2 Cấu trúc dữ liệu, API và cơ chế bảo mật](#muc-252)
5. [2.6 Thiết kế Order Service](#muc-26) *(order-service)*
   - [2.6.1 Vai trò của service](#muc-261)
   - [2.6.2 Cấu trúc dữ liệu, luồng nghiệp vụ, API](#muc-262)
6. [2.7 Thiết kế Payment Service](#muc-27) *(payment-service)*
   - [2.7.1 Vai trò của service](#muc-271)
   - [2.7.2 Cấu trúc dữ liệu, API](#muc-272)
7. [2.8 Thiết kế Shipping Service](#muc-28) *(shipping-service)*
   - [2.8.1 Vai trò của service](#muc-281)
   - [2.8.2 Cấu trúc dữ liệu, API](#muc-282)
8. [Bảng tổng hợp kiến trúc](#muc-bang-tong-hop)

---

<a id="muc-23"></a>

## 2.3 Thiết kế Product Service

<a id="muc-231"></a>

### 2.3.1 Vai trò của service

Product Service đảm nhiệm **bounded context danh mục và sản phẩm** trong hệ thống E-Commerce: quản lý thực thể `Category`, `Product` và ba dạng mở rộng theo từng loại hàng hóa **Book** (sách), **Electronics** (điện tử) và **Fashion** (thời trang), mỗi dạng liên kết một-một với `Product` trong cùng cơ sở dữ liệu.

Việc tách thành một microservice riêng có các lý do sau: (1) tách vòng đời và tần suất cập nhật dữ liệu sản phẩm khỏi tài khoản, giỏ hàng, đơn hàng; (2) cho phép lựa chọn hệ quản trị cơ sở dữ liệu phù hợp bối cảnh dữ liệu phẩm (trong triển khai hiện tại: PostgreSQL, `product_db`); (3) giao diện đọc dành cho nội bộ (`/internal/products/...`) phục vụ kiểm tra giá và tồn kho khi đặt hàng mà **không** cần Foreign Key xuyên cơ sở dữ liệu tới dịch vụ khác.

Product Service **không** thực hiện lời gọi HTTP tới các service còn lại. Thay vào đó, Order Service gọi endpoint nội bộ để lấy thông tin sản phẩm theo mã logic `product_id`.

<a id="muc-232"></a>

### 2.3.2 Cấu trúc dữ liệu, API và cơ chế bảo mật

**Mô hình dữ liệu.** `Category` gồm trường `name`. `Product` gồm `name`, `price`, `stock` và tham chiếu `category` tới `Category` (quan hệ một-nhiều). Các bảng chi tiết `Book`, `Electronics`, `Fashion` mỗi bảng có `OneToOneField` tới `Product` và bổ sung thuộc tính đặc thù. Serializer tổng hợp (`app/serializers.py`) hỗ trợ tạo/cập nhật kèm `detail_type` và `detail` (từ điển) để đồng bộ bản ghi chi tiết tương ứng.

**Minh chứng mã nguồn — toàn bộ model (`product-service/app/models.py`):**

```python
from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products")

    def __str__(self):
        return self.name


class Book(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="book")
    author = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20)


class Electronics(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="electronics")
    brand = models.CharField(max_length=100)
    warranty = models.IntegerField()


class Fashion(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name="fashion")
    size = models.CharField(max_length=10)
    color = models.CharField(max_length=50)
```

**Minh chứng mã nguồn — định tuyến (`product-service/app/urls.py`):**

```python
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, InternalProductViewSet, ProductViewSet

router = DefaultRouter()
router.trailing_slash = "/?"
router.register("products", ProductViewSet, basename="product")
router.register("categories", CategoryViewSet, basename="category")
router.register("internal/products", InternalProductViewSet, basename="internal-product")

urlpatterns = router.urls
```

**Giao diện API.** Router REST đăng ký `products`, `categories` (ViewSet CRUD tùy phương thức HTTP) và `internal/products` (chỉ đọc) cho giao tiếp giữa các service: Order Service gọi `GET` tới tài nguyên sản phẩm theo định danh, kèm JWT nội bộ.

**Xác thực và phân quyền.** Cấu hình mặc định dùng `JWTStatelessUserAuthentication` (Django REST Framework) và mức `IsAuthenticated`. Đối với thao tác liệt kê và xem chi tiết sản phẩm, danh mục, hệ thống cho phép truy cập công khai (`AllowAny`). Các thao tác tạo, sửa, xóa yêu cầu quyền quản trị: kiểm tra claim `role` trên access token bằng lớp `IsAdmin` (vai trò `admin`). Các yêu cầu tới tài nguyên nội bộ sử dụng lớp `InternalServiceAuthentication`, xác minh JWT ký bằng bí mật nội bộ, kiểm tra `issuer` (trong cấu hình triển khai: `order-service`) và `audience` tương ứng `product-service` (cấu hình hóa bằng biến môi trường trong `docker-compose.yml`).

**Cơ sở dữ liệu.** Một cơ sở dữ liệu duy nhất, engine PostgreSQL, tên mặc định `product_db`, tham số kết nối qua `DB_*` trong cài đặt Django. Điều này phù hợp với nguyên tắc “mỗi service một database” ở mức vật lý/tách schema trong bối cảnh triển khai monorepo.

---

<a id="muc-24"></a>

## 2.4 Thiết kế User Service

<a id="muc-241"></a>

### 2.4.1 Vai trò của service

User Service đảm nhiệm **bounded context quản lý tài khoản và cấp phát định danh số hóa**: đăng ký người dùng, đăng nhập (phát hành JWT bằng thư viện Simple JWT), cùng giao diện quản trị danh sách tài khoản cho vai trò quản trị viên. Tách service giúp tách biệt trách nhiệm bảo mật mật khẩu, mô hình người dùng tùy biến (`AbstractUser` mở rộng) và khóa ký `JWT` dùng chung với các dịch vụ tiêu thụ token (cùng `SIGNING_KEY` qua biến `JWT_SIGNING_KEY`).

Trong mã nguồn đã khảo sát, User Service **không** gọi REST sang service khác; mối liên hệ với các bounded context còn lại là **tham chiếu logic** `user_id` (số nguyên) ở Cart, Order, Payment và Shipping.

<a id="muc-242"></a>

### 2.4.2 Cấu trúc dữ liệu, API và cơ chế bảo mật

**Mô hình dữ liệu.** Lớp `User` kế thừa `AbstractUser`, bổ sung trường `role` với các lựa chọn `admin`, `staff`, `customer` (mặc định `customer`). Các trường sẵn có của `AbstractUser` (tên đăng nhập, thư điện tử, tên, họ, mật khẩu đã băm) được sử dụng đầy đủ. Cấu hình `AUTH_USER_MODEL` trỏ tới ứng dụng `app.User`.

**Minh chứng mã nguồn — model (`user-service/app/models.py`):**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("staff", "Staff"),
        ("customer", "Customer"),
    )

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="customer")

    def __str__(self):
        return self.username
```

**Minh chứng mã nguồn — bổ sung claim vào access token khi đăng nhập (`user-service/app/serializers.py`, lớp `LoginSerializer` đầy đủ theo tệp gốc; `UserSerializer` cùng tệp, khai báo phía trên lớp này):**

```python
class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["user_id"] = user.id
        token["id"] = user.id
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data
```

**Minh chứng mã nguồn — định tuyến (`user-service/app/urls.py`):**

```python
from django.urls import path

from .views import LoginView, RegisterView, UserDetailView, UserListView

urlpatterns = [
    path("auth/register", RegisterView.as_view(), name="register"),
    path("auth/login", LoginView.as_view(), name="login"),
    path("users/", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="user-detail"),
]
```

**Giao diện API cốt lõi (khớp `urlpatterns` ở trên):**

| Đường dẫn (tương đối) | Mô tả |
|----------------------|--------|
| `POST /auth/register` | Tạo tài khoản; mật khẩu ghi riêng, tối thiểu 6 ký tự. |
| `POST /auth/login` | Cấp cặp access/refresh token; bổ sung claim `role`, `user_id` (và tương đương) để dịch vụ sau suy ra định danh. Kèm dữ liệu người dùng dạng JSON. |
| `GET`, `POST /users/` | Chỉ `admin`: liệt kê, hoặc tạo tài khoản (serializer ghi dành cho quản trị). |
| `GET`, `PUT`, `PATCH`, `DELETE /users/<pk>/` | Chỉ `admin`: xem, sửa, xóa; cho phép đổi mật khẩu khi cập nhật. |

**Cài đặt JWT.** Thời gian sống access token: 30 phút; refresh token: một ngày (có thể trích dẫn khi cần bảo vệ bài toán bảo mật trong báo cáo).

**Cơ sở dữ liệu.** MySQL, tên cơ sở dữ liệu mặc định `user_db` (kết nối qua cấu hình `DATABASES` trong `config/settings.py`).

---

<a id="muc-25"></a>

## 2.5 Thiết kế Cart Service

<a id="muc-251"></a>

### 2.5.1 Vai trò của service

Cart Service quản lý **bounded context giỏ hàng theo người dùng**: mỗi người tương ứng một bản ghi `Cart` xác định bởi `user_id` (số, tham chiếu logic tới User Service, không dùng khóa ngoại xuyên cơ sở dữ liệu), chứa nhiều `CartItem` (mỗi dòng: `product_id` logic, `quantity`).

Lý do tách service: (1) tách tải đọc/ghi giỏ với tải đơn hàng; (2) cho phép triển khai và mở rộng độc lập; (3) hỗ trợ giao diện nội bộ để **Order Service** lấy nội dung giỏ và xóa giỏ sau khi tạo đơn thành công, với bảo mật JWT nội bộ thống nhất với các service được gọi trong luồng thanh toán.

<a id="muc-252"></a>

### 2.5.2 Cấu trúc dữ liệu, API và cơ chế bảo mật

**Mô hình dữ liệu** — toàn bộ khai báo trong `app/models.py` (tham chiếu `user_id` / `product_id` là số nguyên, không FK xuyên service).

**Minh chứng mã nguồn (`cart-service/app/models.py`):**

```python
from django.db import models


class Cart(models.Model):
    user_id = models.IntegerField()

    def __str__(self):
        return f"Cart<{self.user_id}>"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    quantity = models.IntegerField()
```

**Minh chứng mã nguồn — định tuyến (`cart-service/app/urls.py`):**

```python
from django.urls import path

from .views import (
    AddToCartView,
    CartDetailView,
    ClearCartView,
    InternalCartDetailView,
    InternalClearCartView,
    RemoveCartItemView,
    UpdateCartView,
)

urlpatterns = [
    path("cart/add", AddToCartView.as_view(), name="cart-add"),
    path("cart/", CartDetailView.as_view(), name="cart-detail"),
    path("cart/update", UpdateCartView.as_view(), name="cart-update"),
    path("cart/remove", RemoveCartItemView.as_view(), name="cart-remove"),
    path("cart/clear", ClearCartView.as_view(), name="cart-clear"),
    path("internal/cart/<int:user_id>/", InternalCartDetailView.as_view(), name="internal-cart-detail"),
    path("internal/cart/<int:user_id>/clear", InternalClearCartView.as_view(), name="internal-cart-clear"),
]
```

**Giao diện API hướng người dùng (đã đăng nhập):** như các `path` công khai trong `urlpatterns` (thêm/lấy/cập nhật/xóa/giỏ trống). `user_id` **được lấy từ access token** (hàm hỗ trợ trên chuỗi claim), không chấp nhận từ client — phù hợp mục tiêu kiểm thử bảo mật luồng đặt hàng mô tả trong tài liệu hướng dẫn smoke test an toàn.

**Giao diện nội bộ phục vụ Order Service:** lấy giỏ theo `user_id` trên đường dẫn nội bộ, xóa toàn bộ mục theo cùng quy ước. Xác thực: `InternalServiceAuthentication` với `audience` là `cart-service` và `issuer` là `order-service` (cấu hình theo môi trường).

**Cơ sở dữ liệu.** MySQL, tên cơ sở dữ liệu mặc định `cart_db`.

---

<a id="muc-26"></a>

## 2.6 Thiết kế Order Service

<a id="muc-261"></a>

### 2.6.1 Vai trò của service

Order Service đóng vai trò **điều phối (orchestrator)** cho luồng đặt hàng: từ dữ liệu giỏ, kiểm tra tồn và tính giá từ Product Service, tạo bản ghi `Order` và `OrderItem`, gọi thanh toán tới Payment Service, tạo vận chuyển tại Shipping Service, rồi dọn giỏ tại Cart Service — theo mã nguồn, toàn bộ bước tạo đơn nằm trong một giao dịch cơ sở dữ liệu (`transaction.atomic`). Hệ thống triển khai gọi dịch vụ **đồng bộ qua HTTP**, không sử dụng message broker theo tài liệu dự án.

Tách service đặt hàng tách bạch: trạng thái vòng đời đơn, tổng giá, và tổ hợp bước nghiệp vụ, khỏi chi tiết sản phẩm, thanh toán hạ tầng và vận chuyển.

<a id="muc-262"></a>

### 2.6.2 Cấu trúc dữ liệu, luồng nghiệp vụ, API

**Mô hình dữ liệu.** Bảng đơn dùng `db_table = "orders"`; bảng dòng `OrderItem` liên kết tới `Order` bằng `ForeignKey`.

**Minh chứng mã nguồn — toàn bộ model (`order-service/app/models.py`):**

```python
from django.db import models


class Order(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Paid", "Paid"),
        ("Cancelled", "Cancelled"),
        ("Shipping", "Shipping"),
        ("Completed", "Completed"),
    )

    user_id = models.IntegerField()
    total_price = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")

    class Meta:
        db_table = "orders"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()
    quantity = models.IntegerField()
```

**Minh chứng mã nguồn — định tuyến (`order-service/app/urls.py`):**

```python
from django.urls import path

from .views import OrderListCreateView, OrderRetrieveView

urlpatterns = [
    path("orders/", OrderListCreateView.as_view(), name="order-list-create"),
    path("orders/<int:pk>", OrderRetrieveView.as_view(), name="order-detail-no-slash"),
    path("orders/<int:pk>/", OrderRetrieveView.as_view(), name="order-detail"),
]
```

**Minh chứng mã nguồn — gọi dịch vụ nội bộ (`order-service/app/service_clients.py`; header `Authorization` / `X-Correlation-ID` do `_internal_headers` tạo):**

```python
def get_cart(user_id, correlation_id):
    response = requests.get(
        f"{settings.CART_SERVICE_URL}/internal/cart/{user_id}/",
        headers=_internal_headers("cart-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "cart-service")
    return response.json()


def get_product(product_id, correlation_id):
    response = requests.get(
        f"{settings.PRODUCT_SERVICE_URL}/internal/products/{product_id}/",
        headers=_internal_headers("product-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "product-service")
    return response.json()


def create_payment(order_id, user_id, amount, correlation_id, simulate_failure=False):
    payload = {"order_id": order_id, "user_id": user_id, "amount": amount, "simulate_failure": simulate_failure}
    response = requests.post(
        f"{settings.PAYMENT_SERVICE_URL}/internal/payment/pay",
        json=payload,
        headers=_internal_headers("payment-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "payment-service")
    return response.json()


def create_shipment(order_id, user_id, address, correlation_id):
    payload = {"order_id": order_id, "user_id": user_id, "address": address}
    response = requests.post(
        f"{settings.SHIPPING_SERVICE_URL}/internal/shipping/create",
        json=payload,
        headers=_internal_headers("shipping-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "shipping-service")
    return response.json()


def clear_cart(user_id, correlation_id):
    response = requests.delete(
        f"{settings.CART_SERVICE_URL}/internal/cart/{user_id}/clear",
        headers=_internal_headers("cart-service", correlation_id),
        timeout=5,
    )
    _raise_for_response(response, "cart-service")
    return response.json()
```

*Lưu ý: đoạn trên tương ứng logic đầy đủ trong `order-service/app/service_clients.py` (cùng tệp còn có `ServiceClientError`, `_raise_for_response`, `_internal_headers`). Chuỗi JWT nội bộ do `build_internal_service_token` tạo trong `order-service/app/auth.py`.*

**Luồng tạo đơn (mô tả theo mã nguồn `app/views.py`, tóm lược bước nghiệp vụ):** (1) lấy `user_id` từ token; chuẩn hóa `X-Correlation-ID` (header hoặc sinh mới) phục vụ theo dõi; (2) gọi nội bộ lấy giỏ; nếu rỗng, trả lỗi 400; (3) với từng mục, gọi sản phẩm theo mã, kiểm tra tồn, cộng dồn thành tiền; (4) tạo đơn và dòng; (5) gọi thanh toán nội bộ, có tham số mô phỏng lỗi; nếu không thành công, đánh dấu đơn hủy, trả mã 402; (6) nếu thành công, tạo vận chuyển; cập nhật trạng thái đơn tương ứng trạng thái vận chuyển; (7) gọi xóa giỏ. Lỗi mạng hoặc lỗi từ dịch vụ ngoài có thể trả 502 kèm thông điệp hoặc thông tin đơn, tùy bước.

**Giao diện API:** danh sách và tạo đơn tại `orders/`; khách hàng chỉ thấy đơn thuộc mình, staff hoặc admin xem theo bộ lọc (ví dụ `user_id`). Chi tiết và cập nhật tại `orders/<pk>` (có cả biến thể đường dẫn với dấu gạch chéo cuối theo cấu hình urlconf). Cập nhật trạng thái đơn giới hạn cho staff hoặc admin. Định danh ngoài: JWT người dùng. Định danh nội bộ: token ký từ Order Service, `iss` = `order-service`, `service` theo tên cấu hình.

**Cơ sở dữ liệu.** MySQL, `order_db`. URL dịch vụ hạ tầng được cấu hình bằng biến môi trường (cart, product, payment, shipping).

---

<a id="muc-27"></a>

## 2.7 Thiết kế Payment Service

<a id="muc-271"></a>

### 2.7.1 Vai trò của service

Payment Service chịu trách nhiệm **bounded context thanh toán theo đơn hàng:** lưu bản ghi gồm `order_id` (tham chiếu logic tới Order Service), `user_id` (sở hữu, phục vụ phân quyền truy vấn), `amount` và `status`. Tách service giúp tách bạch bài toán thanh toán, kiểm thử kịch bản thất bại, và tách dữ liệu thanh toán với dữ liệu đơn hàng tại Order Service. Triển khai hiện tại mô phỏng kết quả thành công hoặc thất bại theo cờ nghiệp vụ, không tích hợp cổng thanh toán bên ngoài.

<a id="muc-272"></a>

### 2.7.2 Cấu trúc dữ liệu, API

**Mô hình dữ liệu:** bản ghi `Payment` tham chiếu logic `order_id`, `user_id`; không Foreign Key tới cơ sở dữ liệu Order.

**Minh chứng mã nguồn — toàn bộ model (`payment-service/app/models.py`):**

```python
from django.db import models


class Payment(models.Model):
    STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Success", "Success"),
        ("Failed", "Failed"),
    )

    order_id = models.IntegerField()
    user_id = models.IntegerField()
    amount = models.FloatField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Pending")
```

**Minh chứng mã nguồn — định tuyến (`payment-service/app/urls.py`):**

```python
from django.urls import path

from .views import InternalPaymentProcessView, PaymentStatusDetailView, PaymentStatusListView

urlpatterns = [
    path("internal/payment/pay", InternalPaymentProcessView.as_view(), name="payment-pay"),
    path("payment/status", PaymentStatusListView.as_view(), name="payment-status"),
    path("payment/status/<int:order_id>", PaymentStatusDetailView.as_view(), name="payment-status-detail"),
]
```

**Giao diện API:** (1) `POST` nội bộ tới endpoint xử lý thanh toán, chỉ chấp nhận JWT dịch vụ, thân yêu cầu gồm mã đơn, mã người dùng, số tiền và tùy chọn mô phỏng thất bại; (2) `GET` danh sách trạng thái theo nghiệp vụ: khách chỉ thấy bản ghi của mình, staff hoặc admin xem tập rộng hơn, có hỗ trợ lọc theo `order_id` khi thuộc quyền; (3) `GET` chi tiết theo `order_id` (bản ghi mới nhất theo mã nguồn), với kiểm tra sở hữu: khác `user_id` thì giao diện trả trạng thái “không tìm thấy” theo cách dùng lớp tương ứng.

**Cơ sở dữ liệu:** MySQL, `payment_db`. Xác thực public: JWT người dùng. Xác thực nội bộ: cùng mẫu `InternalServiceAuthentication` với `audience` = `payment-service`.

---

<a id="muc-28"></a>

## 2.8 Thiết kế Shipping Service

<a id="muc-281"></a>

### 2.8.1 Vai trò của service

Shipping Service đảm nhiệm **bounded context vận chuyển:** lưu thông tin giao hàng theo từng `order_id`, kèm `user_id` (kiểm soát truy cập) và trường văn bản `address`, cùng `status` (Processing, Shipping, Delivered theo mã nguồn). Tách service cho phép mở rộng quy trình giao hàng, cập nhật trạng thái vận hành mà không trộn lẫn với Product hoặc Payment.

**Liên hệ với Order Service:** tạo bản ghi vận chuyển qua lời gọi nội bộ từ Order Service (phương thức `POST` với payload chứa mã đơn, mã người dùng và địa chỉ).

<a id="muc-282"></a>

### 2.8.2 Cấu trúc dữ liệu, API

**Mô hình dữ liệu:** bảng ghi thông tin giao hàng, trạng thái theo lựa chọn đã khai báo.

**Minh chứng mã nguồn — toàn bộ model (`shipping-service/app/models.py`):**

```python
from django.db import models


class Shipment(models.Model):
    STATUS_CHOICES = (
        ("Processing", "Processing"),
        ("Shipping", "Shipping"),
        ("Delivered", "Delivered"),
    )

    order_id = models.IntegerField()
    user_id = models.IntegerField()
    address = models.TextField()
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Processing")
```

**Minh chứng mã nguồn — định tuyến (`shipping-service/app/urls.py`):**

```python
from django.urls import path

from .views import InternalShipmentCreateView, ShipmentStatusDetailView, ShipmentStatusListView

urlpatterns = [
    path("internal/shipping/create", InternalShipmentCreateView.as_view(), name="shipping-create"),
    path("shipping/status", ShipmentStatusListView.as_view(), name="shipping-status"),
    path("shipping/status/<int:order_id>", ShipmentStatusDetailView.as_view(), name="shipping-status-detail"),
]
```

**Giao diện API:** (1) tạo nội bộ qua `internal/shipping/create`, JWT dịch vụ; (2) liệt kê `shipping/status` với phân quyền tương tự mô tả ở Payment; (3) tra cứu và cập nhật `shipping/status/<order_id>` — khách hàng không đọc được bản ghi của người khác; cập nhật trạng thái chỉ dành cho staff hoặc admin.

**Cơ sở dữ liệu:** MySQL, `shipping_db`.

---

<a id="muc-bang-tong-hop"></a>

## Bảng tổng hợp kiến trúc

| Nội dung | Cách thể hiện trong dự án |
|----------|---------------------------|
| Mỗi service một cơ sở dữ liệu | `docker-compose.yml` khai báo từng container DB; `product_db` (PostgreSQL) và năm MySQL tương ứng từng dịch vụ. |
| Không Foreign Key xuyên service | Tham chiếu `user_id`, `product_id`, `order_id` kiểu số nguyên. |
| JWT người dùng | Phát từ User Service; tiêu thụ bởi DRF (Simple JWT, stateless). |
| JWT nội bộ (service-to-service) | HMAC HS256, `issuer` từ Order Service, `audience` theo từng dịch vụ, claim `service` xác định tên dịch vụ gọi. |
| Giao tiếp giữa các service | Chủ yếu do Order Service gọi qua thư viện HTTP, header nội bộ `Authorization` và `X-Correlation-ID`. |
| Tài liệu giao diện người dùng | Tài liệu `docs/frontend-ui-overview.md` mô tả ứng dụng Next.js — tham chiếu chéo nếu báo cáo cần nêu tầng trình bày, nằm ngoài mục 2.3–2.8 nếu chỉ tập trung backend. |

---

*Tài liệu này có thể đưa trực tiếp vào phần thân chương 2 của báo cáo tiểu luận, hoặc chuyển sang định dạng sách giáo khoa (Word/LaTeX) theo yêu cầu định dạng của cơ sở đào tạo.*
