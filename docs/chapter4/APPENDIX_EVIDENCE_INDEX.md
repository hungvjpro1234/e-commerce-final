# PHỤ LỤC B - EVIDENCE INDEX

Phụ lục này lập chỉ mục evidence để đối chiếu nhanh giữa yêu cầu Chương 4, code và kết quả thực thi.

## B1. Evidence về kiến trúc và gateway

| Path | Mô tả ngắn | Chứng minh tiêu chí | Cách mở/cách dùng |
| --- | --- | --- | --- |
| `gateway/nginx.conf` | Cấu hình Nginx gateway thực thi route, headers, block internal route | Có API Gateway, route mapping, security headers | Mở file trực tiếp để xem mapping `/api/*` |
| `gateway/Dockerfile` | Đóng gói gateway thành container | Gateway deploy được qua Docker | Mở file để đối chiếu image build |
| `docs/chapter4/evidence/health-check.json` | Kết quả check health qua gateway cho toàn service chính | Gateway hoạt động và route tới service | Mở JSON, xem trường `results` |
| `docs/chapter4/screenshots/gateway-health.png` | Ảnh endpoint health của gateway | Min chứng trực quan gateway runtime | Mở ảnh PNG |
| `docs/chapter4/01-system-architecture.md` | Tài liệu kiến trúc tổng thể | Mô hình microservices và boundary | Mở markdown, mục service ownership |

## B2. Evidence về auth và RBAC

| Path | Mô tả ngắn | Chứng minh tiêu chí | Cách mở/cách dùng |
| --- | --- | --- | --- |
| `docs/chapter4/evidence/auth-rbac-check.json` | Kết quả kiểm tra JWT + RBAC | Login trả token, protected route 401, customer 403/admin 200 | Mở JSON, kiểm tra các trường status |
| `docs/chapter4/evidence/role-flows-check.json` | Kết quả role flow theo vai trò | Hành vi role-based ngoài auth cơ bản | Mở JSON và đối chiếu theo role |
| `user-service/app/serializers.py` | Code phát JWT claim role/user_id | Cấu hình JWT claims | Xem `LoginSerializer.get_token` |
| `user-service/app/views.py` | Route auth và admin route permission | Enforce RBAC tại API | Xem `UserListView`/`LoginView` |
| `docs/chapter4/03-authentication-security.md` | Diễn giải trust model auth | Liên kết code auth với kiến trúc | Mở phần token issuance/validation |

## B3. Evidence về E2E checkout

| Path | Mô tả ngắn | Chứng minh tiêu chí | Cách mở/cách dùng |
| --- | --- | --- | --- |
| `scripts/e2e_checkout_flow.ps1` | Script chạy full flow checkout qua gateway | Có flow login -> browse -> cart -> order -> payment -> shipping | Chạy script bằng PowerShell |
| `docs/chapter4/evidence/e2e-checkout-success.json` | Kết quả flow thành công | Order chuyển `Shipping`, payment `Success`, shipping `Processing` | Mở JSON, đối chiếu status |
| `docs/chapter4/evidence/e2e-checkout-payment-failure.json` | Kết quả flow thất bại có chủ đích | Nhánh payment fail làm order `Cancelled` | Mở JSON, xem `simulated_fail=true` |
| `order-service/app/views.py` | Orchestration code checkout | Điều phối payment/shipping và state transition | Xem `OrderListCreateView.create` |
| `docs/chapter4/06-end-to-end-flow.md` | Tài liệu flow và cách chạy script | Quy trình tái lập evidence E2E | Mở mục command và expected behavior |

## B4. Evidence về Docker/network/runtime

