# PHỤ LỤC MÃ NGUỒN - PHIÊN BẢN V2

Phụ lục này tập trung vào các đoạn mã mang giá trị kiến trúc, bảo mật, điều phối nghiệp vụ và tích hợp hệ thống. Mỗi đoạn mã đi kèm mục đích và nhận xét ngắn để thuận tiện tra cứu khi đọc báo cáo chính.

## 1) Gateway

### Excerpt 1.1 - Chặn route nội bộ và chuyển tiếp auth header

- **File:** `gateway/nginx.conf`
- **Khối mã:** internal-route guard + proxy header forwarding
- **Dòng:** 93-106
- **Mục đích:** cô lập endpoint nội bộ, duy trì trust flow JWT qua gateway

```nginx
location ~ ^/api/(products|cart|orders|payments|shipping|ai)/internal/ {
    default_type application/json;
    return 403 '{"detail":"Internal routes are not publicly accessible through the gateway."}';
}

location /api/users/auth/ {
    rewrite ^/api/users/auth/(.*)$ /auth/$1 break;
    proxy_pass http://user_service;
    proxy_set_header X-Correlation-ID $effective_correlation_id;
    proxy_set_header Authorization $http_authorization;
}
```

Đoạn cấu hình này thể hiện rõ triết lý “policy ở ingress”: route nội bộ bị đóng ở biên công khai, trong khi JWT được chuyển tiếp để downstream tiếp tục xác thực theo miền trách nhiệm.

### Excerpt 1.2 - Định dạng log ingress có correlation context

- **File:** `gateway/nginx.conf`
- **Khối mã:** `log_format chapter4_main`
- **Dòng:** 11-19
- **Mục đích:** hỗ trợ truy vết request qua ingress và upstream

```nginx
log_format chapter4_main
    '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for" '
    'rt=$request_time ua="$upstream_addr" us="$upstream_status" '
    'urt="$upstream_response_time" cid="$http_x_correlation_id"';
```

Việc đưa `cid` và thời gian upstream vào log format tạo nền tảng cho phân tích sự cố liên service ở mức tối thiểu.

## 2) Authentication và RBAC

### Excerpt 2.1 - Phát JWT kèm role claim

- **File:** `user-service/app/serializers.py`
- **Khối mã:** `LoginSerializer.get_token`
- **Dòng:** 52-59
- **Mục đích:** gắn thông tin phân quyền vào token cho downstream authorization

```python
class LoginSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["user_id"] = user.id
        token["id"] = user.id
        return token
```

Role claim giúp giảm phụ thuộc vào truy vấn user service trong mọi request protected.

### Excerpt 2.2 - RBAC ở route quản trị user

- **File:** `user-service/app/views.py`
- **Khối mã:** `UserListView`
- **Dòng:** 32-35
- **Mục đích:** thể hiện ràng buộc quyền admin ở endpoint nhạy cảm

```python
class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAdmin]
```

Điểm này là nền tảng cho phân tách vai trò admin/staff/customer trong toàn hệ thống.

## 3) Service Communication

### Excerpt 3.1 - Request wrapper cho orchestration

- **File:** `order-service/app/service_clients.py`
- **Khối mã:** `_send_request(...)`
- **Dòng:** 30-96
- **Mục đích:** thống nhất timeout, retry và lỗi gọi service

```python
def _send_request(..., retries=1, json=None):
    attempts = max(1, retries)
    timeout_seconds = settings.SERVICE_CLIENT_TIMEOUT_SECONDS
    ...
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=json,
        timeout=timeout_seconds,
    )
    _raise_for_response(response, service_name)
```

Đây là điểm quan trọng về maintainability: cùng một chiến lược gọi service được tái sử dụng cho toàn bộ luồng checkout.

## 4) End-to-End Orchestration

### Excerpt 4.1 - Điều phối trạng thái order theo payment/shipping

- **File:** `order-service/app/views.py`
- **Khối mã:** `OrderListCreateView.create`
- **Dòng:** 72-96
- **Mục đích:** bảo đảm trạng thái đơn hàng bám kết quả downstream

```python
payment = create_payment(order.id, user_id, total_price, correlation_id, data["simulate_payment_failure"])
if payment["status"] != "Success":
    order.status = "Cancelled"
    order.save(update_fields=["status"])
    return Response(OrderSerializer(order).data, status=status.HTTP_402_PAYMENT_REQUIRED)

order.status = "Paid"
order.save(update_fields=["status"])

shipment = create_shipment(order.id, user_id, data["address"], correlation_id)
if shipment["status"] in {"Processing", "Shipping", "Delivered"}:
    order.status = "Shipping"
    order.save(update_fields=["status"])
```

Thiết kế này cho phép phản ánh cả nhánh thất bại mà không làm sai lệch trạng thái nghiệp vụ.

