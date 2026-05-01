# CHƯƠNG 4. XÂY DỰNG HỆ THỐNG HOÀN CHỈNH

## 4.1 Kiến trúc tổng thể

### 4.1.1 Mô hình hệ thống

Trong bối cảnh phát triển hệ thương mại điện tử phân tán, Chương 4 đóng vai trò hợp nhất các kết quả của Chương 2 (microservices nghiệp vụ) và Chương 3 (dịch vụ AI) thành một kiến trúc vận hành thống nhất. Điểm cốt lõi của kiến trúc hiện tại không nằm ở việc tăng thêm số lượng service một cách cơ học, mà ở việc xác lập một trục điều phối rõ ràng giữa lớp truy cập bên ngoài, lớp nghiệp vụ và lớp dữ liệu, từ đó giảm sự phụ thuộc trực tiếp giữa các miền chức năng.

Mô hình triển khai hiện hành gồm các service: `user-service`, `product-service`, `cart-service`, `order-service`, `payment-service`, `shipping-service`, `ai-service`, cùng `gateway` và `frontend`. Trong cấu trúc này, gateway Nginx giữ vai trò điểm vào tập trung cho API; frontend đảm nhiệm lớp trình bày; các service còn lại chịu trách nhiệm theo miền nghiệp vụ độc lập. Sự kế thừa từ Chương 3 được thể hiện ở việc `ai-service` không đứng ngoài hệ thống mà được định tuyến cùng các API nghiệp vụ qua cùng một entry point. Đồng thời, phạm vi catalog cũng phản ánh đúng mở rộng thực tế: `product-service` đang vận hành với 10 nhóm loại sản phẩm trong `product-service/app/product_types.py`, thay vì mức mô phỏng tối giản.

**File:** `product-service/app/product_types.py`  
**Khối mã:** `PRODUCT_TYPE_SCHEMAS`  
**Dòng:** 1-82  
**Mục đích:** thể hiện trực tiếp độ rộng domain catalog ở triển khai thật

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

Sự nhất quán này còn được phản ánh ở lớp triển khai runtime: `docker-compose.yml` định nghĩa đầy đủ service, cơ sở dữ liệu, mạng nội bộ; `docs/chapter4/logs/compose-ps.txt` và `docs/chapter4/logs/network-inspect.json` cho thấy toàn bộ container vận hành trên cùng topology; nhóm ảnh giao diện như `docs/chapter4/screenshots/storefront-home.png`, `docs/chapter4/screenshots/customer-storefront-fixed.png` và `docs/chapter4/screenshots/ai-recommend-api.png` cho thấy hệ thống được sử dụng như một nền tảng thống nhất thay vì các module rời rạc.

| Thành phần | Vai trò | CSDL chính | Đầu vào/đầu ra nổi bật |
| --- | --- | --- | --- |
| `gateway` | Điều phối ingress, chuẩn hóa route công khai, chặn route nội bộ | Không sở hữu business DB | `/health`, `/api/users/*`, `/api/products/*`, `/api/cart/*`, `/api/orders/*`, `/api/payments/*`, `/api/shipping/*`, `/api/ai/*` |
| `user-service` | Đăng ký, đăng nhập, phát JWT, quản trị người dùng theo vai trò | MySQL `user_db` | `/auth/*`, `/users/*`, `/health` |
| `product-service` | Quản lý catalog và category, hỗ trợ truy vấn nội bộ | PostgreSQL `product_db` | `/products*`, `/categories*`, `/internal/products/*`, `/health` |
| `cart-service` | Quản trị giỏ hàng theo user | MySQL `cart_db` | `/cart/*`, `/internal/cart/*`, `/health` |
| `order-service` | Điều phối checkout và quản lý trạng thái đơn hàng | MySQL `order_db` | `/orders/*`, gọi payment/shipping/cart/product nội bộ, `/health` |
| `payment-service` | Xử lý và tra cứu thanh toán | MySQL `payment_db` | `/payment/*`, `/internal/payment/*`, `/health` |
| `shipping-service` | Tạo và theo dõi vận chuyển | MySQL `shipping_db` | `/shipping/*`, `/internal/shipping/*`, `/health` |
| `ai-service` | Recommendation, chatbot, behavior, graph, RAG | PostgreSQL `ai_db` + Neo4j | `/recommend`, `/chatbot`, `/behavior/*`, `/graph/*`, `/rag/*`, `/health` |
| `frontend` | Lớp tương tác người dùng theo vai trò khách hàng/nhân viên/admin | Không sở hữu business DB | Trang mua sắm, quản trị user, theo dõi đơn, chatbot |

