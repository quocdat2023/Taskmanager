# TÀI LIỆU YÊU CẦU NGHIỆP VỤ

# BUSINESS REQUIREMENTS DOCUMENT (BRD)

---

**Tên dự án:** EduTask Manager – Hệ thống Quản lý Học vụ và Nhiệm vụ Trực tuyến

**Phiên bản tài liệu:** 2.0

**Ngày soạn thảo:** 29/03/2026

**Phiên bản trước:** 1.0 (25/03/2026)

**Trạng thái:** Bản chính thức

**Người soạn thảo:** Business Analysis Team

---

## MỤC LỤC

1. [Tổng quan dự án (Executive Summary)](#1-tổng-quan-dự-án-executive-summary)
2. [Phạm vi dự án (Project Scope)](#2-phạm-vi-dự-án-project-scope)
3. [Các bên liên quan & Vai trò người dùng (Stakeholders & User Roles)](#3-các-bên-liên-quan--vai-trò-người-dùng)
4. [Yêu cầu nghiệp vụ cốt lõi (Key Business Requirements)](#4-yêu-cầu-nghiệp-vụ-cốt-lõi-key-business-requirements)
5. [Yêu cầu chức năng (Functional Requirements)](#5-yêu-cầu-chức-năng-functional-requirements)
6. [Yêu cầu phi chức năng (Non-Functional Requirements)](#6-yêu-cầu-phi-chức-năng-non-functional-requirements)
7. [Giả định (Assumptions)](#7-giả-định-assumptions)
8. [Ràng buộc (Constraints)](#8-ràng-buộc-constraints)
9. [Lịch sử thay đổi tài liệu (Change Log)](#9-lịch-sử-thay-đổi-tài-liệu-change-log)
10. [Thuật ngữ (Glossary)](#10-thuật-ngữ-glossary)

---

# 1. Tổng quan dự án (Executive Summary)

## 1.1. Mục đích tài liệu

Tài liệu Business Requirements Document (BRD) phiên bản 2.0 này được cập nhật nhằm phản ánh đầy đủ và chính xác toàn bộ yêu cầu nghiệp vụ hiện tại của dự án **EduTask Manager**, bao gồm các tính năng mới được bổ sung kể từ phiên bản 1.0. Tài liệu đóng vai trò là nguồn tham chiếu duy nhất (*single source of truth*) cho tất cả các bên liên quan: nhóm phát triển, nhóm kiểm thử (QA/QC), ban quản lý dự án và đối tác triển khai.

## 1.2. Tóm tắt dự án

**EduTask Manager** là một nền tảng web quản lý học vụ và nhiệm vụ trực tuyến, được thiết kế đặc thù cho môi trường giáo dục đại học. Hệ thống giải quyết bài toán phân tán thông tin trong công tác giảng dạy và học tập bằng cách tích hợp trên một nền tảng duy nhất các chức năng:

- Quản lý nhiệm vụ học tập theo nhóm lớp (với Kanban Board thời gian thực)
- Lịch học và sự kiện (có nhắc nhở tự động qua email)
- Kho tài liệu học thuật tập trung
- Diễn đàn hỏi đáp (QnA) có kiểm duyệt nội dung
- Trò chuyện trực tiếp 1-1 (Real-time Chat)
- Hệ thống thông báo đa kênh (In-app + Email)
- Quản trị hệ thống toàn diện (người dùng, năm học, kiểm duyệt nội dung)

Hệ thống được xây dựng trên kiến trúc **REST API** kết hợp **WebSocket (Socket.IO)**, đảm bảo mọi cập nhật được phản ánh tức thì mà không cần tải lại trang.

## 1.3. Bối cảnh và vấn đề nghiệp vụ

Trong môi trường đại học, sự phối hợp giữa Giảng viên và Sinh viên thường gặp các vấn đề:

| STT | Vấn đề | Tác động |
|-----|--------|----------|
| 1 | Quản lý nhiệm vụ rời rạc qua nhiều kênh | Bỏ sót deadline, nhầm lẫn thông tin |
| 2 | Thiếu công cụ theo dõi tiến độ trực quan | Giảng viên không nắm được tiến độ sinh viên |
| 3 | Lịch học phân tán trên nhiều hệ thống | Thiếu đồng bộ, quên lịch thi/họp |
| 4 | Giao tiếp học thuật không có tổ chức | Khó lưu trữ, tìm kiếm câu hỏi/trả lời |
| 5 | Thiếu kiểm soát nội dung trong thảo luận | Nội dung không phù hợp không được kiểm duyệt |

**EduTask Manager** thống nhất toàn bộ quy trình trên vào một nền tảng số hóa duy nhất.

## 1.4. Mục tiêu kinh doanh (Business Goals)

| Mã | Mục tiêu | Chỉ số đo lường (KPI) |
|----|----------|------------------------|
| BG-01 | Tập trung hóa quản lý nhiệm vụ học tập | 100% nhiệm vụ được tạo, giao và theo dõi trên hệ thống |
| BG-02 | Tăng tỷ lệ hoàn thành bài tập đúng hạn | Tăng ≥ 20% so với phương pháp thủ công |
| BG-03 | Rút ngắn thời gian phản hồi học thuật | Thời gian trả lời câu hỏi trung bình < 24 giờ |
| BG-04 | Nâng cao tính minh bạch trong đánh giá | 100% lịch sử thay đổi nhiệm vụ được ghi lại |
| BG-05 | Hỗ trợ vận hành đa năm học, đa học kỳ | Dữ liệu được tổ chức theo năm học và học kỳ |
| BG-06 | Đảm bảo chất lượng nội dung thảo luận | 100% nội dung QnA có thể được kiểm duyệt bởi Admin |
| BG-07 | Bảo vệ toàn vẹn dữ liệu tham chiếu | Ngăn chặn xóa năm học đang được sử dụng |

---

# 2. Phạm vi dự án (Project Scope)

## 2.1. Trong phạm vi (In-Scope)

- **Module Xác thực & Phân quyền:** Đăng ký, đăng nhập JWT, RBAC (Admin/Teacher/Student), ghi nhận hoạt động đăng nhập
- **Module Quản lý Nhiệm vụ:** CRUD nhiệm vụ, subtasks, giao việc có phê duyệt, Kanban Board thời gian thực, lịch sử audit, quản lý quyền truy cập nhiệm vụ
- **Module Lịch học & Sự kiện:** Quản lý lịch, sự kiện lặp lại, nhắc nhở email tự động
- **Module Kho Tài liệu:** Tải lên/xuống, phân loại theo danh mục và môn học
- **Module Hỏi & Đáp (QnA):** Đặt câu hỏi, trả lời phân cấp, chấp nhận câu trả lời, kiểm duyệt nội dung bởi Admin
- **Module Trò chuyện:** Nhắn tin 1-1 thời gian thực qua WebSocket
- **Module Thông báo:** Đa kênh (In-app + Email), thông báo theo ngữ cảnh và vai trò
- **Module Quản lý Người dùng:** Duyệt tài khoản, khóa/mở khóa, phân quyền
- **Module Quản lý Năm học:** CRUD năm học, bảo vệ toàn vẹn dữ liệu tham chiếu
- **Module Cài đặt Cá nhân:** Hồ sơ, avatar, tùy chỉnh nhắc nhở
- **Hạ tầng & Vận hành:** Docker, Nginx, Prometheus, Grafana, Redis

## 2.2. Ngoài phạm vi (Out-of-Scope)

- Tích hợp LMS bên ngoài (Moodle, Canvas)
- Thi trực tuyến, chấm bài tự động
- Ứng dụng di động native (iOS/Android)
- Thanh toán học phí
- Báo cáo BI phức tạp
- Hỗ trợ đa ngôn ngữ (i18n)
- Single Sign-On (SSO)

---

# 3. Các bên liên quan & Vai trò người dùng

## 3.1. Danh sách các bên liên quan (Stakeholders)

| STT | Bên liên quan | Mức độ quan tâm | Trách nhiệm |
|-----|---------------|-----------------|-------------|
| 1 | Ban Giám hiệu / Phòng Đào tạo | Cao | Phê duyệt triển khai, cung cấp yêu cầu cấp cao |
| 2 | Giảng viên | Rất cao | Tạo nhiệm vụ, tài liệu, lịch học; tương tác QnA |
| 3 | Sinh viên | Rất cao | Thực hiện nhiệm vụ, tương tác học thuật |
| 4 | Quản trị viên hệ thống | Cao | Vận hành, giám sát, kiểm duyệt toàn bộ hệ thống |
| 5 | Nhóm phát triển kỹ thuật | Cao | Xây dựng, triển khai, bảo trì |
| 6 | Nhóm QA/QC | Trung bình | Kiểm thử chất lượng, nghiệm thu |

## 3.2. Vai trò người dùng và quyền hạn

### 3.2.1. Quản trị viên (Admin)

| Nhóm chức năng | Quyền hạn |
|----------------|-----------|
| Quản lý người dùng | Duyệt, khóa, mở khóa, xóa tài khoản; thay đổi vai trò |
| Quản lý nhiệm vụ | Tạo/sửa/xóa bất kỳ nhiệm vụ; xử lý yêu cầu phê duyệt; giao việc trực tiếp |
| Quản lý năm học | Tạo, sửa, xóa năm học (có kiểm tra ràng buộc dữ liệu) |
| Kiểm duyệt QnA | Xem, ẩn, xóa mềm câu trả lời; tìm kiếm và phân trang nội dung |
| Giám sát hệ thống | Dashboard Grafana/Prometheus; xem lịch sử hoạt động |
| Thông báo | Gửi thông báo đến toàn bộ người dùng |

### 3.2.2. Giảng viên (Teacher)

| Nhóm chức năng | Quyền hạn |
|----------------|-----------|
| Nhiệm vụ | Tạo nhiệm vụ; giao cho sinh viên (qua phê duyệt Admin); theo dõi tiến độ |
| Lịch học | Tạo, sửa, xóa lịch học, lịch thi, sự kiện |
| Tài liệu | Tải lên, quản lý, xóa tài liệu |
| QnA | Trả lời, chấp nhận câu trả lời tốt nhất |
| Chat | Nhắn tin trực tiếp với sinh viên và đồng nghiệp |

### 3.2.3. Sinh viên (Student)

| Nhóm chức năng | Quyền hạn |
|----------------|-----------|
| Nhiệm vụ | Xem nhiệm vụ được giao; cập nhật trạng thái cá nhân; yêu cầu giao/rút |
| Lịch học | Xem lịch học của bản thân |
| Tài liệu | Xem và tải xuống tài liệu |
| QnA | Đặt câu hỏi và trả lời |
| Chat | Nhắn tin trực tiếp |
| Cài đặt | Chỉnh sửa hồ sơ, avatar, tùy chỉnh nhắc nhở |

---

# 4. Yêu cầu nghiệp vụ cốt lõi (Key Business Requirements)

| Mã | Yêu cầu | Mô tả | Mức ưu tiên |
|----|---------|-------|-------------|
| KR-01 | Xác thực và phân quyền bảo mật | Hệ thống phải xác thực người dùng bằng JWT và phân quyền theo vai trò RBAC | Cao |
| KR-02 | Quản lý vòng đời nhiệm vụ hoàn chỉnh | Hỗ trợ đầy đủ: tạo → giao → theo dõi → hoàn thành, với lịch sử audit | Cao |
| KR-03 | Giao tiếp thời gian thực | Mọi thay đổi trạng thái phải được phản ánh tức thì qua WebSocket | Cao |
| KR-04 | Kiểm soát quyền truy cập nhiệm vụ | Chỉ người tạo, người được giao và Admin mới được xem nhiệm vụ | Cao |
| KR-05 | Kiểm duyệt nội dung QnA | Admin có thể ẩn/xóa mềm nội dung không phù hợp trong diễn đàn | Trung bình |
| KR-06 | Bảo vệ toàn vẹn dữ liệu | Không cho phép xóa năm học đang được tham chiếu bởi nhiệm vụ | Cao |
| KR-07 | Thông báo theo ngữ cảnh | Thông báo chỉ gửi đến người liên quan, không gửi cho chính người thực hiện | Cao |
| KR-08 | Nhắc nhở lịch học tự động | Gửi email nhắc nhở trước sự kiện theo cấu hình của người dùng | Trung bình |

---

# 5. Yêu cầu chức năng (Functional Requirements)

## 5.1. Module Xác thực & Phân quyền

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-01 | Đăng ký tài khoản | Tất cả | Người dùng điền họ tên, username, email, mật khẩu, vai trò, mã SV, khoa. Tài khoản tạo ở trạng thái chờ duyệt (`is_approved = False`). Admin nhận thông báo. |
| FR-02 | Đăng nhập JWT | Đã duyệt | Xác thực username/password, kiểm tra `is_active` và `is_approved`, phát hành JWT (24h). Ghi nhận `last_login`. |
| FR-03 | Duyệt & Quản lý tài khoản | Admin | Duyệt (`is_approved = True`), từ chối, khóa (`is_active = False`), thay đổi vai trò, xóa tài khoản. Gửi email thông báo kết quả. |

## 5.2. Module Quản lý Nhiệm vụ

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-04 | Tạo & Giao nhiệm vụ | Admin, Teacher | Điền tiêu đề, mô tả, ưu tiên (low/medium/high/urgent), hạn nộp, môn học, mã môn, nhóm lớp, học kỳ, năm học. Admin giao trực tiếp; Teacher giao qua phê duyệt. Thông báo in-app + email cho người được giao. |
| FR-05 | Theo dõi & Cập nhật tiến độ | Tất cả | Student cập nhật trạng thái cá nhân (todo/in_progress/done), progress, ghi chú. Admin/Teacher cập nhật trạng thái toàn cục. Mọi thay đổi ghi vào TaskHistory và phát sóng qua WebSocket. |
| FR-06 | Kanban Board thời gian thực | Tất cả | Board 3 cột (To Do, In Progress, Done). Admin/Teacher kéo-thả. Cập nhật tức thì qua Socket.IO cho tất cả client. |
| FR-07 | Luồng yêu cầu nhiệm vụ | Teacher, Student | Các loại: `assign` (giao thêm), `delete` (xóa), `withdraw` (rút), `remove` (xóa thành viên). Admin phê duyệt/từ chối. Thông báo kết quả cho người yêu cầu. |
| FR-08 | Lịch sử hoạt động | Admin, Teacher | Ghi nhận tự động: người thực hiện, hành động, chi tiết, thời gian. Hiển thị Timeline giảm dần. |
| FR-09 | Kiểm soát quyền truy cập | Hệ thống | Chỉ người tạo, người được giao (trong TaskAssignment) và Admin mới được xem nhiệm vụ. Thành viên bị xóa không còn nhìn thấy nhiệm vụ. |
| FR-10 | Quản lý Subtask | Admin, Teacher | Tạo, cập nhật, xóa công việc con trong nhiệm vụ. Ghi lịch sử và phát sóng WebSocket. |
| FR-11 | Bình luận nhiệm vụ | Tất cả | Bình luận phân cấp (có reply). Thông báo cho tất cả người liên quan (trừ người bình luận). |
| FR-12 | Đính kèm tệp | Admin, Teacher | Đính kèm và xóa tệp trong nhiệm vụ. Ghi lịch sử. |

## 5.3. Module Lịch học & Sự kiện

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-13 | Quản lý lịch học | Admin, Teacher | Tạo sự kiện (class/exam/meeting/event) với môn học, nhóm lớp, địa điểm, thời gian, màu sắc. Hỗ trợ sự kiện lặp lại (weekly, biweekly). |
| FR-14 | Nhắc nhở tự động | Tất cả | Thiết lập nhắc nhở trước sự kiện (tính bằng phút). Tiến trình nền gửi email tự động. Hỗ trợ snooze. |

## 5.4. Module Kho Tài liệu

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-15 | Tải lên tài liệu | Admin, Teacher | Chọn tệp, điền tiêu đề, mô tả, danh mục (lecture/assignment/reference/general), môn học, nhóm lớp. Lưu tệp vào `uploads/`. |
| FR-16 | Tải xuống tài liệu | Tất cả | Tìm kiếm/lọc tài liệu, tải xuống. Hệ thống tăng `download_count`. |

## 5.5. Module Hỏi & Đáp (QnA)

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-17 | Đặt câu hỏi | Student | Tạo câu hỏi với tiêu đề, nội dung, gắn môn học. Trạng thái mặc định `is_resolved = False`. |
| FR-18 | Trả lời & Trả lời phân cấp | Tất cả | Đăng câu trả lời, hỗ trợ reply to answer. Cập nhật thời gian thực qua Socket.IO. |
| FR-19 | Chấp nhận câu trả lời | Người hỏi, Teacher, Admin | Đánh dấu `is_accepted = True`. Câu hỏi tự động chuyển `is_resolved = True`. |
| FR-20 | Kiểm duyệt nội dung QnA | Admin | Trang quản trị riêng `/admin/qna` với: phân trang, tìm kiếm, xem tất cả câu trả lời, ẩn/hiện câu trả lời, xóa mềm nội dung không phù hợp. |

## 5.6. Module Trò chuyện

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-21 | Chat 1-1 thời gian thực | Tất cả | Nhắn tin riêng tư qua Socket.IO. Phòng chat theo cặp user ID. Trạng thái đã đọc (`is_read`). |

## 5.7. Module Thông báo

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-22 | Thông báo đa kênh | Tất cả | In-app + Email. Sự kiện kích hoạt: giao nhiệm vụ, xử lý yêu cầu, trả lời QnA, sự kiện sắp diễn ra, duyệt tài khoản. Chỉ gửi cho người liên quan, không gửi cho người thực hiện hành động. |

## 5.8. Module Quản lý Năm học

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-23 | CRUD Năm học | Admin | Tạo năm học (tên, năm bắt đầu/kết thúc, trạng thái active). Dùng làm dữ liệu tham chiếu cho nhiệm vụ và lịch. |
| FR-24 | Bảo vệ xóa năm học | Hệ thống | Không cho phép xóa năm học đang được tham chiếu bởi nhiệm vụ. Trả về thông báo lỗi rõ ràng. |

## 5.9. Module Cài đặt Cá nhân

| Mã | Tính năng | Vai trò | Mô tả |
|----|-----------|---------|-------|
| FR-25 | Chỉnh sửa hồ sơ | Tất cả | Cập nhật họ tên, email, phone, avatar, tùy chỉnh thời gian nhắc nhở. |

---

# 6. Yêu cầu phi chức năng (Non-Functional Requirements)

## 6.1. Hiệu suất (Performance)

| Mã | Danh mục | Yêu cầu | Ngưỡng |
|----|----------|---------|--------|
| NFR-P01 | Phản hồi API | Thời gian phản hồi REST API thông thường | ≤ 500ms (< 100 users đồng thời) |
| NFR-P02 | WebSocket | Độ trễ sự kiện real-time | ≤ 200ms (mạng nội bộ) |
| NFR-P03 | Tải trang | Time to Interactive (TTI) | ≤ 3 giây (10 Mbps) |
| NFR-P04 | Upload tệp | Hỗ trợ tệp tối đa | 50MB; upload ≤ 10s (10 Mbps) |
| NFR-P05 | Chịu tải | WebSocket sessions đồng thời | Tối thiểu 200 (có Redis scale) |

## 6.2. Bảo mật (Security)

| Mã | Danh mục | Yêu cầu | Cơ chế |
|----|----------|---------|--------|
| NFR-S01 | Xác thực | Tất cả API (trừ login/register) yêu cầu JWT hợp lệ | Flask-JWT-Extended |
| NFR-S02 | Mật khẩu | Không lưu plaintext | Werkzeug PBKDF2-HMAC-SHA256 |
| NFR-S03 | CSP | HTTP Security Headers chống XSS, Clickjacking | Flask-Talisman |
| NFR-S04 | Sanitization | Làm sạch HTML đầu vào (QnA, Chat) | Bleach |
| NFR-S05 | Rate Limiting | Giới hạn tần suất API nhạy cảm | Flask-Limiter |
| NFR-S06 | WebSocket CORS | Chỉ cho phép origins được khai báo | Flask-SocketIO CORS |
| NFR-S07 | Path Traversal | Làm sạch tên tệp upload | Werkzeug `secure_filename` |

## 6.3. Tính sẵn sàng (Availability)

| Mã | Danh mục | Yêu cầu | Ngưỡng |
|----|----------|---------|--------|
| NFR-A01 | Uptime | Thời gian hoạt động production | ≥ 99% (< 7.3h downtime/năm) |
| NFR-A02 | Auto-restart | Container lỗi tự khởi động lại | Docker `restart: always` |
| NFR-A03 | Background tasks | Nhắc nhở email chạy song song, không ảnh hưởng HTTP | Thread riêng, kiểm tra mỗi 60s |

## 6.4. Khả năng mở rộng (Scalability)

| Mã | Danh mục | Yêu cầu | Cơ chế |
|----|----------|---------|--------|
| NFR-SC01 | Scale ngang WebSocket | Đồng bộ trạng thái giữa nhiều instance | Redis message queue |
| NFR-SC02 | Reverse Proxy | SSL termination, routing, load balancing | Nginx |
| NFR-SC03 | Containerization | Toàn bộ service đóng gói Docker | Docker Compose |
| NFR-SC04 | Giám sát | Metrics thời gian thực (request rate, latency, error) | Prometheus + Grafana |

---

# 7. Giả định (Assumptions)

| STT | Giả định | Lý do |
|-----|----------|-------|
| A-01 | Mỗi người dùng chỉ thuộc một vai trò cố định (Admin/Teacher/Student). Thay đổi vai trò do Admin thực hiện. | Mô hình RBAC đơn role. |
| A-02 | Sinh viên không thể tự tạo nhiệm vụ. Tất cả nhiệm vụ được khởi tạo bởi Admin hoặc Teacher. | Đảm bảo kiểm soát trong môi trường giảng dạy. |
| A-03 | Mọi người dùng có kết nối Internet ổn định để sử dụng WebSocket. | Chế độ ngoại tuyến không được hỗ trợ. |
| A-04 | Admin thiết lập năm học trước khi Giảng viên tạo nhiệm vụ/lịch học. | Các thực thể có trường tham chiếu `academic_year`. |
| A-05 | Hệ thống triển khai chính trên mạng nội bộ (Intranet). Truy cập Internet qua VPN. | Phù hợp với mô hình bảo mật đã áp dụng. |
| A-06 | Dịch vụ SMTP bên ngoài luôn sẵn sàng cho gửi email. | Nếu SMTP lỗi, thông báo in-app vẫn hoạt động. |

---

# 8. Ràng buộc (Constraints)

| STT | Ràng buộc | Mô tả |
|-----|-----------|-------|
| C-01 | Cơ sở dữ liệu | SQLite (dev), nâng cấp PostgreSQL/MySQL (production). Sử dụng SQLAlchemy ORM. |
| C-02 | Môi trường | Docker container trên Linux. |
| C-03 | Trình duyệt | Chrome ≥ 90, Firefox ≥ 88, Edge ≥ 90. Không hỗ trợ IE. |
| C-04 | Kích thước tệp | Tối đa 50MB/tệp (cấu hình Nginx + Flask). Định dạng cho phép: pdf, doc, docx, xls, xlsx, ppt, pptx, txt, zip, rar, png, jpg, jpeg. |
| C-05 | Phụ thuộc SMTP | Gửi email phụ thuộc SMTP bên ngoài. Lỗi SMTP không ảnh hưởng thông báo in-app. |
| C-06 | Ngôn ngữ | Giao diện và tài liệu chỉ hỗ trợ Tiếng Việt. |
| C-07 | Stack công nghệ | Python 3.10+, Flask 2.3, SQLAlchemy 2.0, Socket.IO, Redis, Nginx, Prometheus, Grafana. |

---

# 9. Lịch sử thay đổi tài liệu (Change Log)

| Phiên bản | Ngày | Thay đổi chính |
|-----------|------|----------------|
| 1.0 | 25/03/2026 | Phiên bản đầu tiên – mô tả toàn bộ yêu cầu cơ bản |
| 2.0 | 29/03/2026 | Bổ sung: FR-09 (Kiểm soát quyền truy cập nhiệm vụ), FR-20 (Kiểm duyệt QnA bởi Admin), FR-24 (Bảo vệ xóa năm học), cập nhật FR-22 (Thông báo theo ngữ cảnh – chỉ gửi cho người liên quan). Bổ sung BG-06, BG-07, KR-04 đến KR-08. Tái cấu trúc tài liệu theo chuẩn BRD mới. |

---

# 10. Thuật ngữ (Glossary)

| Thuật ngữ | Giải thích |
|-----------|-----------|
| **BRD** | Business Requirements Document – Tài liệu Yêu cầu Nghiệp vụ |
| **API** | Application Programming Interface – Giao diện lập trình ứng dụng |
| **REST API** | Kiến trúc API sử dụng HTTP methods (GET, POST, PUT, DELETE) |
| **JWT** | JSON Web Token – Token xác thực và truyền thông tin an toàn |
| **WebSocket** | Giao thức truyền thông song công cho giao tiếp hai chiều liên tục |
| **Socket.IO** | Thư viện xây dựng trên WebSocket, hỗ trợ fallback và rooms |
| **RBAC** | Role-Based Access Control – Kiểm soát truy cập dựa trên vai trò |
| **Redis** | Cơ sở dữ liệu in-memory, dùng làm message queue cho Socket.IO |
| **Docker** | Nền tảng container hóa ứng dụng |
| **Nginx** | Web server và reverse proxy hiệu suất cao |
| **Prometheus** | Hệ thống thu thập metrics dạng time-series |
| **Grafana** | Nền tảng trực quan hóa metrics |
| **ORM** | Object-Relational Mapping – Ánh xạ đối tượng sang CSDL (SQLAlchemy) |
| **CSP** | Content Security Policy – Chính sách bảo mật nội dung |
| **XSS** | Cross-Site Scripting – Lỗ hổng chèn mã độc vào trang web |
| **SMTP** | Simple Mail Transfer Protocol – Giao thức gửi email |
| **KPI** | Key Performance Indicator – Chỉ số hiệu suất cốt yếu |
| **TTI** | Time to Interactive – Thời gian để trang có thể tương tác |
| **Subtask** | Công việc con trong một nhiệm vụ tổng |
| **Kanban Board** | Bảng quản lý trực quan theo cột trạng thái |
| **Audit Trail** | Nhật ký kiểm toán – ghi lại mọi thay đổi để truy xuất |
| **Soft Delete** | Xóa mềm – đánh dấu ẩn thay vì xóa vĩnh viễn khỏi CSDL |

---

*Tài liệu này được soạn thảo bởi Business Analysis Team dựa trên phân tích codebase hiện tại của dự án EduTask Manager. Mọi thắc mắc hoặc đề xuất thay đổi vui lòng liên hệ trực tiếp với nhóm phát triển.*

*Phiên bản: 2.0 | Ngày: 29/03/2026 | Trạng thái: Bản Chính thức*
