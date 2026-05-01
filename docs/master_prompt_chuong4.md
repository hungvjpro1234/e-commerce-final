# MASTER PROMPT – TRIỂN KHAI CHƯƠNG 4 CHO DỰ ÁN `ecom-final`

## 1. Vai trò của bạn

Bạn là **AI engineering agent** chịu trách nhiệm **hoàn thiện Chương 4 – Xây dựng hệ thống hoàn chỉnh** cho dự án `ecom-final`, dựa trên bối cảnh sau:

- **Chương 2 và Chương 3 đã được triển khai thật bằng codebase**, không phải chỉ là báo cáo lý thuyết.
- Codebase hiện tại đã là một hệ thống **e-commerce microservices** với các service nghiệp vụ chính.
- Riêng **product-service không chỉ có 2–3 loại sản phẩm minh họa**, mà đã được mở rộng thành **10 nhóm loại sản phẩm đầy đủ** trong triển khai thực tế.
- Dự án đã có nền tảng từ:
  - **User Service**
  - **Product Service**
  - **Cart Service**
  - **Order Service**
  - **Payment Service**
  - **Shipping Service**
  - **AI Service**
- Mục tiêu của bạn là **tiếp nối đúng tinh thần của Chương 4 trong đề bài**, để sau khi hoàn thành:
  1. Dự án **đạt đầy đủ tất cả các tiêu chí của Chương 4**.
  2. Các phần triển khai đều có **evidence/deliverable rõ ràng** để con người có thể kiểm tra lại.
  3. Mọi thay đổi phải phản ánh **triển khai thật trong codebase**, không được làm báo cáo suông.
  4. Kết quả cuối phải đủ tốt để dùng làm nền tảng viết **báo cáo tiểu luận, demo hệ thống, và đối chiếu checklist đánh giá**.

---

## 2. Mục tiêu tổng quát

Hãy hoàn thiện dự án theo đúng yêu cầu của **Chương 4 – Xây dựng hệ thống hoàn chỉnh**, bao gồm tối thiểu các nội dung sau:

1. **Kiến trúc tổng thể hoàn chỉnh** cho hệ thống microservices.
2. **API Gateway bằng Nginx** làm entry point cho toàn hệ thống.
3. **JWT Authentication** hoạt động xuyên service theo đúng kiến trúc hiện tại.
4. **Giao tiếp giữa các service** rõ ràng, có best practice tối thiểu.
5. **Docker hóa toàn hệ thống** và chạy được bằng Docker Compose.
6. **Luồng end-to-end hoàn chỉnh** cho use case mua hàng.
7. **Tích hợp AI service** vào toàn hệ thống theo vai trò recommendation/chatbot.
8. **Logging và monitoring ở mức phù hợp với đồ án**, ít nhất có cấu trúc hoặc bản triển khai khả dụng.
9. **Đánh giá hệ thống** bằng các tiêu chí trong Chương 4.
10. Tạo ra **tài liệu, evidence, script, ảnh chụp/log/output** đủ để chứng minh từng mục đã làm.

---

## 3. Nguyên tắc làm việc bắt buộc

### 3.1 Không phá vỡ hệ thống hiện có
- Không được viết lại toàn bộ project nếu không cần thiết.
- Ưu tiên **tận dụng codebase hiện tại**, chỉ bổ sung/chuẩn hóa/hoàn thiện những phần còn thiếu để đạt tiêu chí Chương 4.
- Mọi refactor lớn phải có lý do rõ ràng.

### 3.2 Triển khai thật, không làm giả
- Không được tạo file mô tả nói rằng “đã làm” nếu code không có.
- Nếu một tính năng chưa đủ hoàn chỉnh để production, vẫn phải triển khai ở mức **đúng cho đồ án**, chạy được hoặc có skeleton hợp lý, có giải thích phạm vi.
- Không viết các bằng chứng giả.

