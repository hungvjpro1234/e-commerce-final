# PHỤ LỤC A - CODE EXCERPTS

Phụ lục này gom các đoạn mã cốt lõi phục vụ đối chiếu nhanh với báo cáo Chương 4. Các đoạn mã được rút gọn có chủ đích, chỉ giữ phần chứng minh yêu cầu.

## A1. Gateway

### Excerpt A1.1 - Chặn internal routes và map public routes

- **File:** `gateway/nginx.conf`
- **Khối mã:** internal route guard + users/payments/ai proxy
- **Line:** 93-106, 190-225
- **Mục đích:** chứng minh gateway là single entry point, có route governance

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

location /api/payments/ {
    rewrite ^/api/payments/(.*)$ /payment/$1 break;
    proxy_pass http://payment_service;
}

location /api/ai/ {
    rewrite ^/api/ai/(.*)$ /$1 break;
    proxy_pass http://ai_service;
}
```

**Phân tích:** gateway vừa đảm bảo route công khai ổn định vừa bảo vệ endpoint nội bộ. Cách này hỗ trợ loose coupling giữa client và topology nội bộ.

## A2. Authentication và RBAC

### Excerpt A2.1 - JWT claims mở rộng

- **File:** `user-service/app/serializers.py`
- **Khối mã:** `LoginSerializer.get_token`
- **Line:** 52-59
- **Mục đích:** chứng minh JWT chứa role/user context cho authorize phân tán

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

**Phân tích:** claim-level authorization giúp giảm round-trip identity lookup ở downstream services.

### Excerpt A2.2 - Admin-only route

- **File:** `user-service/app/views.py`
- **Khối mã:** `UserListView`
- **Line:** 32-35
- **Mục đích:** chứng minh RBAC được enforce tại view layer

```python
class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAdmin]
```

**Phân tích:** role `admin` được ràng buộc rõ ràng cho route quản trị user.

## A3. Service Communication

### Excerpt A3.1 - HTTP wrapper với timeout/retry/log

- **File:** `order-service/app/service_clients.py`
- **Khối mã:** `_send_request(...)`
- **Line:** 30-96
- **Mục đích:** chứng minh best practice giao tiếp liên service

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

**Phân tích:** wrapper thống nhất hành vi network và lỗi, tăng khả năng bảo trì và quan sát của orchestration layer.

## A4. E2E Workflow (Order -> Payment -> Shipping)

### Excerpt A4.1 - Nhánh success/failure khi checkout

- **File:** `order-service/app/views.py`
- **Khối mã:** `OrderListCreateView.create`
- **Line:** 72-96
- **Mục đích:** chứng minh luồng nghiệp vụ và state transition

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

**Phân tích:** orchestration thể hiện rõ branching theo kết quả payment, là bằng chứng trung tâm cho checklist flow liên service.

## A5. Docker và Deployment

### Excerpt A5.1 - Tích hợp gateway vào compose network

- **File:** `docker-compose.yml`
- **Khối mã:** `gateway` service + `ecom-network`
- **Line:** 281-294, 325-327
- **Mục đích:** chứng minh gateway là thành phần runtime thật, không chỉ tài liệu

```yaml
gateway:
  build: ./gateway
  container_name: gateway
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

**Phân tích:** mô hình compose đảm bảo topology tích hợp đúng tinh thần Chapter 4.

## A6. AI Integration

### Excerpt A6.1 - Đăng ký router AI service

- **File:** `ai-service/app/main.py`
- **Khối mã:** `app.include_router(...)`
- **Line:** 37-42
- **Mục đích:** chứng minh AI service là API surface thật cho behavior/graph/rag/recommend/chatbot

```python
app.include_router(health_router)
app.include_router(behavior_router)
app.include_router(graph_router)
app.include_router(rag_router)
app.include_router(recommend_router)
app.include_router(chatbot_router)
```

**Phân tích:** AI không phải script rời; đây là service API có lifecycle và router rõ ràng.

## A7. Product Scope (10 nhóm sản phẩm)

### Excerpt A7.1 - PRODUCT_TYPE_SCHEMAS

- **File:** `product-service/app/product_types.py`
- **Khối mã:** `PRODUCT_TYPE_SCHEMAS`
- **Line:** 1-82
- **Mục đích:** chứng minh product-service đã mở rộng 10 nhóm sản phẩm trong triển khai thực tế

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

**Phân tích:** đây là bằng chứng trực tiếp cho phạm vi catalog nâng cao, quan trọng để khớp bối cảnh Chương 4.

## A8. Logging và Health

### Excerpt A8.1 - Health endpoint tại business service

- **File:** `order-service/app/views.py`
- **Khối mã:** `HealthCheckView`
- **Line:** 133-137
- **Mục đích:** chứng minh service-level health phục vụ monitoring tối thiểu

```python
class HealthCheckView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response({"service": "order-service", "status": "ok"})
```

**Phân tích:** health endpoint lightweight nhưng đủ phục vụ smoke-check qua gateway.

### Excerpt A8.2 - Logging format của gateway

- **File:** `gateway/nginx.conf`
- **Khối mã:** `log_format chapter4_main`
- **Line:** 11-19
- **Mục đích:** chứng minh có logging ingress-level để truy vết request/upstream/correlation

```nginx
log_format chapter4_main
    '$remote_addr - $remote_user [$time_local] "$request" '
    '$status $body_bytes_sent "$http_referer" '
    '"$http_user_agent" "$http_x_forwarded_for" '
    'rt=$request_time ua="$upstream_addr" us="$upstream_status" '
    'urt="$upstream_response_time" cid="$http_x_correlation_id"';
```

**Phân tích:** log format mang đủ trường để audit latency và trace theo correlation id.

## A9. Ghi chú sử dụng phụ lục

- Đối chiếu runtime nên mở kèm `docs/chapter4/APPENDIX_EVIDENCE_INDEX.md`.
- Nếu cần xem flow đầy đủ thay vì excerpt rút gọn, mở trực tiếp các file nguồn đã nêu trong metadata từng mục.
