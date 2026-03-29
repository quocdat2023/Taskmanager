# BUSINESS REQUIREMENTS DOCUMENT (BRD)

**EduTask Manager – Hệ thống Quản lý Học vụ và Nhiệm vụ Trực tuyến**

**Phiên bản:** 1.0  
**Ngày phát hành:** 29/03/2026  
**Người soạn thảo:** Senior Business Analyst  
**Trạng thái:** Bản chính thức  

---

## MỤC LỤC

1. [Tóm tắt điều hành (Executive Summary)](#1-tóm-tắt-điều-hành-executive-summary)
2. [Mục tiêu kinh doanh (Business Objectives)](#2-mục-tiêu-kinh-doanh-business-objectives)
3. [Phạm vi dự án (Project Scope)](#3-phạm-vi-dự-án-project-scope)
4. [Phân tích Stakeholder](#4-phân-tích-stakeholder)
5. [Chân dung người dùng (User Personas)](#5-chân-dung-người-dùng-user-personas)
6. [Quy trình hiện tại (AS-IS)](#6-quy-trình-hiện-tại-as-is)
7. [Giải pháp đề xuất (TO-BE)](#7-giải-pháp-đề-xuất-to-be)
8. [Yêu cầu chức năng (Functional Requirements)](#8-yêu-cầu-chức-năng-functional-requirements)
9. [Yêu cầu phi chức năng (Non-Functional Requirements)](#9-yêu-cầu-phi-chức-năng-non-functional-requirements)
10. [Business Rules](#10-business-rules)
11. [Yêu cầu dữ liệu](#11-yêu-cầu-dữ-liệu)
12. [Giả định và ràng buộc](#12-giả-định-và-ràng-buộc)
13. [Rủi ro và phương án giảm thiểu](#13-rủi-ro-và-phương-án-giảm-thiểu)
14. [Chỉ số đánh giá thành công (KPIs)](#14-chỉ-số-đánh-giá-thành-công-kpis)
15. [Thuật ngữ (Glossary)](#15-thuật-ngữ-glossary)

---

## 1. Tóm tắt điều hành (Executive Summary)

### 1.1. Mục đích tài liệu
Tài liệu Business Requirements Document (BRD) này mô tả chi tiết các yêu cầu nghiệp vụ cho dự án **EduTask Manager**, một nền tảng web quản lý học vụ và nhiệm vụ trực tuyến dành cho môi trường giáo dục đại học. Tài liệu phục vụ làm nguồn tham chiếu duy nhất cho nhóm phát triển, kiểm thử và các bên liên quan, đảm bảo hệ thống được triển khai đúng theo mục tiêu kinh doanh.

### 1.2. Tóm tắt dự án
EduTask Manager là hệ thống số hóa quy trình quản lý nhiệm vụ học tập, lịch học, tài liệu và giao tiếp giữa giảng viên và sinh viên. Hệ thống tích hợp REST API với giao tiếp thời gian thực qua WebSocket, hỗ trợ Kanban board, diễn đàn QnA và kho tài liệu tập trung. Dự án nhằm giải quyết vấn đề phân tán thông tin trong công tác giảng dạy, tăng hiệu quả vận hành học vụ.

### 1.3. Bối cảnh và vấn đề nghiệp vụ
Trong môi trường đại học, quản lý nhiệm vụ và lịch học thường gặp khó khăn do thiếu công cụ tập trung, dẫn đến bỏ sót thông tin, chậm trễ phản hồi và kém minh bạch. EduTask Manager ra đời để thống nhất các quy trình này trên một nền tảng duy nhất, nâng cao trải nghiệm học tập và giảng dạy.

### 1.4. Mục tiêu kinh doanh chính
- Tập trung hóa quản lý nhiệm vụ và lịch học.
- Tăng tỷ lệ hoàn thành nhiệm vụ đúng hạn.
- Rút ngắn thời gian phản hồi học thuật.
- Nâng cao tính minh bạch trong đánh giá.
- Hỗ trợ vận hành đa năm học và học kỳ.

---

## 2. Mục tiêu kinh doanh (Business Objectives)

| STT | Mục tiêu | Mô tả | Chỉ số đo lường |
|-----|----------|-------|-----------------|
| BG-01 | Tập trung hóa quản lý nhiệm vụ | 100% nhiệm vụ được tạo và theo dõi trên hệ thống | Tỷ lệ nhiệm vụ quản lý trên hệ thống |
| BG-02 | Tăng tỷ lệ hoàn thành đúng hạn | Tăng ≥ 20% so với phương pháp thủ công | Tỷ lệ nhiệm vụ hoàn thành đúng hạn |
| BG-03 | Rút ngắn thời gian phản hồi | Thời gian trả lời trung bình < 24 giờ | Thời gian phản hồi trung bình |
| BG-04 | Nâng cao minh bạch | 100% lịch sử thay đổi được ghi lại | Tỷ lệ nhiệm vụ có lịch sử đầy đủ |
| BG-05 | Hỗ trợ đa chu kỳ học vụ | Quản lý dữ liệu theo năm học và học kỳ | Số năm học/học kỳ được hỗ trợ |

---

## 3. Phạm vi dự án (Project Scope)

### 3.1. Trong phạm vi (In-Scope)
- Module xác thực và phân quyền (JWT, RBAC).
- Quản lý nhiệm vụ với Kanban board thời gian thực.
- Quản lý lịch học và sự kiện.
- Kho tài liệu học thuật.
- Diễn đàn hỏi đáp (QnA) với tóm tắt tự động.
- Trò chuyện trực tiếp (Real-time Chat).
- Hệ thống thông báo đa kênh.
- Quản lý người dùng và năm học.
- Hạ tầng Docker, Nginx, Prometheus, Grafana.

### 3.2. Ngoài phạm vi (Out-of-Scope)
- Tích hợp với LMS bên ngoài (Moodle, Canvas).
- Chức năng thi trực tuyến và chấm bài tự động.
- Ứng dụng di động native.
- Thanh toán học phí.
- Báo cáo BI phức tạp.
- Hỗ trợ đa ngôn ngữ.
- SSO với hệ thống trường.

---

## 4. Phân tích Stakeholder

| Stakeholder | Vai trò | Mức độ ảnh hưởng | Ghi chú |
|-------------|---------|------------------|---------|
| Ban Giám hiệu/Phòng Đào tạo | Phê duyệt và cung cấp yêu cầu cấp cao | Cao | Quyết định triển khai |
| Giảng viên | Người dùng chính, tạo và quản lý nhiệm vụ | Rất cao | Tổ chức hoạt động học thuật |
| Sinh viên | Người dùng chính, thực hiện nhiệm vụ | Rất cao | Tham gia học tập |
| Quản trị viên hệ thống | Vận hành và giám sát | Cao | Quản lý toàn bộ hệ thống |
| Nhóm phát triển kỹ thuật | Xây dựng và bảo trì | Cao | Triển khai hệ thống |
| Nhóm QA/QC | Kiểm thử chất lượng | Trung bình | Đảm bảo nghiệm thu |

---

## 5. Chân dung người dùng (User Personas)

### 5.1. Persona: Giảng viên Nguyễn Văn A (35 tuổi, Khoa CNTT)
- **Hồ sơ:** Giảng viên có 10 năm kinh nghiệm, phụ trách 3 môn học, quản lý 200 sinh viên.
- **Mục tiêu:** Quản lý nhiệm vụ hiệu quả, theo dõi tiến độ sinh viên, giao tiếp nhanh chóng.
- **Điểm đau:** Mất thời gian theo dõi email và nhóm chat, khó kiểm soát deadline.
- **Giải pháp mong đợi:** Nền tảng tập trung để tạo nhiệm vụ, xem báo cáo tiến độ, gửi thông báo tức thì.

### 5.2. Persona: Sinh viên Trần Thị B (20 tuổi, Sinh viên năm 3)
- **Hồ sơ:** Sinh viên chăm chỉ, tham gia nhiều nhóm dự án, cần quản lý deadline chặt chẽ.
- **Mục tiêu:** Nhận nhiệm vụ rõ ràng, cập nhật tiến độ dễ dàng, đặt câu hỏi và nhận phản hồi nhanh.
- **Điểm đau:** Bỏ sót nhiệm vụ do thông tin phân tán, chậm phản hồi từ giảng viên.
- **Giải pháp mong đợi:** Dashboard cá nhân hiển thị nhiệm vụ, công cụ QnA và chat trực tiếp.

### 5.3. Persona: Admin Lê Văn C (40 tuổi, IT Manager)
- **Hồ sơ:** Quản lý hệ thống IT của trường, phụ trách vận hành phần mềm.
- **Mục tiêu:** Đảm bảo hệ thống ổn định, quản lý người dùng, giám sát hiệu suất.
- **Điểm đau:** Khó khăn trong việc theo dõi lỗi và mở rộng hệ thống.
- **Giải pháp mong đợi:** Dashboard giám sát với metrics thời gian thực, công cụ quản lý người dùng tự động.

---

## 6. Quy trình hiện tại (AS-IS)

### 6.1. Quy trình quản lý nhiệm vụ
1. Giảng viên gửi nhiệm vụ qua email hoặc nhóm chat.
2. Sinh viên nhận thông tin từ nhiều nguồn, dễ bỏ sót.
3. Sinh viên cập nhật tiến độ thủ công qua email hoặc gặp trực tiếp.
4. Giảng viên theo dõi bằng cách hỏi từng sinh viên, tốn thời gian.
5. Deadline thường bị trễ do thiếu nhắc nhở tự động.

### 6.2. Quy trình giao tiếp học thuật
1. Sinh viên đặt câu hỏi qua email hoặc gặp trực tiếp.
2. Giảng viên trả lời chậm do lịch trình bận rộn.
3. Thiếu kho lưu trữ câu hỏi và câu trả lời cho sinh viên khác tham khảo.
4. Giao tiếp nhóm diễn ra trên nhiều nền tảng, thiếu tập trung.

### 6.3. Quy trình quản lý lịch học
1. Lịch học được thông báo qua bảng tin hoặc email.
2. Sinh viên ghi nhớ thủ công, dễ quên sự kiện.
3. Thiếu tích hợp nhắc nhở tự động.

---

## 7. Giải pháp đề xuất (TO-BE)

### 7.1. Quy trình quản lý nhiệm vụ số hóa
1. Giảng viên tạo nhiệm vụ trên hệ thống với deadline và phân công rõ ràng.
2. Sinh viên nhận thông báo tức thì và cập nhật tiến độ qua Kanban board.
3. Hệ thống tự động nhắc nhở deadline và gửi báo cáo tiến độ.
4. Giảng viên theo dõi thời gian thực qua dashboard.

### 7.2. Quy trình giao tiếp tập trung
1. Sinh viên đặt câu hỏi trên diễn đàn QnA, gắn với môn học.
2. Giảng viên và sinh viên trả lời, đánh dấu câu trả lời tốt nhất.
3. Chat trực tiếp cho trao đổi riêng tư.
4. Tất cả tương tác được lưu trữ và tìm kiếm dễ dàng.

### 7.3. Quy trình quản lý lịch học tự động
1. Giảng viên tạo lịch sự kiện trên hệ thống.
2. Sinh viên xem lịch tích hợp trên dashboard.
3. Hệ thống gửi nhắc nhở email trước sự kiện.

---

## 8. Yêu cầu chức năng (Functional Requirements)

| ID | Tên | Mô tả | Priority | Ghi chú |
|----|-----|-------|----------|---------|
| FR-01 | Đăng ký và xác thực tài khoản | Hệ thống phải cho phép người dùng đăng ký và đăng nhập với JWT. | High | Bao gồm duyệt tài khoản bởi Admin |
| FR-02 | Quản lý nhiệm vụ | Hệ thống phải hỗ trợ tạo, giao, theo dõi nhiệm vụ với Kanban board. | High | Thời gian thực qua WebSocket |
| FR-03 | Quản lý lịch học | Hệ thống phải cho phép tạo và quản lý lịch sự kiện với nhắc nhở. | Medium | Hỗ trợ sự kiện lặp lại |
| FR-04 | Kho tài liệu | Hệ thống phải cung cấp upload và download tài liệu học thuật. | Medium | Phân loại theo môn học |
| FR-05 | Diễn đàn QnA | Hệ thống phải hỗ trợ hỏi đáp với trả lời phân cấp và tóm tắt. | High | Thời gian thực |
| FR-06 | Chat trực tiếp | Hệ thống phải cung cấp nhắn tin 1-1 qua WebSocket. | Medium | Riêng tư |
| FR-07 | Thông báo đa kênh | Hệ thống phải gửi thông báo in-app và email tự động. | High | Cho các sự kiện quan trọng |
| FR-08 | Quản lý người dùng | Hệ thống phải cho phép Admin quản lý tài khoản và vai trò. | High | RBAC |
| FR-09 | Quản lý năm học | Hệ thống phải hỗ trợ cấu trúc năm học và học kỳ. | Low | Tham chiếu cho nhiệm vụ |

---

## 9. Yêu cầu phi chức năng (Non-Functional Requirements)

| ID | Loại | Mô tả | Chỉ số đo lường |
|----|------|-------|-----------------|
| NFR-01 | Hiệu suất | Thời gian phản hồi API ≤ 500ms | Trung bình dưới tải bình thường |
| NFR-02 | Bảo mật | Sử dụng JWT và RBAC cho xác thực | 100% endpoint bảo vệ |
| NFR-03 | Tính sẵn sàng | Uptime ≥ 99% | < 7.3 giờ downtime/năm |
| NFR-04 | Khả năng mở rộng | Hỗ trợ 200 sessions WebSocket đồng thời | Với Redis queue |
| NFR-05 | Tương thích | Hỗ trợ trình duyệt hiện đại | Chrome, Firefox, Edge |

---

## 10. Business Rules

- **BR-01:** Chỉ Admin và Teacher được tạo nhiệm vụ.
- **BR-02:** Sinh viên chỉ cập nhật trạng thái nhiệm vụ của mình.
- **BR-03:** Tài khoản mới cần duyệt bởi Admin trước khi hoạt động.
- **BR-04:** Nhiệm vụ phải gắn với năm học và học kỳ.
- **BR-05:** Chat chỉ giữa hai người dùng đã xác thực.

---

## 11. Yêu cầu dữ liệu

### 11.1. Cơ sở dữ liệu chính
- **Người dùng:** ID, tên, email, vai trò, trạng thái.
- **Nhiệm vụ:** ID, tiêu đề, mô tả, deadline, người tạo, người giao.
- **Lịch học:** ID, tiêu đề, thời gian, môn học.
- **Tài liệu:** ID, tên file, đường dẫn, danh mục.
- **QnA:** ID, câu hỏi, câu trả lời, trạng thái.
- **Chat:** ID, người gửi, người nhận, nội dung.

### 11.2. Yêu cầu lưu trữ
- Hỗ trợ SQLite (dev) và PostgreSQL (prod).
- Sao lưu tự động hàng ngày.

---

## 12. Giả định và ràng buộc

### 12.1. Giả định
- Người dùng có kết nối Internet ổn định.
- Admin thiết lập năm học trước khi sử dụng.
- Mỗi người dùng một vai trò cố định.

### 12.2. Ràng buộc
- Chạy trên Docker container Linux.
- Hỗ trợ trình duyệt hiện đại.
- Tệp upload tối đa 50MB.
- Phụ thuộc SMTP cho email.

---

## 13. Rủi ro và phương án giảm thiểu

| Rủi ro | Mức độ | Phương án giảm thiểu |
|--------|---------|---------------------|
| Mất dữ liệu | Cao | Sao lưu tự động, khôi phục từ backup |
| Tấn công bảo mật | Cao | Áp dụng CSP, rate limiting, làm sạch input |
| Hệ thống chậm | Trung bình | Giám sát với Prometheus, tối ưu query |
| Người dùng không chấp nhận | Trung bình | Đào tạo và hỗ trợ người dùng |

---

## 14. Chỉ số đánh giá thành công (KPIs)

- Tỷ lệ nhiệm vụ hoàn thành đúng hạn: ≥ 80%
- Thời gian phản hồi QnA: < 24 giờ
- Uptime hệ thống: ≥ 99%
- Số người dùng hoạt động: Tăng 50% sau 6 tháng
- Điểm hài lòng người dùng: ≥ 4/5

---

## 15. Thuật ngữ (Glossary)

| Thuật ngữ | Giải thích |
|-----------|------------|
| BRD | Business Requirements Document |
| JWT | JSON Web Token |
| RBAC | Role-Based Access Control |
| WebSocket | Giao thức giao tiếp thời gian thực |
| Kanban | Phương pháp quản lý nhiệm vụ trực quan |
| KPI | Key Performance Indicator |
| API | Application Programming Interface |
| Docker | Nền tảng containerization |
| Nginx | Web server và reverse proxy |
| Prometheus | Hệ thống giám sát metrics |

---

*Tài liệu này được tạo dựa trên phân tích dự án EduTask Manager. Mọi cập nhật vui lòng liên hệ nhóm Business Analysis.*