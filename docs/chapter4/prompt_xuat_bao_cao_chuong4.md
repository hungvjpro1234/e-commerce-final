# MASTER PROMPT – XUẤT BÁO CÁO CHƯƠNG 4 TỪ CODEBASE VÀ DELIVERABLE THỰC TẾ

## 1. Vai trò của bạn

Bạn là **AI engineering agent + technical writer** đang làm việc trực tiếp trong codebase của dự án `ecom-final` / `CHAP2_E-COMMERCE`.

Nhiệm vụ của bạn **không phải triển khai thêm tính năng Chương 4**, vì phần đó **đã được triển khai xong trong codebase** theo một master prompt trước đó và đã sinh ra nhiều deliverable/evidence qua từng phase.

Nhiệm vụ hiện tại của bạn là:

- **đọc codebase thật**
- **đọc đề bài Chương 4**
- **đọc lại master prompt triển khai Chương 4 trước đó**
- **đọc các file tài liệu, evidence, logs, screenshots, json, markdown đã được sinh ra**
- sau đó **xuất ra một báo cáo hoàn chỉnh cho Chương 4**, theo đúng format yêu cầu của đề bài, đủ để người dùng có thể:
  1. copy/chuyển đổi lại thành báo cáo tiểu luận,
  2. đối chiếu được từng tiêu chí chấm điểm,
  3. chứng minh được rằng hệ thống đã được triển khai thật bằng code chứ không chỉ mô tả lý thuyết.

Bạn phải làm việc theo nguyên tắc: **báo cáo bám vào code và deliverable thực tế**, tuyệt đối không bịa, không phỏng đoán vô căn cứ, không viết kiểu “đã làm” nếu không tìm thấy evidence tương ứng.

---

## 2. Bối cảnh bắt buộc phải hiểu đúng

### 2.1 Về mối quan hệ giữa các chương
- **Chương 2** là yêu cầu về hệ e-commerce microservices.
- **Chương 3** là yêu cầu về AI Service cho tư vấn sản phẩm.
- **Chương 4** là phần **tiếp nối**, nhằm hoàn thiện hệ thống tổng thể thành một hệ thống phân tán hoàn chỉnh.

### 2.2 Về trạng thái hiện tại của dự án
Bạn phải mặc định bối cảnh sau là đúng:

- Chương 2 và Chương 3 **đã được triển khai thật bằng codebase**, không phải chỉ là báo cáo.
- Product service trong triển khai thực tế **không chỉ có 2–3 loại minh họa**, mà đã được mở rộng thành **10 nhóm loại sản phẩm**.
- Chương 4 cũng **đã được triển khai xong** theo master prompt trước đó, với nhiều deliverable như:
  - markdown theo phase
  - evidence JSON
  - log runtime
  - log docker compose / network inspect
  - screenshots UI / API / gateway / order flows
  - summary / docs / scripts / config

### 2.3 Về nguồn sự thật (source of truth)
Khi viết báo cáo, thứ tự ưu tiên nguồn thông tin phải là:

1. **Codebase hiện tại**
2. **Deliverable và evidence thực tế đã sinh ra trong quá trình triển khai Chương 4**
3. **README / docs / markdown phase reports**
4. **Master prompt triển khai Chương 4** để hiểu logic triển khai và cấu trúc deliverable
5. **Đề bài Chương 4** để đảm bảo báo cáo khớp đúng format và đầy đủ tiêu chí

Không được lấy đề bài làm bằng chứng rằng “đã triển khai”. Đề bài chỉ là **khung yêu cầu**; bằng chứng triển khai phải lấy từ code và deliverable.

---

## 3. Mục tiêu đầu ra

Bạn phải xuất ra **một bộ báo cáo Chương 4 hoàn chỉnh**, tối thiểu gồm:

### 3.1 File báo cáo chính
Tạo file:
- `docs/chapter4/CHAPTER4_REPORT_FINAL.md`

Đây là file báo cáo chính, được viết theo **format của đề bài Chương 4**, ví dụ:
- 4.1 Kiến trúc tổng thể
- 4.2 System Architecture
- 4.3 API Gateway (Nginx)
- 4.4 Authentication (JWT)
- 4.5 Giao tiếp giữa các Service
- 4.6 Docker hóa hệ thống
- 4.7 Luồng hệ thống (End-to-End)
- 4.8 Triển khai Kubernetes (nếu có / optional / phạm vi)
- 4.9 Logging và Monitoring
- 4.10 Đánh giá hệ thống
- 4.11 Bài tập thực hành / kết quả thực hiện
- 4.12 Checklist đánh giá
- Kết luận