### 4.1.2 Nguyên tắc

Nguyên tắc database-per-service được thực thi tương đối rõ trong cấu hình compose: mỗi service nghiệp vụ có DB riêng, và các service giao tiếp qua API thay vì truy cập trực tiếp schema của nhau. Điều này quan trọng trong hệ phân tán vì ràng buộc lỗi và vòng đời dữ liệu được giữ trong phạm vi miền nghiệp vụ. Khi `order-service` cần dữ liệu giỏ hàng hay sản phẩm, service này sử dụng client HTTP nội bộ thay vì truy vấn trực tiếp `cart_db` hoặc `product_db`. Cách tiếp cận đó giảm mức liên đới giữa các mô-đun persistence và hỗ trợ fault isolation ở tầng dữ liệu.

Về giao tiếp, REST đồng bộ là lựa chọn chủ đạo, phù hợp với yêu cầu xử lý thời gian thực của checkout. Đổi lại, kiến trúc chấp nhận chi phí chờ đồng bộ và độ nhạy với lỗi mạng trong các đoạn gọi chuỗi. Mã nguồn đã xử lý phần này ở mức thực dụng bằng timeout, retry có chọn lọc và chuẩn hóa lỗi ở `order-service/app/service_clients.py`; đồng thời kết quả chạy thực tế trong `docs/chapter4/evidence/e2e-checkout-success.json` và `docs/chapter4/evidence/e2e-checkout-payment-failure.json` cho thấy cơ chế điều phối vẫn giữ được nhất quán trạng thái giữa đơn hàng và thanh toán.

Từ góc nhìn thiết kế, kiến trúc hiện tại đạt cân bằng hợp lý giữa loose coupling và high cohesion cho phạm vi đồ án. Loose coupling thể hiện ở việc các service chỉ biết endpoint của nhau qua biến môi trường và hợp đồng API; high cohesion thể hiện ở việc mỗi service tập trung xử lý một miền rõ ràng. Dù vậy, để tiến gần production-grade, hệ thống cần mở rộng sang communication pattern bất đồng bộ cho các đường xử lý có side effect cao, thay vì phụ thuộc hoàn toàn vào chuỗi gọi đồng bộ.

## 4.2 System Architecture

### 4.2.1 Overview

Nếu xem hệ thống như một nền tảng thương mại điện tử hoàn chỉnh, kiến trúc hiện tại đã vượt khỏi mô hình “nhiều API cùng tồn tại” để đạt mô hình “nhiều miền nghiệp vụ cùng cộng tác dưới một giao diện hệ thống thống nhất”. Trục thống nhất đó là gateway; trục giá trị nghiệp vụ là checkout orchestration; và trục khác biệt của dự án nằm ở tích hợp AI recommendation/chatbot từ Chương 3 vào luồng vận hành chung của Chương 4.

Sự liên kết Chương 2 -> Chương 3 -> Chương 4 vì vậy không chỉ mang tính thứ tự nội dung, mà là tiến trình hoàn thiện kiến trúc: từ nền dịch vụ nghiệp vụ cơ bản, mở rộng năng lực thông minh, rồi hợp nhất cả hai trong một topology có thể quan sát, đánh giá và kiểm tra bằng dữ liệu runtime.

### 4.2.2 Microservice Architecture

`user-service` giữ vai trò identity boundary: service này phát JWT, gắn claim vai trò và điều khiển lớp quản trị người dùng. `product-service` là catalog boundary, đồng thời là nguồn ngữ cảnh quan trọng cho AI. `cart-service` duy trì trạng thái tạm thời của hành vi mua sắm; `order-service` là orchestration boundary, điều phối các bước tạo đơn, thanh toán, vận chuyển. `payment-service` và `shipping-service` được giữ riêng để tách biệt vòng đời giao dịch tài chính và logistics. `ai-service` mở rộng hệ thống theo hướng tư vấn, nhưng vẫn dựa trên dữ liệu sản phẩm và hành vi người dùng thực của nền tảng.