### 3.3 Mỗi tiêu chí phải có bằng chứng đối chiếu
Mỗi phần triển khai phải đi kèm ít nhất một trong các loại evidence sau:
- file cấu hình thật
- source code thật
- API route thật
- docker compose/service definition thật
- log chạy thật
- ảnh PNG từ kết quả chạy hệ thống
- markdown tổng hợp kết quả
- command/script tái hiện được

### 3.4 Ưu tiên khả năng kiểm tra lại
- Mọi deliverable phải dễ kiểm tra bởi con người.
- Nếu tạo tài liệu tổng hợp, phải chỉ rõ:
  - file nào chứa code
  - chạy bằng lệnh nào
  - kết quả nào chứng minh yêu cầu đã đạt

### 3.5 Không làm qua loa
- Nếu đề yêu cầu “Có API Gateway”, thì không chỉ tạo thư mục `gateway/` rỗng.
- Nếu đề yêu cầu “Có JWT Auth”, thì phải có luồng thực tế hoặc tối thiểu là cấu hình + middleware/validation + flow test được.
- Nếu đề yêu cầu “Có flow order → payment → shipping”, thì phải có luồng thật qua API/service calls hoặc event flow khả dụng.

---

## 4. Diễn giải yêu cầu Chương 4 thành mục tiêu triển khai cụ thể

Dựa trên đề bài Chương 4, bạn phải đảm bảo hệ thống cuối cùng thể hiện được các điểm sau:

### 4.1 Kiến trúc tổng thể
Hệ thống phải thể hiện rõ một kiến trúc microservices hoàn chỉnh, gồm:
- `gateway/`
- `user-service/`
- `product-service/`
- `cart-service/`
- `order-service/`
- `payment-service/`
- `shipping-service/`
- `ai-service/`
- `infrastructure/` hoặc cấu trúc tương đương để chứa thành phần triển khai hệ thống

Yêu cầu:
- Mỗi service là một thành phần độc lập.
- Mỗi service có database riêng hoặc cấu hình riêng đúng theo nguyên tắc database-per-service.
- Không có dấu hiệu truy cập trực tiếp DB của service khác.
- Kiến trúc thư mục, config, network, container phải phản ánh điều đó.

### 4.2 API Gateway bằng Nginx
Phải có **API Gateway** hoạt động như entry point duy nhất hoặc entry point chính của hệ thống.

Gateway phải thể hiện được tối thiểu:
- reverse proxy đến đúng service
- route prefix rõ ràng, ví dụ:
  - `/api/users/...`
  - `/api/products/...`
  - `/api/cart/...`
  - `/api/orders/...`
  - `/api/payments/...`
  - `/api/shipping/...`
  - `/api/ai/...`
- có xử lý tối thiểu liên quan đến:
  - forwarding headers
  - JWT header passthrough hoặc validation strategy
  - basic security headers
  - logging access/error

Khuyến nghị:
- có thêm rate limiting, CORS handling, request size limit, timeout, upstream config nếu phù hợp.

### 4.3 JWT Authentication
Phải có cơ chế xác thực JWT nhất quán trong hệ thống.

Kết quả mong muốn:
- User login nhận được token.
- Client gửi token qua header.
- Gateway và/hoặc downstream services xử lý token đúng chiến lược kiến trúc hiện tại.
- Những route cần bảo vệ phải thực sự được bảo vệ.
- RBAC phải tiếp tục hoạt động theo vai trò như:
  - admin
  - staff
  - customer

Phải làm rõ trong code và docs:
- token được cấp ở đâu
- token được verify ở đâu
- service nào tin cậy service nào
- trường hợp service-to-service auth đang dùng cách nào

### 4.4 Service communication
Phải thể hiện được giao tiếp giữa các service, tối thiểu gồm:
- synchronous REST calls cho các tác vụ thời gian thực
- best practice cơ bản:
  - timeout
  - retry ở mức hợp lý
  - error handling rõ ràng
  - logging khi gọi service khác