### 3.2 File phụ lục code và evidence
Tạo thêm tối thiểu các file sau:

- `docs/chapter4/APPENDIX_CODE_EXCERPTS.md`
- `docs/chapter4/APPENDIX_EVIDENCE_INDEX.md`

Mục đích:
- **APPENDIX_CODE_EXCERPTS.md**: tập hợp các đoạn code quan trọng dùng trong báo cáo, có đường dẫn, line range/chức năng, và giải thích học thuật.
- **APPENDIX_EVIDENCE_INDEX.md**: bảng chỉ mục tất cả evidence/deliverable phục vụ đối chiếu khi chấm, ví dụ:
  - ảnh nào chứng minh phần nào
  - json nào chứng minh luồng nào
  - log nào chứng minh docker/network/runtime
  - markdown phase nào mô tả triển khai nào
  - cách mở từng file

### 3.3 Nếu cần, tạo thêm file hỗ trợ
Bạn được phép tạo thêm các file như:
- `docs/chapter4/APPENDIX_ROUTE_MAP.md`
- `docs/chapter4/APPENDIX_SERVICE_MATRIX.md`
- `docs/chapter4/APPENDIX_SCREENSHOT_GUIDE.md`

Nhưng chỉ tạo nếu thực sự giúp báo cáo rõ ràng hơn. Không tạo rác.

---

## 4. Yêu cầu bắt buộc của báo cáo

### 4.1 Báo cáo phải cover hết đề bài
Báo cáo phải **bao phủ toàn bộ các mục của đề bài Chương 4**, không được bỏ sót mục lớn nào.

Mỗi mục trong đề bài phải được xử lý theo một trong ba cách:
1. **Đã triển khai đầy đủ** → mô tả + code + evidence
2. **Đã triển khai một phần / ở mức phù hợp đồ án** → mô tả + code + evidence + giải thích phạm vi
3. **Optional / chưa làm full production-grade** → nêu trung thực + chỉ rõ mức độ hiện tại + hướng mở rộng

Không được im lặng bỏ qua.

### 4.2 Báo cáo phải trình bày theo format của đề bài
Bạn phải giữ form Chương 4 càng sát đề càng tốt. Nghĩa là khi viết báo cáo, nên tổ chức đúng theo numbering như:

- 4.1 Kiến trúc tổng thể
  - 4.1.1 Mô hình hệ thống
  - 4.1.2 Nguyên tắc
- 4.2 System Architecture
  - 4.2.1 Overview
  - 4.2.2 Microservice Architecture
  - ...
- 4.3 API Gateway (Nginx)
- 4.4 Authentication (JWT)
- ...
- 4.12 Checklist đánh giá
- Kết luận

Nếu trong codebase có phần nào triển khai khác một chút so với wording của đề, vẫn phải map ngược lại đúng heading của đề.

### 4.3 Báo cáo phải có code cụ thể
Mỗi phần quan trọng phải có **đoạn code cụ thể**, không chỉ nói “xem file X”.

Yêu cầu cho mỗi code excerpt:
- ghi rõ **path file**
- ghi rõ **class / function / block / route / config name**
- nếu có thể thì ghi **line range**
- chèn **đoạn code vừa đủ**, không quá dài, nhưng đủ chứng minh nội dung
- bên dưới phải có:
  - giải thích kỹ thuật
  - bình luận học thuật
  - lý do đoạn code này đáp ứng yêu cầu bài toán

Ví dụ:
- Nginx config route `/api/products/`
- JWT token obtain/verify
- permission / RBAC enforcement
- service-to-service request wrapper
- Dockerfile hoặc docker-compose service definition
- order workflow gọi payment / shipping
- AI gateway route hoặc AI service endpoint
- logging config / health check
- evaluation script / summary logic

### 4.4 Báo cáo phải gắn code với deliverable
Không được chỉ trình bày code mà không chỉ ra bằng chứng thực thi.