**File:** `ai-service/app/main.py`  
**Khối mã:** đăng ký router của AI service  
**Dòng:** 37-42  
**Mục đích:** làm rõ AI được triển khai như một API service online trong kiến trúc chung

```python
app.include_router(health_router)
app.include_router(behavior_router)
app.include_router(graph_router)
app.include_router(rag_router)
app.include_router(recommend_router)
app.include_router(chatbot_router)
```

Đề bài có nhắc đến khả năng tồn tại `notification-service`; trong triển khai thực tế chưa có service này như một biên độc lập. Đây là lựa chọn phạm vi hợp lý trong đồ án hiện tại: ưu tiên hoàn chỉnh checkout, auth, gateway và AI integration trước khi mở thêm domain giao tiếp hậu giao dịch.

### 4.2.3 API Gateway

Trong hệ phân tán, gateway không chỉ đơn thuần là reverse proxy mà còn là lớp ổn định hợp đồng truy cập. Client không cần biết topology nội bộ (`user-service:8002`, `order-service:8004`, ...), chỉ cần làm việc với contract `/api/*`. Cấu hình tại `gateway/nginx.conf` cho thấy rõ triết lý này: route được ánh xạ theo miền nghiệp vụ, header `Authorization` và `X-Correlation-ID` được truyền xuyên suốt, nhóm route nội bộ bị chặn từ biên công khai.

Lựa chọn Nginx còn tạo lợi thế ở khả năng áp chính sách tập trung (security headers, timeout, body size) mà không buộc mỗi service lặp lại cùng một lớp cấu hình. Dữ liệu kiểm tra sức khỏe trong `docs/chapter4/evidence/health-check.json`, ảnh `docs/chapter4/screenshots/gateway-health.png`, cùng log runtime trong `docs/chapter4/logs/runtime-logs.txt` xác nhận lớp ingress vận hành ổn định trong thời gian đo.

### 4.2.4 Service Communication

Mô hình communication hiện nay theo hướng orchestration tập trung tại `order-service`, phù hợp với đặc tính checkout cần kiểm soát thứ tự nghiệp vụ: lấy giỏ hàng, kiểm tra sản phẩm, tạo thanh toán, tạo vận chuyển, rồi kết thúc bằng cập nhật trạng thái đơn. Phương án này giúp business flow dễ đọc và dễ kiểm soát nhất quán giao dịch ở mức ứng dụng.

Mặt khác, orchestration đồng bộ làm tăng độ nhạy với độ trễ downstream. Nhóm hàm `_send_request` trong `order-service/app/service_clients.py` đã đưa vào timeout, retry theo mức độ idempotent và chuẩn hóa lỗi, nhưng vẫn chưa thay thế được các mẫu resilience cao hơn như circuit breaker hoặc queue-based compensation. Do đó, kiến trúc hiện phù hợp mô hình đồ án và MVP có bằng chứng vận hành, song cần cải tiến thêm nếu mở rộng tải đồng thời cao.

### 4.2.5 Containerization and Deployment

Containerization ở đây không chỉ phục vụ đóng gói, mà còn là công cụ chuẩn hóa môi trường thực nghiệm để kiểm chứng kiến trúc. Với `docker-compose.yml`, toàn bộ stack được đưa vào một mạng nội bộ thống nhất (`ecom-network`), cho phép tái lập đầy đủ quan hệ service-to-service và service-to-database.

`docs/chapter4/logs/compose-ps.txt` cho thấy các container lõi đều ở trạng thái Up, còn `docs/chapter4/logs/network-inspect.json` phản ánh gateway, frontend và các service cùng tham gia một bridge network chung. Điều này quan trọng về phương pháp luận: đánh giá kiến trúc chỉ có giá trị khi được kiểm chứng trong topology gần với vận hành tích hợp, không chỉ ở mức chạy đơn lẻ từng service.

### 4.2.6 System Structure