## 5) Docker và Topology

### Excerpt 5.1 - Compose network và gateway integration

- **File:** `docker-compose.yml`
- **Khối mã:** `x-app-network`, `gateway`, `networks`
- **Dòng:** 7-9, 281-294, 325-327
- **Mục đích:** biểu diễn topology tích hợp của toàn hệ thống

```yaml
x-app-network: &app-network
  networks:
    - ecom-network

services:
  gateway:
    build: ./gateway
    ports:
      - "8080:80"
    depends_on:
      - user-service
      - product-service
      - cart-service
      - order-service
      - payment-service
      - shipping-service
      - ai-service

networks:
  ecom-network:
    driver: bridge
```

Tập trung service vào cùng một network giúp tái lập đúng quan hệ runtime khi đánh giá kiến trúc.

## 6) AI Integration

### Excerpt 6.1 - API AI trở thành first-class routes

- **File:** `ai-service/app/main.py`
- **Khối mã:** router registration
- **Dòng:** 37-42
- **Mục đích:** thể hiện AI service có surface API hoàn chỉnh trong hệ thống

```python
app.include_router(health_router)
app.include_router(behavior_router)
app.include_router(graph_router)
app.include_router(rag_router)
app.include_router(recommend_router)
app.include_router(chatbot_router)
```

Đoạn mã xác nhận AI không chỉ là pipeline offline, mà là lớp dịch vụ online phục vụ truy vấn.

### Excerpt 6.2 - Frontend gọi AI qua API thống nhất

- **File:** `frontend/lib/ai.ts`
- **Khối mã:** `fetchRecommendations`, `sendChatbotMessage`, `trackBehaviorEvent`
- **Dòng:** 28-74
- **Mục đích:** chứng minh AI được tích hợp ở tầng client theo contract chung

```typescript
const response = await api.get("/ai/recommend", {
  params: { user_id: userId, limit, query: query || undefined },
});

const chatbot = await api.post("/ai/chatbot", {
  user_id: userId,
  message,
});
```

Luồng frontend -> gateway -> ai-service giúp AI trở thành một phần tự nhiên của trải nghiệm người dùng.

## 7) Product Scope mở rộng

### Excerpt 7.1 - 10 nhóm loại sản phẩm

- **File:** `product-service/app/product_types.py`
- **Khối mã:** `PRODUCT_TYPE_SCHEMAS`
- **Dòng:** 1-82
- **Mục đích:** phản ánh phạm vi catalog mở rộng của triển khai thật

```python
PRODUCT_TYPE_SCHEMAS = {
    "book": {...},
    "electronics": {...},
    "fashion": {...},
    "home-living": {...},
    "beauty": {...},
    "sports": {...},
    "toys": {...},
    "grocery": {...},
    "office": {...},
    "pet-supplies": {...},
}
```

Nội dung này làm rõ sự khác biệt giữa bài toán minh họa nhỏ và hệ thống đã mở rộng dữ liệu domain.

## 8) Script kiểm chứng hệ thống

### Excerpt 8.1 - End-to-end script xác minh cả nhánh thất bại

- **File:** `scripts/e2e_checkout_flow.ps1`
- **Khối mã:** `-SimulatePaymentFailure` và kiểm tra trạng thái
- **Dòng:** 181-233
- **Mục đích:** xác nhận luồng checkout được kiểm tra có điều kiện lỗi

```powershell
$order = Invoke-JsonRequestAllowFailureStatus -Method POST -Url $ordersUrl -AllowedStatusCodes @(402) ...
if ($SimulatePaymentFailure) {
    if ($ownerOrder.status -ne "Cancelled") { throw ... }
    if ($paymentStatus.status -ne "Failed") { throw ... }
}
```

Khối script này giúp đánh giá hệ thống ở cả positive path và negative path.

### Excerpt 8.2 - RBAC script theo hành vi truy cập

- **File:** `scripts/auth_rbac_check.ps1`
- **Khối mã:** `Invoke-ExpectStatus` cho 401/403 và gọi admin route
- **Dòng:** 96-111
- **Mục đích:** kiểm chứng tính đúng của protected route và role policy

```powershell
$protectedRouteWithoutToken = Invoke-ExpectStatus -Method GET -Url $cartUrl -ExpectedStatus 401
$adminRouteWithCustomerToken = Invoke-ExpectStatus -Method GET -Url $adminUsersUrl -ExpectedStatus 403 -Headers $customerHeaders
$adminUsers = Invoke-JsonRequest -Method GET -Url $adminUsersUrl -Headers $adminHeaders
```

Kiểm tra theo kỳ vọng HTTP status là cách đối chiếu đơn giản nhưng hiệu quả cho bài toán phân quyền.