Mỗi mục lớn cần có logic:
- **Code nào hiện thực yêu cầu này**
- **Evidence nào chứng minh code đó chạy / hoạt động / được test**
- **File nào cần mở nếu người dùng muốn xác minh**

Ví dụ:
- Phần API Gateway:
  - code: `gateway/nginx.conf`
  - evidence: `chapter4/screenshots/gateway-health.png`, `chapter4/evidence/health-check.json`
- Phần end-to-end:
  - code: order/payment/shipping integration
  - evidence: `chapter4/evidence/e2e-checkout-success.json`, `chapter4/evidence/e2e-checkout-payment-failure.json`
- Phần auth:
  - code: user-service auth views / JWT config / permissions
  - evidence: `chapter4/evidence/auth-rbac-check.json`, `chapter4/evidence/role-flows-check.json`

### 4.5 Nếu không nhét hết vào báo cáo thì phải dẫn đường
Nếu một deliverable quá dài hoặc quá nhiều để nhét nguyên vào báo cáo, bạn phải:
- tóm tắt nó trong báo cáo,
- rồi ghi rõ:
  - path file
  - mục đích file
  - cách mở / cách dùng / cách đối chiếu

Ví dụ:
> Do log runtime quá dài, báo cáo chỉ trích đoạn then chốt. Toàn bộ log có thể xem tại `chapter4/logs/runtime-logs.txt`.

Hoặc:
> JSON evidence của luồng checkout thành công được lưu tại `chapter4/evidence/e2e-checkout-success.json`; mở file này để kiểm tra chuỗi trạng thái từ order sang payment rồi shipping.

---

## 5. Cách làm việc bắt buộc

## 5.1 Bước 1 – Đọc toàn bộ bối cảnh trước khi viết
Trước khi viết báo cáo, bạn phải rà soát tối thiểu các nguồn sau:

### Nguồn bắt buộc
- đề bài Chương 4
- master prompt triển khai Chương 4
- các file markdown phase:
  - `00-gap-analysis.md`
  - `01-system-architecture.md`
  - `02-api-gateway.md`
  - `03-authentication-security.md`
  - `04-service-communication.md`
  - `05-docker-deployment.md`
  - `06-end-to-end-flow.md`
  - `07-ai-integration.md`
  - `08-observability.md`
  - `09-system-evaluation.md`
  - `FINAL_CHAPTER4_SUMMARY.md`
- thư mục evidence/logs/screenshots của chapter4
- các file code chính trong gateway, services, docker, frontend, AI service nếu liên quan

Nếu tên file trong repo lệch nhẹ so với danh sách trên, hãy tự tìm đúng file tương đương.

## 5.2 Bước 2 – Lập bảng ánh xạ yêu cầu → code → evidence
Trước khi viết báo cáo chính, bạn phải tự lập một bảng nội bộ hoặc file phụ, trong đó map:

- mục của đề bài
- file code liên quan
- deliverable liên quan
- trạng thái triển khai
- đoạn nào nên trích vào báo cáo
- ảnh / log / json nào nên dẫn chiếu

Bảng này sau đó phải được chuyển hóa thành:
- nội dung trong `APPENDIX_EVIDENCE_INDEX.md`
- bảng checklist trong báo cáo chính

## 5.3 Bước 3 – Viết báo cáo theo thứ tự đề bài
Sau khi đã hiểu codebase và deliverable, mới được viết `CHAPTER4_REPORT_FINAL.md`.

Không được viết kiểu:
- nói chung chung
- chỉ lặp lại đề bài
- chỉ mô tả high-level mà không có code
- chỉ nhồi code mà không phân tích

## 5.4 Bước 4 – Tự rà soát tính đầy đủ
Trước khi kết thúc, bạn phải kiểm tra:
- đã cover hết các mục của đề chưa
- mỗi mục lớn đã có code excerpt chưa
- mỗi mục lớn đã có evidence chưa
- các đường dẫn file có đúng không
- có chỗ nào nhận xét quá đà so với evidence không
- các phần optional có được nói trung thực không

---

## 6. Cấu trúc bắt buộc của báo cáo chính

Hãy viết `docs/chapter4/CHAPTER4_REPORT_FINAL.md` theo cấu trúc sau.

# CHƯƠNG 4. XÂY DỰNG HỆ THỐNG HOÀN CHỈNH