Cấu trúc thư mục phản ánh tương đối rõ ba lớp của hệ thống: lớp ứng dụng (`*-service`, `frontend`), lớp hạ tầng (`gateway`, `infrastructure/monitoring`), và lớp học thuật minh chứng (`docs/chapter4`, `scripts`). Cách tổ chức này giúp người đọc truy vết được mối liên hệ giữa thiết kế, triển khai và kiểm chứng.

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
scripts/
docs/chapter4/
```

Về mặt học thuật, cấu trúc trên phù hợp với tinh thần microservices thực dụng: không tối ưu tuyệt đối cho production, nhưng đủ rõ ràng để tách biên chức năng, tái lập môi trường và đánh giá hành vi hệ thống.

### 4.2.7 Design Principles

**Loose coupling:** Biên giao tiếp nằm ở API và biến môi trường (`*_SERVICE_URL`), thể hiện rõ trong `order-service/config/settings.py` và `ai-service/app/config.py`.  
**High cohesion:** Mỗi service xử lý logic miền tương ứng; ví dụ `payment-service` không đảm nhận orchestration checkout.  
**Scalability:** Tách lớp gateway và service độc lập tạo tiền đề scale theo hotspot; đặc biệt `ai-service` có dependency riêng (`ai_db`, Neo4j) nên có thể mở rộng theo hướng tính toán.  
**Fault isolation:** Lỗi downstream được cô lập và chuyển nghĩa rõ ràng tại tầng gọi service; nhánh thanh toán thất bại vẫn giữ hệ thống ở trạng thái nhất quán (`order_status=Cancelled`) theo dữ liệu chạy thực.

### 4.2.8 Security Considerations

Trong kiến trúc phân tán, bài toán bảo mật không chỉ là “có token” mà là xác lập ranh giới tin cậy giữa các lớp. Ở hệ thống hiện tại, token được phát tại `user-service`, mang claim vai trò, sau đó được gateway chuyển tiếp đến downstream để xác thực theo chính sách của từng service. Chiến lược pass-through này tránh việc lặp lại logic auth ở ingress, đồng thời giữ thẩm quyền kiểm soát truy cập sát miền nghiệp vụ.

Mặt khác, vì hệ thống có các endpoint nội bộ phục vụ orchestration, gateway chặn trực tiếp family `/internal/*` ở lớp public route. Đây là quyết định quan trọng về giảm bề mặt tấn công: ngay cả khi token người dùng hợp lệ, client bên ngoài vẫn không được gọi trực tiếp các endpoint chỉ dành cho trust path giữa service.

### 4.2.9 Discussion

So với kiến trúc monolithic, hệ thống hiện tại đạt lợi thế rõ về khả năng phân tách miền và tiến hóa tính năng độc lập, đặc biệt là AI subsystem. Tuy nhiên, chi phí đi kèm cũng đã xuất hiện: complexity vận hành cao hơn, nhiều điểm cấu hình hơn, phụ thuộc mạng nội bộ lớn hơn, và đòi hỏi observability tốt hơn để chẩn đoán lỗi xuyên service.

Điểm mạnh lớn nhất của triển khai hiện tại là có thể quan sát được trạng thái hệ thống bằng nhiều lớp dữ liệu (JSON kiểm thử, log runtime, ảnh giao diện, cấu hình hạ tầng). Điểm còn non chủ yếu nằm ở resilience pattern nâng cao và monitoring production-grade. Như vậy, hệ thống đã đạt tính hoàn chỉnh ở mức đồ án nghiêm túc, đồng thời vẫn giữ không gian phát triển rõ ràng cho giai đoạn hậu đồ án.

## 4.3 API Gateway (Nginx)

### 4.3.1 Vai trò

API Gateway trong hệ thống này đóng bốn vai trò đồng thời. Thứ nhất, nó tạo một điểm vào thống nhất để client giao tiếp với toàn bộ hệ thống qua contract route ổn định. Thứ hai, nó tách lớp client khỏi topology nội bộ, giúp thay đổi endpoint nội bộ mà không phá vỡ hợp đồng API bên ngoài. Thứ ba, nó là điểm áp policy tập trung, bao gồm security headers, timeout và forwarding headers. Thứ tư, nó giảm bề mặt tấn công bằng cách loại bỏ khả năng truy cập công khai tới route nội bộ.

Những vai trò trên được phản ánh cả ở cấu hình lẫn vận hành thực. Cụ thể, endpoint sức khỏe gateway phản hồi ổn định trong ảnh `docs/chapter4/screenshots/gateway-health.png`; các kịch bản health tổng hợp và truy cập service qua gateway được ghi nhận trong `docs/chapter4/evidence/health-check.json`; nhật ký chạy container xác nhận Nginx khởi tạo bình thường trong `docs/chapter4/logs/runtime-logs.txt`.

### 4.3.2 Cấu hình mẫu

**File:** `gateway/nginx.conf`  
**Khối mã:** internal-route guard + user auth route + ai route  
**Dòng:** 93-106, 223-232  
**Mục đích:** thể hiện đồng thời policy bảo vệ và policy định tuyến

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

location /api/ai/ {
    rewrite ^/api/ai/(.*)$ /$1 break;
    proxy_pass http://ai_service;
    proxy_set_header X-Correlation-ID $effective_correlation_id;
    proxy_set_header Authorization $http_authorization;
}
```

Đoạn mã trên cho thấy kiến trúc không đánh đổi bảo mật để lấy sự tiện lợi định tuyến. Từ góc nhìn thiết kế hệ thống, việc ghép policy “cho phép route công khai” và policy “cấm route nội bộ” trong cùng một lớp ingress giúp giảm sai lệch cấu hình giữa các service downstream, đồng thời tăng khả năng kiểm soát nhất quán.

## 4.4 Authentication (JWT)

### 4.4.1 Cài đặt

Bài toán xác thực trong hệ phân tán là bài toán cân bằng giữa tính độc lập của service và tính nhất quán danh tính người dùng. Hệ thống chọn JWT vì token này hỗ trợ truyền danh tính theo kiểu stateless, giảm phụ thuộc truy vấn đồng bộ tới identity provider trong từng request.

### 4.4.2 Cấu hình

**File:** `user-service/app/serializers.py`  
**Khối mã:** `LoginSerializer.get_token`  
**Dòng:** 52-59  
**Mục đích:** gắn claim vai trò và danh tính vào access token

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

**File:** `user-service/app/views.py`  
**Khối mã:** `UserListView`  
**Dòng:** 32-35  
**Mục đích:** enforce RBAC tại route quản trị

```python
class UserListView(generics.ListCreateAPIView):
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAdmin]
```

### 4.4.3 Luồng

Luồng auth hiện tại có thể tóm tắt như sau: người dùng đăng nhập tại user-service qua gateway; token được cấp kèm claim role; client gửi bearer token ở các request cần bảo vệ; downstream service tự xác thực và áp quyền truy cập theo vai trò. Cơ chế này được xác nhận bằng dữ liệu kiểm tra vai trò trong `docs/chapter4/evidence/auth-rbac-check.json` và `docs/chapter4/evidence/role-flows-check.json`, đồng thời được phản ánh ở giao diện đa vai trò qua `docs/chapter4/screenshots/admin-users-fixed.png` và `docs/chapter4/screenshots/staff-orders-fixed.png`.

Từ góc nhìn học thuật, kiến trúc JWT hiện tại phù hợp phạm vi đồ án vì đảm bảo được ba yêu cầu cốt lõi: xác thực, phân quyền, và khả năng mở rộng theo service. Hạn chế nằm ở chỗ verification policy còn phân tán theo từng service; nếu mở rộng quy mô lớn hơn, hệ thống có thể cân nhắc thêm lớp token introspection hoặc policy engine tập trung.

## 4.5 Giao tiếp giữa các Service

### 4.5.1 REST API call

Giao tiếp liên service trong checkout là biểu hiện rõ nhất của kiến trúc cộng tác đa miền. `order-service` không chỉ tạo bản ghi đơn hàng mà còn điều phối chuỗi hành động phụ thuộc lẫn nhau với `cart-service`, `product-service`, `payment-service`, `shipping-service`. Nhờ vậy, trạng thái cuối cùng của đơn hàng phản ánh được kết quả thật từ các service downstream, thay vì cập nhật giả định.

### 4.5.2 Best Practice

**File:** `order-service/app/service_clients.py`  
**Khối mã:** `_send_request`  
**Dòng:** 30-96  
**Mục đích:** chuẩn hóa timeout, retry và lỗi gọi service

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

Phần thiết kế đáng chú ý là retry được giới hạn cho thao tác ít rủi ro nhân bản side effect; các lệnh POST tạo payment/shipment không retry tự động. Đây là lựa chọn thận trọng nhằm giảm nguy cơ ghi trùng nghiệp vụ trong bối cảnh chưa triển khai idempotency key hoặc saga pattern đầy đủ.

Đánh giá tổng thể cho thấy chiến lược hiện tại đủ tốt cho mục tiêu đồ án: rõ ràng, kiểm soát được luồng lỗi, dễ kiểm chứng bằng kịch bản thành công/thất bại. Tuy nhiên, khi yêu cầu độ bền giao dịch tăng cao, hệ thống sẽ cần chuyển một phần communication sang bất đồng bộ để giảm coupling thời gian thực.

## 4.6 Docker hóa hệ thống

### 4.6.1 Dockerfile

Dockerfile được duy trì cho các service chính, cho phép đóng gói độc lập theo công nghệ (Django, FastAPI, Next.js, Nginx). Về phương diện kỹ thuật, điều này giúp ổn định dependency boundary của từng service và giảm sai lệch môi trường khi đánh giá tích hợp.

### 4.6.2 docker-compose.yml

**File:** `docker-compose.yml`  
**Khối mã:** security env chung + gateway + network  
**Dòng:** 1-9, 281-294, 325-327  
**Mục đích:** biểu diễn topology tích hợp và mạng nội bộ thống nhất

```yaml
x-security-env: &security-env
  JWT_SIGNING_KEY: shared-jwt-signing-key
  INTERNAL_SERVICE_JWT_SECRET: internal-service-secret

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
```

Cấu hình trên cho thấy hai giá trị học thuật quan trọng. Một là tính tái lập: hệ thống có thể được dựng theo một topology nhất quán, phù hợp cho kiểm thử liên service. Hai là tính quan sát: vì tất cả thành phần cùng tham gia mạng chung, việc đối chiếu luồng xử lý và trạng thái container trở nên khả thi qua dữ liệu runtime.

## 4.7 Luồng hệ thống (End-to-End)

### 4.7.1 Use case: Mua hàng

Use case mua hàng được tổ chức như một chuỗi nghiệp vụ liên miền: xác thực người dùng, truy cập catalog, quản lý giỏ hàng, tạo đơn, xử lý thanh toán, khởi tạo vận chuyển. Điểm quan trọng không phải là từng API riêng lẻ chạy được, mà là toàn chuỗi giữ được tính nhất quán trạng thái khi đi qua nhiều service.

Dữ liệu thực thi trong `docs/chapter4/evidence/e2e-checkout-success.json` ghi nhận trạng thái cuối: đơn hàng chuyển sang `Shipping`, thanh toán ở trạng thái `Success`, vận chuyển ở trạng thái `Processing`. Ở chiều ngược lại, `docs/chapter4/evidence/e2e-checkout-payment-failure.json` cho thấy nhánh thất bại được xử lý có kiểm soát: thanh toán `Failed` dẫn tới đơn hàng `Cancelled`. Hai nhánh này xác nhận logic nghiệp vụ không bị cứng vào happy path.

### 4.7.2 Sequence logic

**File:** `order-service/app/views.py`  
**Khối mã:** `OrderListCreateView.create`  
**Dòng:** 72-96  
**Mục đích:** thể hiện state transition theo kết quả payment/shipping

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

Khi đặt đoạn mã này cạnh dữ liệu runtime, có thể thấy logic điều phối được hiện thực hóa nhất quán từ mã nguồn đến trạng thái vận hành. Nhóm ảnh giao diện `docs/chapter4/screenshots/customer-orders-fixed.png` và `docs/chapter4/screenshots/customer-order-detail-fixed.png` bổ sung góc nhìn từ phía người dùng cuối: trạng thái đơn hàng không chỉ đúng ở API mà còn phản ánh lên tầng trình bày.

Việc có thêm `docs/chapter4/screenshots/staff-orders-fixed.png` và `docs/chapter4/screenshots/admin-users-fixed.png` cũng giúp mở rộng phân tích end-to-end theo vai trò: cùng một dữ liệu nghiệp vụ nhưng hiển thị và quyền thao tác khác nhau theo RBAC.

## 4.8 Triển khai Kubernetes (Optional)

Trong phạm vi hiện tại, triển khai chính dừng ở Docker Compose và chưa có manifest Kubernetes đầy đủ cho toàn bộ stack. Đây là giới hạn được chấp nhận vì mục tiêu của Chương 4 tập trung vào hoàn thiện kiến trúc tích hợp và kiểm chứng vận hành. Từ nền tảng hiện có, hướng mở rộng hợp lý là chuyển đổi từng service sang `Deployment`/`Service`, sau đó đưa gateway vào lớp ingress của cụm K8s.

## 4.9 Logging và Monitoring

Mặt bằng observability hiện tại được xây trên ba lớp. Lớp thứ nhất là gateway logging với định dạng log chứa thông tin upstream và correlation id trong `gateway/nginx.conf`. Lớp thứ hai là logging ở application services, thể hiện qua cấu hình `LOGGING` trong các service Django và khởi tạo logging ở `ai-service/app/main.py`. Lớp thứ ba là health endpoint đồng nhất, được kiểm tra tập trung qua `scripts/health_check.ps1` và dữ liệu JSON tương ứng.

Nhìn từ góc độ học thuật, hệ thống đã đạt ngưỡng “có thể quan sát để vận hành” ở mức đồ án: có điểm đo ingress, có điểm đo service-level, có kiểm tra liveness xuyên toàn hệ thống. Tuy nhiên, monitoring vẫn ở mức skeleton (tham chiếu tại `infrastructure/monitoring/prometheus.yml`), chưa mở rộng thành pipeline metrics và dashboard hoàn chỉnh. Điều này cần được ghi nhận như giới hạn kỹ thuật hiện hữu, không nên diễn giải thành đã có full-stack observability.

## 4.10 Đánh giá hệ thống

### 4.10.1 Hiệu năng

Kết quả đo trong `docs/chapter4/evidence/basic-system-eval.json` cho thấy độ trễ trung bình của `GET /health` và `GET /api/products/products` nằm ở mức thấp trong môi trường single-client, trong khi `GET /api/ai/recommend` cao hơn do đặc thù xử lý tổng hợp. Điều này phù hợp với kỳ vọng kiến trúc: request AI phức tạp hơn request catalog thuần.

Quan trọng hơn, số liệu p95 thể hiện sự khác biệt rõ giữa request đầu (cold path) và các request sau (warm path). Vì vậy, bộ số liệu này nên được hiểu như chỉ báo baseline cho môi trường đồ án, không phải benchmark chịu tải đồng thời lớn.

### 4.10.2 Khả năng mở rộng

Kiến trúc hiện có ưu thế về khả năng mở rộng theo service: có thể tăng số instance ở các điểm nóng như gateway, product-service hoặc ai-service tùy loại tải. Tuy nhiên, checkout đồng bộ vẫn là điểm nhạy vì phụ thuộc chuỗi phản hồi của nhiều service. Nếu quy mô giao dịch tăng mạnh, hệ thống cần bổ sung chiến lược bất đồng bộ cho một số tác vụ hậu thanh toán để giảm áp lực phản hồi tức thời.

### 4.10.3 Ưu điểm

Ưu điểm nổi bật nhất là tính nhất quán giữa thiết kế, mã nguồn và dữ liệu vận hành. Nói cách khác, các quyết định kiến trúc không dừng ở mô tả mà đã được kiểm chứng qua đường chạy thực tế: gateway hoạt động, RBAC phân vai được duy trì, checkout có cả nhánh thành công và thất bại, AI được tích hợp trực tiếp vào đường vào hệ thống.

### 4.10.4 Nhược điểm

Điểm yếu chính nằm ở độ chín vận hành hơn là tính đúng chức năng: monitoring chưa đầy đủ, resilience pattern nâng cao chưa triển khai, và benchmark chưa đánh giá concurrency thực. Ngoài ra, vì hệ thống đang tối ưu cho tính kiểm chứng trong phạm vi đồ án, một số quyết định (ví dụ orchestration đồng bộ) vẫn mang tính đánh đổi giữa độ đơn giản và độ bền ở quy mô lớn.

## 4.11 Bài tập thực hành / Kết quả thực hiện

Ở bình diện thực hành, hệ thống đã hiện thực hóa đầy đủ chuỗi năng lực mà Chương 4 hướng tới: triển khai dịch vụ nghiệp vụ bằng Django/FastAPI, định tuyến qua gateway Nginx, docker hóa toàn stack, kiểm chứng luồng mua hàng liên service, và tích hợp AI recommendation/chatbot vào cùng kiến trúc truy cập. Giá trị của phần thực hành nằm ở việc các thành phần này tương tác được với nhau trong cùng môi trường runtime, thay vì tồn tại như các bài tập tách rời.

Nhóm script vận hành (`scripts/e2e_checkout_flow.ps1`, `scripts/auth_rbac_check.ps1`, `scripts/role_flows_check.ps1`, `scripts/ai_gateway_demo.ps1`, `scripts/health_check.ps1`, `scripts/basic_system_eval.ps1`) góp phần chuẩn hóa quy trình kiểm chứng để người đọc có thể tái lập kết quả. Từ góc nhìn học thuật, đây là điều kiện quan trọng giúp báo cáo vượt khỏi mô tả lý thuyết và chuyển sang mức luận chứng có thể kiểm tra độc lập.

## 4.12 Checklist đánh giá

| Tiêu chí | Mức độ đáp ứng | Giải thích ngắn | Code chính | Minh chứng tiêu biểu |
| --- | --- | --- | --- | --- |
| API Gateway | Đạt | Có điểm vào tập trung, ánh xạ route công khai, chặn route nội bộ | `gateway/nginx.conf`, `docker-compose.yml` | `docs/chapter4/evidence/health-check.json`, `docs/chapter4/screenshots/gateway-health.png` |
| JWT Authentication | Đạt | Token phát tại user-service, role claim được dùng cho RBAC downstream | `user-service/app/serializers.py`, `user-service/app/views.py` | `docs/chapter4/evidence/auth-rbac-check.json`, `docs/chapter4/evidence/role-flows-check.json` |
| Docker hóa hệ thống | Đạt | Full stack chạy bằng Compose trên cùng network nội bộ | `docker-compose.yml`, các `Dockerfile` | `docs/chapter4/logs/compose-ps.txt`, `docs/chapter4/logs/network-inspect.json` |
| Flow order -> payment -> shipping | Đạt | Orchestration có nhánh success/failure và cập nhật trạng thái nhất quán | `order-service/app/views.py`, `order-service/app/service_clients.py` | `docs/chapter4/evidence/e2e-checkout-success.json`, `docs/chapter4/evidence/e2e-checkout-payment-failure.json`, ảnh order UI |
| AI integration | Đạt | AI service đi qua gateway, có recommendation và chatbot gắn với catalog thật | `gateway/nginx.conf`, `ai-service/app/main.py`, `frontend/lib/ai.ts` | `docs/chapter4/evidence/ai-gateway-demo.json`, `docs/chapter4/screenshots/ai-recommend-api.png` |
| Logging/Monitoring | Đạt mức đồ án | Có gateway log, service log, health check đồng nhất, monitoring skeleton | `gateway/nginx.conf`, `*/config/settings.py`, `infrastructure/monitoring/prometheus.yml` | `docs/chapter4/logs/runtime-logs.txt`, `docs/chapter4/evidence/health-check.json` |
| Kubernetes | Optional, chưa triển khai đầy đủ | Chưa có bộ manifest vận hành hoàn chỉnh, được ghi nhận như hướng mở rộng | N/A | N/A |

## Kết luận

Chương 4 đã hoàn thiện hệ thống theo hướng một nền tảng thương mại điện tử phân tán có thể vận hành và kiểm chứng thực tế, thay vì dừng ở mức mô tả kiến trúc. Sự hoàn thiện này đến từ bốn trụ cột: gateway thống nhất truy cập, JWT/RBAC nhất quán đa service, orchestration checkout phản ánh đúng vòng đời nghiệp vụ, và dockerized deployment cho phép tái lập môi trường tích hợp. Điểm mở rộng của dự án nằm ở việc AI service từ Chương 3 được đưa vào cùng bức tranh vận hành, tạo ra giá trị tư vấn ngay trong hệ thống thương mại điện tử.

Ở bình diện học thuật, kết quả hiện tại cho thấy một kiến trúc microservices đã đạt độ chín phù hợp đồ án: đủ sâu để phân tích thiết kế, đủ rõ để đối chiếu mã nguồn, và đủ thực nghiệm để kiểm tra bằng dữ liệu runtime. Các giới hạn còn lại (monitoring production-grade, resilience nâng cao, mở rộng Kubernetes) không phủ nhận thành quả của Chương 4, mà xác định hợp lý lộ trình kỹ thuật cho giai đoạn tiếp theo.