Nếu codebase hiện tại có thể hỗ trợ, hãy bổ sung hoặc chuẩn hóa thêm:
- request wrapper/helper dùng chung
- service endpoint config qua environment variables
- health check endpoint

Không bắt buộc phải làm circuit breaker hoàn chỉnh, nhưng nếu không làm thì phải ghi rõ phạm vi.

### 4.5 Docker hóa hệ thống
Phải có khả năng chạy hệ thống bằng Docker Compose ở môi trường phát triển.

Yêu cầu bắt buộc:
- mỗi service có `Dockerfile` hoặc build strategy rõ ràng
- có `docker-compose.yml` hoặc cấu trúc compose tương đương
- có network nội bộ
- có volumes/env phù hợp
- các database/dependency cần thiết phải được khai báo rõ
- command khởi động được ghi lại rõ ràng

Kết quả mong muốn:
- có thể khởi động gần như toàn bộ hệ thống bằng một luồng lệnh nhất quán
- các service nói chuyện được với nhau qua container network

### 4.6 End-to-end flow
Phải có **luồng mua hàng hoàn chỉnh** thể hiện đúng Chương 4:

1. user login
2. xem sản phẩm
3. thêm vào cart
4. tạo order
5. payment
6. shipping

Phải có bằng chứng rằng luồng này chạy được hoặc được mô phỏng hợp lệ trong project:
- API collection, test script, shell script, Postman collection, pytest integration flow, hoặc markdown replay steps
- output thực tế
- status thay đổi hợp lý giữa các service

### 4.7 Tích hợp AI service
AI service phải được đặt trong bức tranh hệ thống hoàn chỉnh, không đứng riêng lẻ.

Phải thể hiện được ít nhất một trong hai luồng:
- recommendation list theo user/query/product context
- chatbot tư vấn sản phẩm

Lý tưởng là có cả hai.

Cần làm rõ:
- API nào expose qua gateway
- dữ liệu đầu vào lấy từ đâu
- AI service kết nối với product/service khác thế nào
- cách dùng AI service trong full system demo

### 4.8 Logging và monitoring
Đối với đồ án, không nhất thiết phải triển khai một platform quan sát production-grade đầy đủ, nhưng phải có mức triển khai hợp lý để thỏa tiêu chí Chương 4.

Ưu tiên theo thứ tự:
1. logging có cấu trúc cho các service
2. gateway logging
3. health endpoints
4. metrics cơ bản hoặc skeleton monitoring
5. nếu đủ thời gian: Prometheus/Grafana hoặc cấu hình demo tương đương

Nếu không thể triển khai full ELK/Prometheus/Grafana, phải:
- tạo cấu trúc sẵn sàng mở rộng
- có tài liệu giải thích rõ mức độ hoàn thành
- tuyệt đối không nhận vơ là đã làm full nếu chưa có

### 4.9 Đánh giá hệ thống
Phải có phần đánh giá hệ thống sau triển khai, bao gồm tối thiểu:
- response time cơ bản
- throughput hoặc chỉ số thay thế hợp lý trong phạm vi đồ án
- khả năng mở rộng theo service
- ưu điểm kiến trúc
- hạn chế hiện tại

Nếu đo benchmark:
- dùng script đo đơn giản
- hoặc test load nhẹ
- hoặc so sánh số liệu từ log/requests có phương pháp

Phải trung thực về mức độ đo được.

---

## 5. Checklist bắt buộc phải đạt sau khi hoàn thành

Sau khi thực hiện xong, dự án phải đạt được **toàn bộ checklist sau**. Đây là tiêu chuẩn nghiệm thu nội bộ bắt buộc.

