# CHƯƠNG 4. XÂY DỰNG HỆ THỐNG HOÀN CHỈNH

Báo cáo này được xây dựng theo nguyên tắc code-first và evidence-first, dựa trên mã nguồn hiện có trong repository và bộ minh chứng runtime tại `docs/chapter4/evidence`, `docs/chapter4/logs`, `docs/chapter4/screenshots`.

## 4.1 Kiến trúc tổng thể

### 4.1.1 Mô hình hệ thống

Hệ thống triển khai theo kiến trúc microservices với lớp truy cập tập trung qua Nginx Gateway, bao gồm các dịch vụ: `user-service`, `product-service`, `cart-service`, `order-service`, `payment-service`, `shipping-service`, `ai-service`, `frontend` và các datastore riêng biệt.

Điểm cần nhấn mạnh theo bối cảnh triển khai thật: `product-service` đã được mở rộng thành **10 nhóm loại sản phẩm** thay vì mô hình minh họa tối giản.

| Service | Vai trò chính | CSDL | Port/service route chính |
| --- | --- | --- | --- |
| `gateway` | Single entry point, routing, header forwarding, block internal route | Không sở hữu business DB | `:8080` -> `/api/*` |
| `user-service` | Đăng ký/đăng nhập, phát JWT, quản trị user | MySQL `user_db` | `:8002`, `/auth/*`, `/users/*`, `/health` |
| `product-service` | Danh mục sản phẩm, category, internal product lookup | PostgreSQL `product_db` | `:8001`, `/products*`, `/categories*`, `/health` |
| `cart-service` | Giỏ hàng khách hàng + internal cart API | MySQL `cart_db` | `:8003`, `/cart/*`, `/health` |
| `order-service` | Điều phối checkout, trạng thái đơn hàng | MySQL `order_db` | `:8004`, `/orders/*`, `/health` |
| `payment-service` | Xử lý/truy vấn thanh toán | MySQL `payment_db` | `:8005`, `/payment/*`, `/health` |
| `shipping-service` | Tạo/truy vấn vận chuyển | MySQL `shipping_db` | `:8006`, `/shipping/*`, `/health` |
| `ai-service` | Recommend/chatbot/behavior/graph/RAG | PostgreSQL `ai_db` + Neo4j | `:8007`, `/recommend`, `/chatbot`, `/health` |
| `frontend` | Giao diện người dùng | Không sở hữu business DB | `:3000` |

### 4.1.2 Nguyên tắc

- **Database-per-service**: mỗi service business dùng database riêng trong `docker-compose.yml`.
- **REST API communication**: giao tiếp liên service qua HTTP nội bộ, thể hiện rõ tại `order-service/app/service_clients.py`.
- **Không truy cập DB chéo service**: orchestration gọi API nội bộ, không có ORM cross-service.
- **Loose coupling và fault isolation**: lỗi downstream được chuẩn hóa thành `ServiceClientError` và trả về `502` ở service gọi.
- **Scalability theo chiều ngang**: service stateless có thể scale độc lập sau gateway trong cùng network Docker.

## 4.2 System Architecture

### 4.2.1 Overview

Từ góc nhìn hệ phân tán, `CHAP2_E-COMMERCE` đã đạt kiến trúc đa dịch vụ có phân tách miền nghiệp vụ rõ ràng, lớp ingress độc lập và tích hợp AI như một service first-class. Kiến trúc này không dừng ở tài liệu: các flow nghiệp vụ, auth, gateway và AI đều có bằng chứng chạy thật dạng JSON/log/screenshot.

### 4.2.2 Microservice Architecture

- `user-service`: identity provider + RBAC claim source.
- `product-service`: catalog nguồn dữ liệu chuẩn cho toàn hệ thống và AI.
- `cart-service`: trạng thái giỏ hàng theo user.
- `order-service`: orchestrator checkout đồng bộ.
- `payment-service`, `shipping-service`: dịch vụ tác vụ downstream.
- `ai-service`: tích hợp recommendation/chatbot qua gateway.
- `gateway`: điểm vào chung, điều phối route và bảo vệ route nội bộ.