| Path | Mô tả ngắn | Chứng minh tiêu chí | Cách mở/cách dùng |
| --- | --- | --- | --- |
| `docker-compose.yml` | Topology full stack + network + gateway | Docker hóa hệ thống hoàn chỉnh | Mở file, xem services/networks |
| `.env.example` | Env tham chiếu cấp root | Tổ chức biến môi trường tổng quan | Mở file và map với env service |
| `docs/chapter4/logs/compose-ps.txt` | Kết quả container up | Compose chạy các service chính | Mở file txt, kiểm tra trạng thái container |
| `docs/chapter4/logs/network-inspect.json` | Kết quả inspect network Docker | Service chạy cùng network nội bộ | Mở JSON, kiểm tra network membership |
| `docs/chapter4/logs/runtime-logs.txt` | Log runtime đa service | Có logging runtime thực tế | Mở txt, tìm theo service/correlation id |

## B5. Evidence về AI integration

| Path | Mô tả ngắn | Chứng minh tiêu chí | Cách mở/cách dùng |
| --- | --- | --- | --- |
| `scripts/ai_gateway_demo.ps1` | Script demo AI qua gateway | AI có thể gọi qua `/api/ai/*` | Chạy script bằng PowerShell |
| `docs/chapter4/evidence/ai-gateway-demo.json` | Kết quả demo AI runtime | Recommend/chatbot trả dữ liệu sản phẩm thật | Mở JSON, xem top product/category |
| `docs/chapter4/screenshots/ai-recommend-api.png` | Ảnh API recommend | Minh chứng trực quan AI route hoạt động | Mở ảnh PNG |
| `ai-service/app/main.py` | Entrypoint FastAPI + routers | AI service tồn tại độc lập trong kiến trúc | Xem `include_router` |
| `docs/chapter4/07-ai-integration.md` | Tài liệu tích hợp AI vào Chương 4 | Liên hệ Chương 3 -> Chương 4 | Mở mục gateway exposure và demo |

## B6. Evidence về logging, monitoring, health

| Path | Mô tả ngắn | Chứng minh tiêu chí | Cách mở/cách dùng |
| --- | --- | --- | --- |
| `scripts/health_check.ps1` | Script health check qua gateway | Có health endpoint và kiểm tra tổng hợp | Chạy script, lưu output JSON |
| `docs/chapter4/evidence/health-check.json` | Kết quả health runtime | Gateway + service đều reachable | Mở JSON, kiểm tra status từng endpoint |
| `infrastructure/monitoring/prometheus.yml` | Monitoring skeleton | Có nền tảng monitoring (mức skeleton) | Mở file để xem scrape config hiện tại |
| `infrastructure/monitoring/README.md` | Tài liệu monitoring scope | Nêu rõ phạm vi chưa full production | Mở file markdown |
| `docs/chapter4/08-observability.md` | Tổng kết quan sát hệ thống | Mapping logging/health/monitoring | Mở markdown |

## B7. Evidence về đánh giá hệ thống

| Path | Mô tả ngắn | Chứng minh tiêu chí | Cách mở/cách dùng |
| --- | --- | --- | --- |
| `scripts/basic_system_eval.ps1` | Script đo response time lightweight | Có số liệu đánh giá định lượng | Chạy script và lưu JSON |
| `docs/chapter4/evidence/basic-system-eval.json` | Kết quả đo `/health`, `/products`, `/ai/recommend` | Đánh giá hiệu năng mức đồ án | Mở JSON, xem `avg_ms`, `p95_ms` |
| `docs/chapter4/09-system-evaluation.md` | Phân tích strengths/limitations dựa trên evidence | Đánh giá hệ thống theo học thuật | Mở markdown |
| `docs/chapter4/CHECKLIST_VERIFICATION.md` | Checklist đối chiếu code + evidence | Kiểm tra đầy đủ tiêu chí chấm | Mở markdown, theo từng mục 5.x |

## B8. Hướng dẫn đối chiếu nhanh khi chấm

1. Bắt đầu từ `docs/chapter4/CHAPTER4_REPORT_FINAL.md` để xem narrative chính.  
2. Khi gặp code excerpt, tra sang `docs/chapter4/APPENDIX_CODE_EXCERPTS.md`.  
3. Khi cần bằng chứng chạy thật, tra bảng theo nhóm trong file này và mở file evidence tương ứng.  
4. Với tiêu chí checklist, đối chiếu trực tiếp tại `docs/chapter4/CHECKLIST_VERIFICATION.md`.