### 5.1 Checklist chức năng và kiến trúc
- [ ] Có `gateway/` hoặc thành phần API Gateway tương đương
- [ ] Có file cấu hình Nginx hoạt động thật
- [ ] Gateway route được đến các service chính
- [ ] Hệ thống thể hiện rõ kiến trúc microservices
- [ ] Mỗi service có ranh giới trách nhiệm rõ
- [ ] Không có truy cập DB chéo service
- [ ] Có service communication giữa các thành phần nghiệp vụ

### 5.2 Checklist bảo mật
- [ ] Có JWT auth hoạt động
- [ ] Login trả token
- [ ] Protected routes yêu cầu token
- [ ] RBAC còn hoạt động
- [ ] Gateway và/hoặc service có xử lý header/auth phù hợp

### 5.3 Checklist containerization
- [ ] Có Dockerfile cho các service chính hoặc chiến lược container hóa tương đương
- [ ] Có `docker-compose.yml`
- [ ] Compose có thể dựng hệ thống hợp lệ
- [ ] Các service chạy được trên cùng network
- [ ] Environment variables được tổ chức rõ ràng

### 5.4 Checklist luồng nghiệp vụ
- [ ] Có flow login → browse product → add cart → create order → payment → shipping
- [ ] Order có thể gọi payment
- [ ] Payment success dẫn đến shipping flow
- [ ] Trạng thái giữa các service được cập nhật hợp lý

### 5.5 Checklist AI integration
- [ ] AI service tồn tại như một service độc lập
- [ ] Có route AI đi qua gateway hoặc cơ chế truy cập hệ thống rõ ràng
- [ ] Có recommendation hoặc chatbot hoạt động
- [ ] AI service dùng được trong demo end-to-end

### 5.6 Checklist observability
- [ ] Có logging cơ bản cho gateway
- [ ] Có logging cơ bản cho các service chính
- [ ] Có health check hoặc endpoint kiểm tra trạng thái
- [ ] Có ít nhất cấu trúc/skeleton cho monitoring nếu chưa full stack

### 5.7 Checklist evidence
- [ ] Có tài liệu markdown tổng hợp kết quả
- [ ] Có chỉ dẫn cách chạy hệ thống
- [ ] Có bằng chứng kiểm thử flow
- [ ] Có output/log/screenshot cho các phần quan trọng
- [ ] Có mapping từ yêu cầu Chương 4 → file code/deliverable tương ứng

---

## 6. Cách thực hiện – quy trình nhiều pha bắt buộc

Hãy làm việc theo **nhiều pha**, và sau mỗi pha phải cập nhật tài liệu tiến độ trong codebase. Không được nhảy cóc đến kết luận.

### Pha 0 – Khảo sát codebase hiện tại
Mục tiêu:
- quét toàn bộ codebase
- xác định những gì đã có sẵn
- đối chiếu với Chương 4
- xác định phần thiếu, phần cần chuẩn hóa, phần cần bổ sung

Bạn phải tạo:
- `docs/chapter4/00-gap-analysis.md`

Nội dung file này phải có:
- hiện trạng từng service
- gateway đã có hay chưa
- JWT đang làm tới đâu
- docker hóa đang làm tới đâu
- AI service đang ở mức nào
- flow end-to-end đã có tới đâu
- phần nào đạt rồi
- phần nào chưa đạt
- phần nào cần sửa ít
- phần nào cần triển khai mới

### Pha 1 – Chuẩn hóa kiến trúc hệ thống
Mục tiêu:
- hoàn thiện cấu trúc thư mục, naming, env config, network topology, service boundary
- đảm bảo dự án nhìn vào là thấy rõ kiến trúc Chương 4

Bạn phải tạo/cập nhật:
- `docs/chapter4/01-system-architecture.md`
- sơ đồ ASCII hoặc Mermaid nếu phù hợp
- mapping service → responsibility → database → exposed routes

Nếu thiếu thư mục `gateway/` hoặc `infrastructure/`, hãy bổ sung hợp lý.

### Pha 2 – API Gateway
Mục tiêu:
- triển khai hoặc hoàn thiện `gateway/nginx.conf`
- route được đến các service chính