Ghi chú phạm vi: kiến trúc hiện không có `notification-service` chuyên biệt; phạm vi đồ án tập trung vào checkout và AI integration.

### 4.2.3 API Gateway

Gateway thực thi vai trò single entry point tại `gateway/nginx.conf`:
- map `/api/users|products|cart|orders|payments|shipping|ai`
- forward `Authorization` và `X-Correlation-ID`
- thêm security headers
- block public access tới route nội bộ (`/internal/*`)
- hỗ trợ `/health` của gateway

### 4.2.4 Service Communication

Mô hình chính là synchronous REST. Luồng order -> payment -> shipping đi qua `order-service` (orchestration), không gọi trực tiếp payment -> shipping.

Code wrapper có timeout/retry/log tập trung:
- timeout: `SERVICE_CLIENT_TIMEOUT_SECONDS`
- retry có chọn lọc cho GET/DELETE idempotent
- không retry POST side-effect (`create_payment`, `create_shipment`)

### 4.2.5 Containerization and Deployment

Hệ thống được Docker hóa đầy đủ, có:
- `Dockerfile` cho các service chính (Django/FastAPI/Next.js/Gateway)
- `docker-compose.yml` tích hợp toàn stack
- network chung `ecom-network`
- env dùng theo mô hình root `.env.example` + per-service `.env.example`

### 4.2.6 System Structure

Cấu trúc thư mục thực tế bám sát tinh thần đề:

```text
gateway/
user-service/
product-service/
cart-service/
order-service/
payment-service/
shipping-service/
ai-service/
frontend/
infrastructure/monitoring/
docs/chapter4/
scripts/
docker-compose.yml
```

### 4.2.7 Design Principles

- **Loose coupling**: downstream gọi qua API client, không import model lẫn nhau.
- **High cohesion**: từng service tập trung đúng miền nghiệp vụ.
- **Scalability**: gateway + service độc lập giúp scale theo hotspot.
- **Fault isolation**: timeout/error downstream không làm sập toàn hệ, được chặn/translate ở lớp orchestration.

### 4.2.8 Security Considerations

- User JWT phát tại `user-service`, kèm claim `role`, `user_id`.
- Gateway pass-through `Authorization`; verify JWT và RBAC ở downstream service.
- RBAC phân vai `admin/staff/customer` trên route protected.
- Route nội bộ bị chặn từ gateway (`403`) để giảm bề mặt tấn công.

### 4.2.9 Discussion

**Ưu điểm**:
- Có kiến trúc vận hành thật, không chỉ mô tả.
- Boundaries rõ, AI tích hợp qua gateway thay vì đứng riêng.
- Có evidence runtime định lượng và flow success/failure.

**Hạn chế**:
- Chưa triển khai event bus/circuit breaker.
- Monitoring mới ở mức skeleton (chưa chạy full Prometheus/Grafana trong compose).
- Benchmark hiệu năng hiện tại là lightweight single-client, không phải load test production-grade.

## 4.3 API Gateway (Nginx)

### 4.3.1 Vai trò

Gateway là ingress thống nhất cho backend API, chuẩn hóa route prefix công khai và cô lập endpoint nội bộ orchestration.

### 4.3.2 Cấu hình mẫu

**File:** `gateway/nginx.conf`  
**Khối mã:** route mapping + block internal routes + header forwarding  
**Line:** 93-106, 190-225  
**Mục đích:** chứng minh gateway thực thi định tuyến, bảo vệ route nội bộ và truyền auth/correlation header

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
    proxy_set_header X-Correlation-ID $effective_correlation_id;
    proxy_set_header Authorization $http_authorization;
}

