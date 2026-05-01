# PHỤ LỤC MINH CHỨNG MỞ RỘNG - PHIÊN BẢN V2

Phụ lục này tổ chức lại toàn bộ tư liệu đối chiếu theo nhóm luận điểm học thuật, nhằm giúp người đọc lần theo lập luận trong báo cáo chính mà không biến phần nội dung thành danh sách kiểm kê rời rạc.

## A. Kiến trúc và Gateway

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/01-system-architecture.md` | Mô tả kiến trúc chuẩn hóa, service boundary, route model | Đọc phần ownership và route exposure |
| `docs/chapter4/02-api-gateway.md` | Diễn giải chính sách ingress và route map | Đối chiếu với `gateway/nginx.conf` |
| `gateway/nginx.conf` | Hiện thực hóa route công khai, policy header, chặn route nội bộ | Tập trung các block `/api/*`, `/internal/*`, `/health` |
| `docs/chapter4/evidence/health-check.json` | Xác nhận gateway định tuyến tới các service chính | Kiểm tra kết quả các endpoint health |
| `docs/chapter4/screenshots/gateway-health.png` | Minh họa gateway vận hành ở lớp ingress | Dùng trong mục 4.3 của báo cáo |
| `docs/chapter4/logs/runtime-logs.txt` | Nhật ký khởi động Nginx và các service nền | Quan sát các dòng `gateway ... ready for start up` |

## B. Auth và RBAC

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/03-authentication-security.md` | Trình bày trust model user token và internal token | Đọc phần token issuance/validation |
| `user-service/app/serializers.py` | Mã phát JWT kèm role claim | Xem `LoginSerializer.get_token` |
| `user-service/app/views.py` | Mã enforce quyền admin trên route quản trị | Xem `permission_classes = [IsAdmin]` |
| `docs/chapter4/evidence/auth-rbac-check.json` | Kiểm tra 401/403/200 theo vai trò và token | Đọc các trường status |
| `docs/chapter4/evidence/role-flows-check.json` | Mô tả hành vi đa vai trò customer/staff/admin | Đối chiếu chuỗi trạng thái nghiệp vụ |
| `docs/chapter4/screenshots/admin-users-fixed.png` | Góc nhìn quản trị sau khi auth hợp lệ | Dùng để minh họa role admin |
| `docs/chapter4/screenshots/staff-orders-fixed.png` | Góc nhìn nhân sự nghiệp vụ | Dùng để minh họa role staff |

## C. End-to-End Checkout

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/06-end-to-end-flow.md` | Mô tả logic luồng mua hàng và replay flow | Đọc sequence 6 bước |
| `order-service/app/views.py` | Logic orchestration order -> payment -> shipping | Xem `OrderListCreateView.create` |
| `order-service/app/service_clients.py` | Cơ chế gọi downstream có timeout/retry | Xem `_send_request` |
| `scripts/e2e_checkout_flow.ps1` | Kịch bản kiểm thử flow qua gateway | Đọc nhánh success và `-SimulatePaymentFailure` |
| `docs/chapter4/evidence/e2e-checkout-success.json` | Trạng thái thành công của checkout | Kiểm tra order/payment/shipping status |
| `docs/chapter4/evidence/e2e-checkout-payment-failure.json` | Trạng thái thất bại có kiểm soát | Kiểm tra order cancelled khi payment failed |
| `docs/chapter4/screenshots/customer-orders-fixed.png` | Trực quan danh sách đơn hàng phía khách | Gắn với phân tích trạng thái đơn |
| `docs/chapter4/screenshots/customer-order-detail-fixed.png` | Trực quan chi tiết đơn | Gắn với phân tích sequence logic |

## D. Docker, Network, Runtime

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/05-docker-deployment.md` | Lập luận về deploy topology và quy trình chạy | Đọc phần topology và startup |
| `docker-compose.yml` | Định nghĩa network, dependencies, env, ports | Xem service map + `ecom-network` |
| `.env.example` | Tổ chức env mức root | Đối chiếu với env service-level |
| `docs/chapter4/logs/compose-ps.txt` | Trạng thái container sau khi dựng stack | Kiểm tra tất cả service ở trạng thái Up |
| `docs/chapter4/logs/network-inspect.json` | Minh chứng mạng nội bộ liên thông | Xem danh sách containers trong network |
| `docs/chapter4/logs/runtime-logs.txt` | Nhật ký chạy service thật | Dùng cho phân tích liveness và startup behavior |

## E. AI Integration

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/07-ai-integration.md` | Đặt AI vào kiến trúc Chương 4 | Đọc phần gateway exposure |
| `ai-service/app/main.py` | Router registration cho các năng lực AI | Xem `include_router(...)` |
| `frontend/lib/ai.ts` | Giao diện client gọi recommendation/chatbot/behavior | Xem các hàm `fetchRecommendations`, `sendChatbotMessage` |
| `scripts/ai_gateway_demo.ps1` | Script kiểm tra AI qua gateway | Đọc chuỗi behavior -> recommend -> chatbot |
| `docs/chapter4/evidence/ai-gateway-demo.json` | Kết quả runtime của AI demo | Kiểm tra top product, query type, context count |
| `docs/chapter4/screenshots/ai-recommend-api.png` | Trực quan endpoint AI recommendation | Dùng trong phần phân tích tích hợp AI |

## F. UI và Role-based Views

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/screenshots/storefront-home.png` | Trực quan giao diện storefront | Liên hệ với bước browse trong E2E |
| `docs/chapter4/screenshots/customer-storefront-fixed.png` | Trực quan storefront ở bản ổn định | Gắn với phần hoàn thiện UX |
| `docs/chapter4/screenshots/customer-orders-fixed.png` | Trực quan lịch sử đơn phía khách | Liên hệ với kết quả orchestration |
| `docs/chapter4/screenshots/customer-order-detail-fixed.png` | Trực quan chi tiết đơn hàng | Liên hệ với trạng thái thanh toán/vận chuyển |
| `docs/chapter4/screenshots/staff-orders-fixed.png` | Trực quan vai trò staff | Gắn với luận điểm RBAC |
| `docs/chapter4/screenshots/admin-users-fixed.png` | Trực quan vai trò admin | Gắn với luận điểm protected admin routes |

## G. Logging, Monitoring, Health

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/08-observability.md` | Tổng hợp hiện trạng observability | Đọc phần implemented vs not implemented |
| `scripts/health_check.ps1` | Kiểm tra liveness xuyên gateway | Đọc target list các endpoint `/health` |
| `docs/chapter4/evidence/health-check.json` | Kết quả health runtime của toàn service chính | Đối chiếu phản hồi theo service |
| `infrastructure/monitoring/prometheus.yml` | Monitoring skeleton cho mở rộng sau đồ án | Xác định phạm vi triển khai hiện tại |
| `docs/chapter4/logs/runtime-logs.txt` | Dữ liệu log phục vụ phân tích vận hành | Dùng trong mục 4.9 |

## H. Đánh giá hệ thống và tổng kết

| Tệp | Vai trò trong lập luận | Cách đối chiếu |
| --- | --- | --- |
| `docs/chapter4/09-system-evaluation.md` | Bình luận hiệu năng, khả năng mở rộng, hạn chế | Đọc phần metrics và discussion |
| `scripts/basic_system_eval.ps1` | Phương pháp đo latency/rps nhẹ | Xem `Measure-Endpoint` |
| `docs/chapter4/evidence/basic-system-eval.json` | Số liệu baseline cho `/health`, `/products`, `/ai/recommend` | Đọc `avg_ms`, `p95_ms`, `approx_rps_single_client` |
| `docs/chapter4/CHECKLIST_VERIFICATION.md` | Bảng đối chiếu tiêu chí Chương 4 | Dùng như tầng kiểm tra cuối |
| `docs/chapter4/FINAL_CHAPTER4_SUMMARY.md` | Bản tổng hợp nghiệm thu trước đó | Dùng tham chiếu chéo với báo cáo V2 |

## I. Tài liệu phase dùng để mở rộng chiều sâu phân tích

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

Nhóm tài liệu này không chỉ cung cấp diễn giải triển khai theo phase, mà còn giúp kiểm tra độ nhất quán giữa mục tiêu kiến trúc, lựa chọn thiết kế và dữ liệu runtime trong toàn bộ Chương 4.