Bạn phải tạo/cập nhật:
- `gateway/nginx.conf`
- `docs/chapter4/02-api-gateway.md`

Tài liệu phải mô tả:
- route map
- security headers
- proxy strategy
- auth header flow
- cách test gateway

### Pha 3 – JWT và bảo mật hệ thống
Mục tiêu:
- chuẩn hóa auth flow xuyên hệ thống
- đảm bảo protected endpoints thực sự bảo vệ được

Bạn phải tạo/cập nhật:
- code auth cần thiết trong services/gateway
- `docs/chapter4/03-authentication-security.md`

Tài liệu phải trình bày:
- luồng login/token/verify
- RBAC matrix ngắn gọn
- route nào public, route nào protected
- cách test token end-to-end

### Pha 4 – Service communication
Mục tiêu:
- chuẩn hóa giao tiếp service-to-service
- bổ sung timeout/retry/error handling cơ bản nếu còn thiếu

Bạn phải tạo/cập nhật:
- các helper/module/service-client nếu cần
- `docs/chapter4/04-service-communication.md`

Phải nêu rõ:
- order gọi payment như thế nào
- payment và shipping liên hệ nhau ra sao
- AI service đọc dữ liệu gì từ hệ thống
- synchronous vs asynchronous hiện đang dùng gì

### Pha 5 – Docker hóa hệ thống
Mục tiêu:
- mọi service chính và dependencies cần thiết chạy được trong Docker Compose

Bạn phải tạo/cập nhật:
- `Dockerfile` cho từng service còn thiếu
- `docker-compose.yml`
- `.env.example` hoặc cấu trúc env mẫu
- `docs/chapter4/05-docker-deployment.md`

Tài liệu phải có:
- cách build
- cách run
- service nào dùng port nào
- dependency nào cần chờ
- common issues và cách xử lý

### Pha 6 – End-to-end workflow
Mục tiêu:
- triển khai/test đầy đủ luồng mua hàng

Bạn phải tạo/cập nhật:
- script test hoặc collection, ví dụ một trong các dạng:
  - `scripts/e2e_checkout_flow.sh`
  - `tests/integration/test_checkout_flow.py`
  - `postman/chapter4-e2e.json`
- `docs/chapter4/06-end-to-end-flow.md`

Bằng chứng phải thể hiện:
- login thành công
- lấy sản phẩm thành công
- add cart thành công
- tạo order thành công
- payment thành công
- shipping được khởi tạo hoặc cập nhật thành công

### Pha 7 – AI integration
Mục tiêu:
- AI service tham gia vào hệ thống hoàn chỉnh

Bạn phải tạo/cập nhật:
- API route cho AI qua gateway nếu chưa có
- script/demo gọi recommendation hoặc chatbot
- `docs/chapter4/07-ai-integration.md`

Phải chứng minh được:
- AI service không đứng ngoài hệ thống
- client có thể gọi AI service qua đường kiến trúc chính
- output AI liên hệ được với dữ liệu sản phẩm/hành vi/ngữ cảnh thật của dự án

### Pha 8 – Logging, monitoring, health check
Mục tiêu:
- bổ sung tính quan sát tối thiểu cho hệ thống

Bạn phải tạo/cập nhật:
- logging config cho các service chính nếu chưa có
- health endpoint nếu thiếu
- nếu khả thi, cấu hình monitoring demo
- `docs/chapter4/08-observability.md`

Phải mô tả rõ:
- log ở đâu
- format log
- health check như thế nào
- monitoring đã triển khai mức nào

### Pha 9 – Đánh giá hệ thống
Mục tiêu:
- tạo phần đánh giá đúng tinh thần Chương 4

Bạn phải tạo:
- `docs/chapter4/09-system-evaluation.md`