location /api/ai/ {
    rewrite ^/api/ai/(.*)$ /$1 break;
    proxy_pass http://ai_service;
    proxy_set_header X-Correlation-ID $effective_correlation_id;
    proxy_set_header Authorization $http_authorization;
}
```

**Mô tả kỹ thuật:** cấu hình dùng rewrite + upstream để chuẩn hóa contract `/api/*` ra các route backend hiện có; đồng thời chặn family `internal` ở edge layer.  
**Liên hệ đề bài:** đáp ứng yêu cầu API Gateway Nginx, single entry point, routing, auth propagation.  
**Bình luận học thuật:** đặt enforcement ở gateway giúp giảm coupling giữa client và nội bộ orchestration, đồng thời tăng tính kiểm soát policy tập trung.

**Evidence chính:**  
- `docs/chapter4/evidence/health-check.json`  
- `docs/chapter4/screenshots/gateway-health.png`  
- `docs/chapter4/logs/runtime-logs.txt`

## 4.4 Authentication (JWT)

### 4.4.1 Cài đặt

JWT triển khai theo `rest_framework_simplejwt` ở `user-service`; token issue tại login endpoint.

### 4.4.2 Cấu hình

**File:** `user-service/app/serializers.py`  
**Khối mã:** `LoginSerializer.get_token()`  
**Line:** 52-64  
**Mục đích:** chứng minh token chứa claim phục vụ RBAC và trace user

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

**Mô tả kỹ thuật:** token nhúng role/user id để downstream authorize mà không phải round-trip tới user service mỗi request.  
**Liên hệ đề bài:** đáp ứng yêu cầu JWT auth + role claims.  
**Bình luận học thuật:** giải pháp stateless token phù hợp hệ phân tán vì giảm phụ thuộc đồng bộ vào identity service.

### 4.4.3 Luồng

1. Client login qua `/api/users/auth/login` (gateway -> user-service).  
2. User-service trả access/refresh token.  
3. Client gửi `Authorization: Bearer ...` cho route protected.  
4. Gateway pass-through header.  
5. Service đích verify JWT và kiểm tra RBAC.

**Code RBAC mẫu**

**File:** `user-service/app/views.py`  
**Khối mã:** admin-only user management  
**Line:** 32-49  
**Mục đích:** chứng minh enforce quyền `IsAdmin`

```python
class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAdmin]
```

**Evidence chính:**  
- `docs/chapter4/evidence/auth-rbac-check.json` (401 không token, 403 customer vào admin route, 200 admin)  
- `docs/chapter4/evidence/role-flows-check.json`

## 4.5 Giao tiếp giữa các Service

### 4.5.1 REST API call

`order-service` thực hiện orchestration checkout qua các call nội bộ: cart -> product -> payment -> shipping -> clear cart.

### 4.5.2 Best Practice

**File:** `order-service/app/service_clients.py`  
**Khối mã:** `_send_request` wrapper  
**Line:** 30-96  
**Mục đích:** chứng minh timeout/retry/log/error handling tập trung

```python
def _send_request(
    *,
    service_name,
    method,
    url,
    headers,
    correlation_id,
    retries=1,
    json=None,
):
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

**Mô tả kỹ thuật:** wrapper chuẩn hóa timeout, logging, retry cho call idempotent; translate lỗi network/HTTP thành `ServiceClientError`.  
**Liên hệ đề bài:** đáp ứng yêu cầu giao tiếp service + best practice ở mức đồ án.  
**Bình luận học thuật:** cách làm tăng maintainability và khả năng quan sát, dù chưa đạt mức circuit-breaker.

**Trung thực phạm vi:** chưa có circuit breaker/event-driven async; đây là phần nâng cao (optional/production hardening).

## 4.6 Docker hóa hệ thống

### 4.6.1 Dockerfile

Các service chính đã có `Dockerfile` riêng, gồm cả `gateway/Dockerfile` và `ai-service/Dockerfile`.

### 4.6.2 docker-compose.yml

**File:** `docker-compose.yml`  
**Khối mã:** network + gateway + service declarations  
**Line:** 7-11, 281-294, 325-327  
**Mục đích:** chứng minh tích hợp full stack qua Docker Compose

```yaml
x-app-network: &app-network
  networks:
    - ecom-network

services:
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

**Mô tả kỹ thuật:** gateway được đưa vào compose như ingress thực; toàn bộ service nằm cùng network nội bộ phục vụ service discovery theo container name.  
**Liên hệ đề bài:** đáp ứng tiêu chí docker hóa đầy đủ và compose orchestration.  
**Bình luận học thuật:** mô hình này phù hợp môi trường dev/test và tái lập minh chứng; production có thể cần orchestration cấp cao hơn.

**Evidence chính:**  
- `docs/chapter4/logs/compose-ps.txt`  
- `docs/chapter4/logs/network-inspect.json`  
- `docs/chapter4/logs/runtime-logs.txt`

## 4.7 Luồng hệ thống (End-to-End)

### 4.7.1 Use case: Mua hàng

Flow kiểm chứng qua `scripts/e2e_checkout_flow.ps1`:
1. login  
2. browse product  
3. add cart  
4. create order  
5. payment  
6. shipping

### 4.7.2 Sequence logic

**File:** `order-service/app/views.py`  
**Khối mã:** `OrderListCreateView.create`  
**Line:** 33-106  
**Mục đích:** chứng minh orchestration success/failure path

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

**Mô tả kỹ thuật:** xử lý phân nhánh nghiệp vụ rõ ràng: payment fail -> cancel order; payment success -> tạo shipment -> cập nhật shipping.  
**Liên hệ đề bài:** đáp ứng yêu cầu flow order -> payment -> shipping với cả nhánh thành công/thất bại.  
**Bình luận học thuật:** orchestration tập trung tại order-service giúp giữ logic chuyển trạng thái nhất quán, đổi lại làm tăng coupling đồng bộ ở checkout path.

**Evidence success:** `docs/chapter4/evidence/e2e-checkout-success.json` (`order_status=Shipping`, `payment_status=Success`, `shipping_status=Processing`).  
**Evidence failure:** `docs/chapter4/evidence/e2e-checkout-payment-failure.json` (`order_status=Cancelled`, `payment_status=Failed`).

## 4.8 Triển khai Kubernetes (Optional)

Trong codebase hiện tại **chưa có manifest Kubernetes hoàn chỉnh** cho toàn stack Chapter 4. Phạm vi chính đang là Docker Compose.

Đánh giá trung thực:
- Đã có nền tảng container hóa tốt để chuyển tiếp sang K8s.
- Chưa có bằng chứng triển khai K8s runtime trong bộ evidence hiện tại.
- Hướng mở rộng: bổ sung `Deployment`, `Service`, `ConfigMap`, `Ingress` theo mapping từ `docker-compose.yml`.

## 4.9 Logging và Monitoring

Logging hiện có:
- Gateway access/error log trong `nginx.conf`.
- Logging settings ở các service Django (`LOGGING` trong `config/settings.py`).
- AI service có `logging.basicConfig(...)` trong `ai-service/app/main.py`.

Health monitoring hiện có:
- `/health` cho gateway và các service chính.
- script kiểm tra tổng hợp: `scripts/health_check.ps1`.

Monitoring nâng cao:
- Có skeleton tại `infrastructure/monitoring/prometheus.yml`.
- Chưa triển khai full metrics pipeline Prometheus/Grafana trong compose.

**Evidence chính:**  
- `docs/chapter4/evidence/health-check.json`  
- `docs/chapter4/logs/runtime-logs.txt`  
- `docs/chapter4/08-observability.md`

## 4.10 Đánh giá hệ thống

### 4.10.1 Hiệu năng

Dựa trên `docs/chapter4/evidence/basic-system-eval.json` (12 iterations):
- `GET /health`: avg `10.31 ms`, p95 `114.79 ms`
- `GET /api/products/products`: avg `13.78 ms`, p95 `19.62 ms`
- `GET /api/ai/recommend`: avg `75.57 ms`, p95 `134.32 ms`

### 4.10.2 Khả năng mở rộng

- Có thể scale theo service vì boundary rõ và stateless API layer.
- AI tách deployment unit độc lập (DB + Neo4j riêng).
- Rủi ro scale chính: checkout orchestration đồng bộ và thiếu queue/event-driven.

### 4.10.3 Ưu điểm

- Kiến trúc và flow có minh chứng chạy thật.
- Auth + RBAC thể hiện rõ bằng JSON test.
- AI tích hợp trực tiếp qua gateway, không tách rời khỏi hệ thống thương mại điện tử.

### 4.10.4 Nhược điểm

- Monitoring mới mức nền tảng.
- Chưa có circuit breaker/event bus.
- Số liệu benchmark chưa đại diện tải đồng thời lớn.

## 4.11 Bài tập thực hành / Kết quả thực hiện

Theo tinh thần đề bài, kết quả thực thi thực tế đã đạt:
- Triển khai hệ service bằng Django/FastAPI.
- Kết nối service qua REST API và gateway Nginx.
- Docker hóa full stack bằng `docker-compose.yml`.
- Kiểm chứng flow mua hàng đầy đủ qua script E2E và evidence JSON.
- Tích hợp AI recommendation/chatbot vào kiến trúc chung và gọi qua gateway.

Các script thực hành tiêu biểu:
- `scripts/e2e_checkout_flow.ps1`
- `scripts/auth_rbac_check.ps1`
- `scripts/health_check.ps1`
- `scripts/ai_gateway_demo.ps1`
- `scripts/basic_system_eval.ps1`

## 4.12 Checklist đánh giá

| Tiêu chí | Trạng thái | Code chính | Evidence chính |
| --- | --- | --- | --- |
| Có API Gateway | Đạt | `gateway/nginx.conf`, `docker-compose.yml` | `docs/chapter4/evidence/health-check.json`, `docs/chapter4/screenshots/gateway-health.png` |
| Có JWT Auth | Đạt | `user-service/app/serializers.py`, `user-service/app/views.py` | `docs/chapter4/evidence/auth-rbac-check.json` |
| Có Docker chạy được | Đạt | `docker-compose.yml`, các `Dockerfile` | `docs/chapter4/logs/compose-ps.txt`, `docs/chapter4/logs/network-inspect.json` |
| Có flow order -> payment -> shipping | Đạt | `order-service/app/views.py`, `order-service/app/service_clients.py` | `docs/chapter4/evidence/e2e-checkout-success.json`, `docs/chapter4/evidence/e2e-checkout-payment-failure.json` |
| Có AI integration từ Chương 3 vào Chương 4 | Đạt | `ai-service/app/main.py`, `gateway/nginx.conf`, `scripts/ai_gateway_demo.ps1` | `docs/chapter4/evidence/ai-gateway-demo.json`, `docs/chapter4/screenshots/ai-recommend-api.png` |
| Logging/health cơ bản | Đạt (mức đồ án) | `gateway/nginx.conf`, `*/config/settings.py`, `scripts/health_check.ps1` | `docs/chapter4/evidence/health-check.json`, `docs/chapter4/logs/runtime-logs.txt` |
| Monitoring full production | Chưa full (optional nâng cao) | `infrastructure/monitoring/prometheus.yml` | `docs/chapter4/08-observability.md` |

## Kết luận

Chương 4 trong dự án này là bước hoàn thiện hệ thống phân tán dựa trên nền Chương 2 (microservices e-commerce) và Chương 3 (AI service). Trạng thái hiện tại cho thấy hệ thống đã được triển khai và kiểm chứng ở mức thực thi: có gateway, auth/RBAC, orchestration checkout, docker deployment, tích hợp AI và bộ evidence đối chiếu rõ ràng. Các phần chưa đạt mức production-grade (Kubernetes đầy đủ, monitoring sâu, resilience pattern nâng cao) đã được ghi nhận trung thực như hướng mở rộng tiếp theo.