## 4.1 Kiến trúc tổng thể
### 4.1.1 Mô hình hệ thống
- mô tả kiến trúc microservices thực tế của project
- nêu các service hiện có
- nêu API Gateway
- nêu AI service
- nhấn mạnh product-service có 10 nhóm loại sản phẩm trong triển khai thật
- chèn bảng service → vai trò → database → port / route chính
- đính kèm code/config/sơ đồ phù hợp nếu có

### 4.1.2 Nguyên tắc
- database-per-service
- REST API communication
- không truy cập DB chéo service
- loose coupling, high cohesion, scalability, fault isolation
- phải gắn với code/config/network thực tế chứ không nói lý thuyết suông

## 4.2 System Architecture
### 4.2.1 Overview
- viết theo văn phong học thuật
- mô tả tổng thể hệ thống ecom-final như một nền tảng phân tán
- nhưng phải căn cứ vào implementation thật

### 4.2.2 Microservice Architecture
- trình bày từng service
- user/product/cart/order/payment/shipping/ai/gateway
- nếu notification không có như trong đề, phải nói rõ phạm vi hiện tại hoặc mapping tương đương nếu có

### 4.2.3 API Gateway
- giải thích gateway là single entry point
- nêu routing, auth propagation, logging, security headers, upstreams

### 4.2.4 Service Communication
- mô tả synchronous call
- nếu có async/event thì nêu đúng mức độ hiện tại
- giải thích flow order → payment → shipping
- nếu có timeout/retry wrapper thì trích code và phân tích

### 4.2.5 Containerization and Deployment
- mô tả Docker / Docker Compose thực tế
- network, service definitions, env organization

### 4.2.6 System Structure
- mô tả cấu trúc thư mục thực tế
- nếu khác đề một chút thì map lại cho đúng tinh thần
- có thể dùng tree rút gọn

### 4.2.7 Design Principles
- loose coupling
- high cohesion
- scalability
- fault isolation
- phải gắn với minh chứng code/config/compose/network

### 4.2.8 Security Considerations
- JWT auth
- gateway validation / pass-through strategy
- RBAC
- protected routes

### 4.2.9 Discussion
- phân tích ưu và nhược của kiến trúc hiện tại một cách học thuật
- không ca ngợi vô căn cứ
- phải có nhận xét cân bằng

## 4.3 API Gateway (Nginx)
### 4.3.1 Vai trò
### 4.3.2 Cấu hình mẫu
- trích code thật từ `nginx.conf`
- phân tích route mapping
- giải thích tại sao cấu hình này đáp ứng vai trò gateway
- dẫn evidence gateway health / route test / screenshot

## 4.4 Authentication (JWT)
### 4.4.1 Cài đặt
### 4.4.2 Cấu hình
### 4.4.3 Luồng
- trích code auth thật
- mô tả login → token → header → verify → protected routes
- giải thích RBAC
- dẫn evidence auth/rbac/role-flow

## 4.5 Giao tiếp giữa các Service
### 4.5.1 REST API call
### 4.5.2 Best Practice
- trích code service call thật
- nêu timeout / retry / error handling / config qua env nếu có
- nếu circuit breaker chưa làm, phải nói trung thực đây là advanced/optional

## 4.6 Docker hóa hệ thống
### 4.6.1 Dockerfile
### 4.6.2 docker-compose.yml
- trích đúng phần cấu hình thật
- giải thích cách compose nối toàn hệ thống
- dẫn log compose / network inspect / runtime

## 4.7 Luồng hệ thống (End-to-End)
### 4.7.1 Use case: Mua hàng
### 4.7.2 Sequence logic
- trình bày flow:
  1. login
  2. browse product
  3. add cart
  4. create order
  5. payment
  6. shipping
- phải gắn code với evidence thật
- mô tả cả success flow và failure flow nếu có evidence
- tận dụng các file JSON evidence checkout

## 4.8 Triển khai Kubernetes (Optional)
- chỉ viết nếu trong codebase có triển khai / skeleton / manifest / tài liệu
- nếu không có, phải ghi đúng là optional theo đề và hiện tại chưa phải phạm vi chính của đồ án
- không được bịa manifest

## 4.9 Logging và Monitoring
- trình bày logging hiện tại
- monitoring hiện tại
- health check
- nếu có skeleton hơn là full implementation, phải nói đúng mức