Nội dung bắt buộc:
- response time cơ bản
- throughput hoặc nhận xét định lượng hợp lý
- scalability discussion
- ưu điểm
- hạn chế
- đề xuất mở rộng về sau

### Pha 10 – Hồ sơ nghiệm thu Chương 4
Mục tiêu:
- tổng hợp tất cả kết quả để con người đối chiếu nhanh

Bạn phải tạo:
- `docs/chapter4/FINAL_CHAPTER4_SUMMARY.md`

File này phải có:
1. Tóm tắt những gì đã triển khai
2. Bảng đối chiếu **Yêu cầu Chương 4 → File code → Deliverable → Trạng thái**
3. Danh sách file quan trọng
4. Cách chạy demo nhanh
5. Cách kiểm tra full flow
6. Danh sách screenshot/log/output đã tạo
7. Những phần hoàn thành đầy đủ
8. Những phần optional đã làm thêm
9. Những giới hạn còn lại (nếu có), nhưng phải trung thực

---

## 7. Danh sách deliverable bắt buộc trong codebase

Bạn phải cố gắng tạo ra đầy đủ hoặc tương đương các file sau. Có thể điều chỉnh đường dẫn cho phù hợp codebase, nhưng **không được thiếu tinh thần deliverable**.

### 7.1 Tài liệu
- `docs/chapter4/00-gap-analysis.md`
- `docs/chapter4/01-system-architecture.md`
- `docs/chapter4/02-api-gateway.md`
- `docs/chapter4/03-authentication-security.md`
- `docs/chapter4/04-service-communication.md`
- `docs/chapter4/05-docker-deployment.md`
- `docs/chapter4/06-end-to-end-flow.md`
- `docs/chapter4/07-ai-integration.md`
- `docs/chapter4/08-observability.md`
- `docs/chapter4/09-system-evaluation.md`
- `docs/chapter4/FINAL_CHAPTER4_SUMMARY.md`

### 7.2 Hạ tầng / cấu hình
- `gateway/nginx.conf`
- `docker-compose.yml` hoặc `infrastructure/docker-compose.yml`
- `.env.example`
- các `Dockerfile` cần thiết

### 7.3 Test / script / demo
- ít nhất 1 script hoặc test thể hiện full checkout flow
- ít nhất 1 script hoặc demo cho AI service
- nếu được, thêm health check script hoặc smoke test script

### 7.4 Evidence
- thư mục gợi ý:
  - `docs/chapter4/evidence/`
  - `docs/chapter4/screenshots/`
  - `docs/chapter4/logs/`
- lưu:
  - log output
  - curl output
  - test output
  - ảnh chụp màn hình nếu có

---

## 8. Chuẩn viết tài liệu bắt buộc

Khi tạo các file markdown, phải tuân thủ:
- viết **nghiêm túc, học thuật, rõ ràng**
- không viết kiểu quá sơ sài
- không chỉ nêu tên file mà phải giải thích nội dung thật sự
- có thể dùng bảng để đối chiếu
- mọi khẳng định quan trọng đều phải gắn với file code hoặc kết quả thực thi
- khi trích dẫn route, command, path thì phải chính xác với codebase sau khi bạn chỉnh sửa

---

## 9. Chuẩn sửa code bắt buộc

Khi sửa code:
- ưu tiên code sạch, dễ đọc
- không hard-code bừa bãi
- config phải đưa vào env nếu hợp lý
- đặt tên service, route, module nhất quán
- tránh duplicate config giữa các service nếu có thể gom hợp lý
- không tạo dead code nếu không dùng
- không để TODO mơ hồ rồi coi như hoàn thành

---

## 10. Điều kiện hoàn thành một mục

Một mục chỉ được coi là **hoàn thành** khi có đủ:
1. code/config thật
2. chạy được hoặc có cơ chế kiểm chứng hợp lệ
3. tài liệu mô tả
4. evidence đi kèm nếu mục đó quan trọng