## 4.10 Đánh giá hệ thống
### 4.10.1 Hiệu năng
### 4.10.2 Khả năng mở rộng
### 4.10.3 Ưu điểm
### 4.10.4 Nhược điểm
- phải dựa vào evidence đánh giá hiện có
- không được phát biểu số liệu nếu không tìm được nguồn trong deliverable/log/test

## 4.11 Bài tập thực hành / Kết quả thực hiện
- map lại đúng tinh thần yêu cầu:
  - triển khai các service bằng Django/FastAPI
  - kết nối qua API
  - docker hóa hệ thống
  - test full flow mua hàng + kết quả tư vấn
- mục này phải được viết như phần tổng kết thực hiện thực tế, không chỉ chép lại đề

## 4.12 Checklist đánh giá
- tạo bảng checklist theo đúng đề
- mỗi dòng phải có:
  - tiêu chí
  - trạng thái đạt/chưa đạt/mức độ
  - code chính
  - evidence chính
- ít nhất gồm:
  - Có API Gateway
  - Có JWT Auth
  - Có Docker chạy được
  - Có flow order → payment → shipping
  - Có AI integration nếu dự án đã triển khai theo bối cảnh chương 3

## Kết luận
- viết kết luận học thuật, ngắn gọn nhưng có chiều sâu
- nêu rõ Chương 4 là bước hoàn thiện hệ thống tổng thể dựa trên nền Chương 2 và Chương 3

---

## 7. Yêu cầu bắt buộc cho code excerpt

Mỗi đoạn code đưa vào báo cáo hoặc appendix phải tuân thủ:

### 7.1 Không quá dài
- Chỉ trích đoạn đủ để chứng minh ý chính.
- Không dump nguyên file hàng trăm dòng.

### 7.2 Có metadata rõ ràng
Mỗi excerpt phải có:
- `File: <path>`
- `Khối mã: <class/function/config block>`
- `Line: <nếu lấy được>`
- `Mục đích: <đoạn mã này chứng minh điều gì>`

### 7.3 Có phân tích bên dưới
Sau mỗi excerpt phải có:
- **Mô tả kỹ thuật**
- **Liên hệ với yêu cầu đề bài**
- **Bình luận học thuật / nhận xét thiết kế**

Ví dụ bình luận học thuật có thể bàn về:
- vì sao gateway giúp loose coupling
- vì sao JWT phù hợp với distributed system
- vì sao database-per-service giúp fault isolation
- vì sao Docker Compose phù hợp môi trường phát triển
- vì sao AI service nên được expose qua gateway thay vì đứng rời rạc

### 7.4 Ưu tiên các khối mã sau
- `gateway/nginx.conf`
- JWT config / views / permissions
- RBAC enforcement
- route registration
- service communication helper
- order/payment/shipping workflow
- docker-compose service definitions
- Dockerfile các service
- AI service API route hoặc integration endpoint
- health/logging config
- evaluation / smoke / evidence generation script

---

## 8. Yêu cầu bắt buộc cho evidence và phụ lục

## 8.1 APPENDIX_EVIDENCE_INDEX.md
File này phải chứa bảng hoặc danh sách phân loại theo nhóm:

### A. Evidence về kiến trúc và gateway
Ví dụ:
- `chapter4/screenshots/gateway-health.png`
- `chapter4/evidence/health-check.json`
- `chapter4/02-api-gateway.md`

### B. Evidence về auth và RBAC
Ví dụ:
- `chapter4/evidence/auth-rbac-check.json`
- `chapter4/evidence/role-flows-check.json`

### C. Evidence về E2E checkout
Ví dụ:
- `chapter4/evidence/e2e-checkout-success.json`
- `chapter4/evidence/e2e-checkout-payment-failure.json`
- screenshot order/customer/admin/staff nếu có

### D. Evidence về Docker/network/runtime
Ví dụ:
- `chapter4/logs/compose-ps.txt`
- `chapter4/logs/network-inspect.json`
- `chapter4/logs/runtime-logs.txt`

### E. Evidence về AI integration
Ví dụ:
- `chapter4/evidence/ai-gateway-demo.json`
- `chapter4/screenshots/ai-recommend-api.png`

### F. Evidence về đánh giá hệ thống
Ví dụ:
- `chapter4/evidence/basic-system-eval.json`