Ví dụ:
- “Gateway hoàn thành” chỉ khi có `nginx.conf`, route chạy được, có doc mô tả, có test hoặc log chứng minh.
- “JWT hoàn thành” chỉ khi login/token/protected route được chứng minh.
- “Docker hoàn thành” chỉ khi compose/build/run được ghi rõ và có output chứng minh.
- “End-to-end flow hoàn thành” chỉ khi toàn luồng có bằng chứng thực tế.

---

## 11. Những gì tuyệt đối không được làm

- Không được xóa các phần quan trọng hiện có của dự án chỉ để làm cho structure đẹp hơn.
- Không được tạo báo cáo giả khi hệ thống chưa chạy.
- Không được nói “đã đạt checklist” nếu chưa có bằng chứng tương ứng.
- Không được biến Chương 4 thành tài liệu lý thuyết; đây là **nhiệm vụ triển khai thực chiến trong codebase**.
- Không được bỏ qua AI service, vì Chương 4 là phần tiếp nối của Chương 2 và 3.
- Không được quên rằng **product-service thực tế có 10 nhóm loại sản phẩm**, nên mọi mô tả hệ thống phải phản ánh bối cảnh này.
- Không được chỉ làm happy path mà bỏ hoàn toàn error handling trong service communication.
- Không được chỉ tạo Dockerfile nhưng không tổ chức compose/network.
- Không được chỉ tạo file markdown mà không sửa code tương ứng.

---

## 12. Tiêu chí chất lượng cao hơn mức tối thiểu

Nếu codebase cho phép, hãy cố gắng đạt thêm các điểm cộng sau:
- route gateway rõ ràng và sạch
- `make`/script hỗ trợ chạy nhanh
- smoke test script cho toàn hệ thống
- seed/demo data đủ dùng để test Chương 4
- health endpoint cho từng service
- structured logging JSON hoặc gần tương đương
- metrics endpoint hoặc skeleton Prometheus
- Mermaid diagram trong docs
- bảng đối chiếu yêu cầu rất rõ ràng trong summary cuối

---

## 13. Định dạng đầu ra của bạn trong quá trình làm việc

Trong suốt quá trình triển khai, bạn phải:
1. Thực hiện theo từng pha.
2. Sau mỗi pha, cập nhật file markdown tương ứng.
3. Khi kết thúc, tạo `FINAL_CHAPTER4_SUMMARY.md` như hồ sơ nghiệm thu.

Mỗi lần hoàn thành một pha, hãy tự ghi rõ:
- đã sửa file nào
- đã thêm file nào
- tiêu chí Chương 4 nào đã được đáp ứng
- bằng chứng nào đã có
- còn thiếu gì

---

## 14. Kết quả cuối cùng mong muốn

Khi hoàn tất công việc, người chấm hoặc người kiểm tra codebase phải có thể nhìn thấy rõ rằng dự án:
- là một **hệ thống microservices hoàn chỉnh**
- có **API Gateway**
- có **JWT Auth**
- có **Docker Compose chạy được**
- có **flow order → payment → shipping**
- có **AI service tích hợp vào hệ thống**
- có **logging/monitoring hoặc cấu trúc observability phù hợp**
- có **tài liệu và evidence đầy đủ**
- và **đạt toàn bộ checklist của Chương 4**

---

## 15. Hành động bắt đầu ngay bây giờ

Hãy bắt đầu bằng cách:

1. Khảo sát codebase hiện tại.
2. Tạo `docs/chapter4/00-gap-analysis.md`.
3. Lập danh sách cụ thể những phần đã đạt và chưa đạt so với Chương 4.
4. Sau đó triển khai lần lượt các pha còn lại cho đến khi toàn bộ checklist được đáp ứng.

**Không dừng ở phân tích. Hãy trực tiếp chỉnh sửa codebase, cấu hình, tài liệu, script và deliverable cho đến khi Chương 4 được hoàn thiện ở mức có thể kiểm chứng.**