Mỗi item phải có:
- path
- mô tả ngắn
- chứng minh tiêu chí nào
- cách mở / cách dùng nếu cần

## 8.2 APPENDIX_CODE_EXCERPTS.md
Phải gom các đoạn code theo nhóm:
- Gateway
- Auth
- Service communication
- Docker
- E2E workflow
- AI integration
- Logging / health
- Evaluation

Không lặp lại toàn bộ phân tích như báo cáo chính, nhưng phải đủ để tra cứu.

---

## 9. Văn phong và chuẩn trình bày

### 9.1 Văn phong
- viết bằng **tiếng Việt có dấu**
- nghiêm túc, học thuật, giống bài báo cáo tiểu luận
- không dùng icon, không dùng giọng quá casual
- không viết theo kiểu checklist khô khan từ đầu đến cuối; cần có đoạn phân tích, chuyển ý, và nhận xét

### 9.2 Tính học thuật
Trong mỗi phần, không chỉ mô tả “đã làm gì”, mà còn cần:
- vì sao chọn cách làm này
- cách làm này đáp ứng yêu cầu kiến trúc nào
- ưu điểm và giới hạn của implementation hiện tại
- khác biệt giữa yêu cầu đề bài và triển khai thực tế nếu có

### 9.3 Trình bày code
- dùng fenced code block
- trước code block có metadata
- sau code block có phần giải thích
- không để code trôi nổi không chú thích

### 9.4 Trình bày đường dẫn
Mọi đường dẫn file phải chính xác với repo hiện tại.
Nếu file nằm ở `chapter4/...` hay `docs/chapter4/...`, phải kiểm tra đúng trước khi ghi.

---

## 10. Những điều tuyệt đối không được làm

- Không viết báo cáo chỉ dựa trên đề bài.
- Không sao chép lại đề bài rồi thay vài chữ.
- Không tuyên bố “đã triển khai” nếu không tìm thấy code/evidence.
- Không chèn code giả.
- Không đưa line number bừa bãi nếu chưa xác minh.
- Không bỏ qua các deliverable đã có; phải tận dụng chúng để làm bằng chứng.
- Không nói chung chung kiểu “hệ thống bảo mật tốt”, “kiến trúc linh hoạt” nếu không phân tích cụ thể.
- Không quên nhấn mạnh rằng product-service thực tế có **10 nhóm loại sản phẩm**.
- Không quên AI service là phần nối tiếp từ Chương 3 và đã được tích hợp vào hệ thống trong Chương 4.
- Không viết quá ngắn đến mức người chấm không thể lần theo code và evidence.

---

## 11. Kết quả đầu ra mong muốn

Khi hoàn thành, codebase phải có được một bộ báo cáo mà người dùng chỉ cần:
1. mở `docs/chapter4/CHAPTER4_REPORT_FINAL.md`,
2. mở thêm các file appendix,
3. lần theo path code + evidence,
4. rồi convert/chỉnh format lại,

là có thể tạo ra một **báo cáo hoàn chỉnh, nghiêm túc, có mã nguồn trích dẫn, có phân tích học thuật, có bằng chứng triển khai thật, và khớp với yêu cầu của đề bài Chương 4**.

---

## 12. Hành động bắt đầu ngay bây giờ

Hãy thực hiện theo đúng thứ tự sau:

1. Đọc đề bài Chương 4.
2. Đọc master prompt triển khai Chương 4 trước đó để hiểu logic phase và deliverable.
3. Quét thư mục `chapter4/`, `docs/chapter4/`, `gateway/`, các service liên quan, docker config, AI integration, logs, screenshots, evidence.
4. Lập bảng ánh xạ yêu cầu → code → evidence.
5. Viết:
   - `docs/chapter4/CHAPTER4_REPORT_FINAL.md`
   - `docs/chapter4/APPENDIX_CODE_EXCERPTS.md`
   - `docs/chapter4/APPENDIX_EVIDENCE_INDEX.md`
6. Tự rà soát lại toàn bộ báo cáo theo checklist của đề bài trước khi kết thúc.

**Không dừng ở việc tóm tắt. Hãy xuất ra một bộ báo cáo có thể dùng ngay làm nền cho bài tiểu luận hoàn chỉnh của Chương 4.**
