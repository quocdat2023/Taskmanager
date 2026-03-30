# TÀI LIỆU YÊU CẦU NGHIỆP VỤ

# BUSINESS REQUIREMENTS DOCUMENT (BRD)

---

**Tên dự án:** EduTask Manager – Hệ thống Quản lý Học vụ và Nhiệm vụ Trực tuyến

**Phiên bản tài liệu:** 1.0

**Ngày soạn thảo:** 25/03/2026

**Trạng thái:** Bản chính thức

**Người soạn thảo:** Business Analysis Team

---

## MỤC LỤC

1. Tổng quan dự án (Executive Summary)
2. Phạm vi dự án (Project Scope)
3. Các bên liên quan & Vai trò người dùng (Stakeholders & User Roles)
4. Yêu cầu chức năng (Functional Requirements)
5. Yêu cầu phi chức năng (Non-Functional Requirements)
6. Ràng buộc & Giả định (Constraints & Assumptions)
7. Thuật ngữ (Glossary)

---

# 1. Tổng quan dự án (Executive Summary)

## 1.1. Mục đích tài liệu

Tài liệu Business Requirements Document (BRD) này được lập ra nhằm mô tả một cách toàn diện, chính xác và có cấu trúc các yêu cầu nghiệp vụ của dự án **EduTask Manager**. Tài liệu đóng vai trò là nguồn tham chiếu duy nhất (*single source of truth*) cho tất cả các bên liên quan, bao gồm nhóm phát triển kỹ thuật, nhóm kiểm thử chất lượng (QA/QC), ban quản lý dự án và các đối tác triển khai.

Tài liệu BRD này được xây dựng theo phương pháp "dịch ngược" (*reverse engineering*): xuất phát từ codebase hoàn chỉnh để hệ thống hóa lại các yêu cầu nghiệp vụ ở cấp độ đặc tả, nhằm phục vụ mục đích tài liệu hóa, bàn giao và duy trì hệ thống dài hạn.

## 1.2. Tóm tắt dự án

**EduTask Manager** là một nền tảng web quản lý học vụ và nhiệm vụ trực tuyến, được thiết kế đặc thù cho môi trường giáo dục đại học. Hệ thống giải quyết bài toán phân tán thông tin trong công tác giảng dạy và học tập bằng cách tích hợp trên một nền tảng duy nhất các chức năng: quản lý nhiệm vụ học tập theo nhóm lớp, lịch học và sự kiện, kho tài liệu học thuật, diễn đàn hỏi đáp và giao tiếp trực tiếp giữa Giảng viên và Sinh viên.

Hệ thống được xây dựng trên kiến trúc REST API kết hợp giao tiếp thời gian thực (Real-time) thông qua WebSocket (Socket.IO), đảm bảo mọi cập nhật về trạng thái nhiệm vụ, thông báo và tin nhắn được phản ánh tức thì đến tất cả người dùng có liên quan mà không cần làm mới trang.

## 1.3. Bối cảnh và vấn đề nghiệp vụ

Trong môi trường đại học, sự phối hợp giữa Giảng viên và Sinh viên thường gặp các vấn đề cốt lõi sau:

- **Quản lý nhiệm vụ rời rạc:** Các bài tập, đề án và deadline được thông báo qua nhiều kênh khác nhau (email, nhóm chat, bảng tin), dẫn đến tình trạng bỏ sót hoặc nhầm lẫn thông tin.
- **Thiếu công cụ theo dõi tiến độ:** Giảng viên không có cơ chế trực quan để theo dõi tiến độ hoàn thành bài tập của từng sinh viên hoặc nhóm lớp theo thời gian thực.
- **Lịch học phân tán:** Thời khóa biểu, lịch thi và lịch họp thường được quản lý trên nhiều hệ thống riêng lẻ, thiếu tính đồng bộ.
- **Giao tiếp học thuật kém hiệu quả:** Sinh viên gặp khó khăn trong việc đặt câu hỏi và nhận phản hồi từ giảng viên một cách có tổ chức và lưu trữ được.

**EduTask Manager** ra đời nhằm thống nhất toàn bộ các quy trình trên vào một nền tảng số hóa duy nhất, tăng hiệu quả vận hành học vụ lên mức tối ưu.

## 1.4. Mục tiêu kinh doanh (Business Goals)

| STT | Mục tiêu | Chỉ số đo lường thành công (KPI) |
|-----|----------|----------------------------------|
| BG-01 | Tập trung hóa quản lý nhiệm vụ học tập | 100% nhiệm vụ được tạo, giao và theo dõi trên hệ thống |
| BG-02 | Tăng tỷ lệ hoàn thành bài tập đúng hạn | Tăng ≥ 20% so với phương pháp thủ công |
| BG-03 | Rút ngắn thời gian phản hồi học thuật | Thời gian trả lời câu hỏi trung bình < 24 giờ |
| BG-04 | Nâng cao tính minh bạch trong đánh giá | 100% lịch sử thay đổi nhiệm vụ được ghi lại |
| BG-05 | Hỗ trợ vận hành đa năm học, đa học kỳ | Hệ thống quản lý dữ liệu theo năm học và học kỳ |

---

# 2. Phạm vi dự án (Project Scope)

## 2.1. Trong phạm vi (In-Scope)

Các chức năng và module sau đây nằm trong phạm vi phát triển của dự án EduTask Manager phiên bản 1.0:

- **Module Xác thực & Phân quyền:** Đăng ký tài khoản, đăng nhập bảo mật bằng JWT, quản lý phiên làm việc, phân quyền theo vai trò (Role-Based Access Control – RBAC).
- **Module Quản lý Nhiệm vụ:** Tạo, giao, theo dõi, cập nhật và xóa nhiệm vụ học tập; hỗ trợ phân cấp với subtask; luồng duyệt yêu cầu qua Admin; Kanban board thời gian thực.
- **Module Lịch học & Sự kiện:** Quản lý lịch học, lịch thi, cuộc họp; hỗ trợ sự kiện lặp lại (recurring); tích hợp nhắc nhở qua email tự động.
- **Module Kho Tài liệu:** Tải lên, phân loại và tải xuống tài liệu học thuật (giáo án, bài tập, tài liệu tham khảo).
- **Module Hỏi & Đáp (QnA):** Diễn đàn hỏi đáp theo môn học; hỗ trợ trả lời phân cấp (threaded replies); tính năng đánh dấu câu trả lời được chấp nhận; tóm tắt thảo luận tự động.
- **Module Trò chuyện (Real-time Chat):** Nhắn tin trực tiếp 1-1 giữa người dùng thông qua WebSocket.
- **Module Thông báo:** Hệ thống thông báo đa kênh (In-app push + Email) theo thời gian thực.
- **Module Quản lý Người dùng:** Admin duyệt tài khoản mới, quản lý danh sách người dùng, phân quyền.
- **Module Quản lý Năm học:** Admin thiết lập và quản lý chu kỳ năm học, học kỳ.
- **Module Cài đặt Cá nhân:** Người dùng chỉnh sửa hồ sơ, avatar, tùy chỉnh nhắc nhở.
- **Hạ tầng & Vận hành:** Containerization bằng Docker, reverse proxy Nginx, giám sát hệ thống bằng Prometheus & Grafana.

## 2.2. Ngoài phạm vi (Out-of-Scope)

Các hạng mục sau **không** thuộc phạm vi của phiên bản 1.0 này:

- Tích hợp với hệ thống quản lý đào tạo (LMS) bên ngoài như Moodle, Canvas.
- Chức năng thi trực tuyến, chấm bài tự động (Auto-grading).
- Ứng dụng di động (Mobile app – iOS/Android) native.
- Thanh toán học phí hoặc tích hợp cổng thanh toán.
- Báo cáo thống kê học thuật phức tạp (Business Intelligence).
- Hỗ trợ đa ngôn ngữ (i18n) ngoài Tiếng Việt.
- SSO (Single Sign-On) với hệ thống trường đại học.

---

# 3. Các bên liên quan & Vai trò người dùng (Stakeholders & User Roles)

## 3.1. Danh sách các bên liên quan

| STT | Bên liên quan | Mức độ quan tâm | Trách nhiệm |
|-----|---------------|-----------------|-------------|
| 1 | Ban Giám hiệu / Phòng Đào tạo | Cao | Phê duyệt triển khai, cung cấp yêu cầu nghiệp vụ cấp cao |
| 2 | Giảng viên | Rất cao | Người dùng chính; tạo và quản lý nhiệm vụ, tài liệu, lịch học |
| 3 | Sinh viên | Rất cao | Người dùng chính; thực hiện nhiệm vụ, tương tác học thuật |
| 4 | Quản trị viên hệ thống | Cao | Vận hành, giám sát và kiểm soát toàn bộ hệ thống |
| 5 | Nhóm phát triển kỹ thuật | Cao | Xây dựng, triển khai và bảo trì hệ thống |
| 6 | Nhóm QA/QC | Trung bình | Kiểm thử chất lượng, xác nhận nghiệm thu |

## 3.2. Phân tích Vai trò Người dùng (User Roles) và Quyền hạn

### 3.2.1. Quản trị viên (Admin)

Quản trị viên là vai trò có quyền hạn cao nhất trong hệ thống, chịu trách nhiệm quản lý cấu hình, người dùng và toàn bộ dữ liệu nền tảng.

| Nhóm chức năng | Quyền hạn |
|----------------|-----------|
| Quản lý người dùng | Xem, duyệt, khóa, mở khóa, xóa tài khoản; cấp/thu hồi vai trò |
| Quản lý nhiệm vụ | Tạo, sửa, xóa bất kỳ nhiệm vụ nào; xử lý các yêu cầu từ Giảng viên |
| Quản lý năm học | Tạo và quản lý các chu kỳ năm học, học kỳ |
| Giám sát hệ thống | Xem toàn bộ lịch sử hoạt động, tiếp cận dashboard Grafana/Prometheus |
| Thông báo | Gửi thông báo hệ thống đến toàn bộ người dùng |

### 3.2.2. Giảng viên (Teacher)

Giảng viên là người tổ chức và điều phối các hoạt động học thuật trên hệ thống.

| Nhóm chức năng | Quyền hạn |
|----------------|-----------|
| Nhiệm vụ | Tạo nhiệm vụ; giao nhiệm vụ cho sinh viên; theo dõi tiến độ; yêu cầu Admin xóa nhiệm vụ nếu cần |
| Lịch học | Tạo, sửa, xóa lịch học, lịch thi và sự kiện của lớp mình |
| Tài liệu | Tải lên, quản lý và xóa tài liệu học thuật của môn học |
| QnA | Trả lời câu hỏi, chấp nhận câu trả lời tốt nhất, tóm tắt thảo luận |
| Chat | Nhắn tin trực tiếp với sinh viên và đồng nghiệp |

### 3.2.3. Sinh viên (Student)

Sinh viên là đối tượng người dùng thực hiện các nhiệm vụ được giao và tương tác học thuật.

| Nhóm chức năng | Quyền hạn |
|----------------|-----------|
| Nhiệm vụ | Xem nhiệm vụ được giao; cập nhật trạng thái cá nhân; nộp báo cáo; yêu cầu giao hoặc rút khỏi nhiệm vụ |
| Lịch học | Xem lịch học của bản thân |
| Tài liệu | Xem và tải xuống tài liệu được chia sẻ |
| QnA | Đặt câu hỏi và trả lời câu hỏi của những sinh viên khác |
| Chat | Nhắn tin trực tiếp với Giảng viên và bạn học |
| Cài đặt | Chỉnh sửa hồ sơ cá nhân, tùy chỉnh nhắc nhở |

---

# 4. Yêu cầu chức năng (Functional Requirements)

| Mã Yêu cầu | Tên Tính năng | User Role | Mô tả Chi tiết & Luồng xử lý |
|------------|---------------|-----------|-------------------------------|
| **FR-01** | **Đăng ký tài khoản** | Tất cả (chưa có tài khoản) | **Mô tả:** Người dùng mới có thể tự đăng ký tài khoản trên hệ thống. **Luồng:** (1) Người dùng điền thông tin: họ tên, tên đăng nhập, email, mật khẩu, vai trò, mã sinh viên (nếu là SV), khoa. (2) Hệ thống kiểm tra tính duy nhất của username và email. (3) Tài khoản được tạo ở trạng thái `is_approved = False` (chờ duyệt). (4) Admin nhận thông báo có tài khoản mới cần duyệt. |
| **FR-02** | **Đăng nhập & Xác thực JWT** | Admin, Teacher, Student | **Mô tả:** Người dùng đã được duyệt có thể đăng nhập bằng username/password. **Luồng:** (1) Người dùng nhập thông tin đăng nhập. (2) Hệ thống xác thực mật khẩu (so với `password_hash`). (3) Kiểm tra `is_active` và `is_approved` của tài khoản. (4) Nếu hợp lệ, hệ thống phát hành JWT Access Token. (5) Token được lưu vào `localStorage` của trình duyệt để xác thực các yêu cầu API tiếp theo. (6) Thời gian `last_login` được ghi nhận. |
| **FR-03** | **Duyệt & Quản lý Tài khoản** | Admin | **Mô tả:** Admin có toàn quyền quản lý vòng đời tài khoản người dùng. **Luồng Duyệt:** (1) Admin vào trang quản lý người dùng. (2) Xem danh sách tài khoản đang chờ duyệt (`is_approved = False`). (3) Admin chọn Duyệt → `is_approved = True` hoặc Từ chối → xóa yêu cầu. (4) Người dùng nhận email thông báo kết quả. **Các hành động khác:** Khóa tài khoản (`is_active = False`), thay đổi vai trò, xóa tài khoản vĩnh viễn. |
| **FR-04** | **Tạo & Giao Nhiệm vụ** | Admin, Teacher | **Mô tả:** Người dùng có quyền quản lý có thể tạo nhiệm vụ học tập và giao cho sinh viên. **Luồng:** (1) Người tạo điền đầy đủ thông tin: tiêu đề, mô tả, mức độ ưu tiên (thấp/trung bình/cao/urgent), hạn nộp, tên môn học, mã môn, nhóm lớp, học kỳ, năm học, thời gian ước tính. (2) Tùy chọn đính kèm tệp và tạo danh sách công việc con (Subtasks). (3) Chọn sinh viên cần giao nhiệm vụ và lưu. (4) Hệ thống tạo bản ghi [TaskAssignment](file:///c:/Users/quocd/Documents/Task2/app/models/task.py#66-90) cho từng người được giao. (5) Sinh viên được giao nhận thông báo in-app và email. (6) Lịch sử tạo nhiệm vụ được ghi vào [TaskHistory](file:///c:/Users/quocd/Documents/Task2/app/models/task.py#157-179). |
| **FR-05** | **Theo dõi & Cập nhật Tiến độ Nhiệm vụ** | Admin, Teacher, Student | **Mô tả:** Người dùng có thể theo dõi và cập nhật trạng thái thực hiện nhiệm vụ. **Luồng (Student – cập nhật cá nhân):** (1) Sinh viên mở chi tiết nhiệm vụ. (2) Cập nhật trạng thái cá nhân (todo / in_progress / done), phần trăm hoàn thành (progress), thời gian thực tế. (3) Tùy chọn để lại ghi chú (note) khi nộp. (4) Hệ thống ghi nhận `submitted_at`. **Luồng (Admin/Teacher – cập nhật tổng thể):** Cập nhật trạng thái toàn cầu của nhiệm vụ và phần trăm hoàn thành tổng thể. Mọi thay đổi đều được ghi vào [TaskHistory](file:///c:/Users/quocd/Documents/Task2/app/models/task.py#157-179) và phát sóng qua WebSocket để cập nhật Kanban Board thời gian thực. |
| **FR-06** | **Quản lý Kanban Board Thời gian thực** | Admin, Teacher, Student | **Mô tả:** Hệ thống cung cấp giao diện Kanban Board dạng kéo-thả (drag-and-drop) để trực quan hóa trạng thái nhiệm vụ. **Luồng:** (1) Board hiển thị 3 cột: `To Do`, `In Progress`, `Done` theo trạng thái toàn cục của nhiệm vụ. (2) Chỉ Admin và Teacher được phép kéo thẻ nhiệm vụ giữa các cột. (3) Khi trạng thái được cập nhật, hệ thống phát sự kiện `task_status_updated` qua Socket.IO. (4) Tất cả client đang kết nối nhận sự kiện và cập nhật giao diện tự động, không cần tải lại trang. |
| **FR-07** | **Luồng Yêu cầu Nhiệm vụ (Task Request)** | Teacher, Student | **Mô tả:** Hệ thống cung cấp cơ chế gửi yêu cầu lên Admin để thực hiện các hành động nhạy cảm. **Các loại yêu cầu:** `assign` (yêu cầu giao thêm sinh viên), `delete` (yêu cầu xóa nhiệm vụ), `withdraw` (yêu cầu rút khỏi nhiệm vụ). **Luồng:** (1) Người dùng gửi yêu cầu kèm ghi chú lý do. (2) Yêu cầu được lưu vào `task_requests` với trạng thái `pending`. (3) Admin nhận thông báo, xem xét và phê duyệt (`approved`) hoặc từ chối (`rejected`). (4) Hệ thống thực thi hành động tương ứng và thông báo kết quả cho người yêu cầu. |
| **FR-08** | **Lịch sử Hoạt động Nhiệm vụ** | Admin, Teacher | **Mô tả:** Hệ thống tự động ghi lại toàn bộ lịch sử thay đổi của mỗi nhiệm vụ để phục vụ kiểm tra (audit) và truy xuất. **Nội dung ghi nhận:** Tên người thực hiện, hành động (tạo, cập nhật trạng thái, thêm người thực hiện...), chi tiết thay đổi, thời gian. **Hiển thị:** Giao diện Timeline theo thứ tự thời gian giảm dần trong chi tiết nhiệm vụ. |
| **FR-09** | **Quản lý Lịch học & Sự kiện** | Admin, Teacher | **Mô tả:** Người dùng có quyền quản lý có thể tạo và duy trì lịch học và sự kiện cho lớp học. **Luồng:** (1) Người tạo điền thông tin: tiêu đề, loại sự kiện (class/exam/meeting/event), môn học, nhóm lớp, địa điểm, thời gian bắt đầu/kết thúc, màu sắc hiển thị. (2) Tùy chọn thiết lập sự kiện lặp lại (hàng tuần, 2 tuần/lần). (3) Sinh viên liên quan có thể xem lịch trên giao diện Calendar. **Tính năng Nhắc nhở:** Người dùng có thể thiết lập thời gian nhắc trước sự kiện (tính bằng phút); hệ thống tự động gửi email nhắc nhở thông qua tiến trình nền tại thời điểm đã định. |
| **FR-10** | **Kho Tài liệu Học thuật** | Admin, Teacher (tải lên), Student (tải xuống) | **Mô tả:** Hệ thống cung cấp một kho lưu trữ tập trung cho tài liệu học thuật. **Luồng Tải lên (Upload):** (1) Teacher chọn tệp, điền tiêu đề, mô tả, danh mục (lecture/assignment/reference/general), môn học, nhóm lớp. (2) Hệ thống lưu tệp vào thư mục `uploads/` trên máy chủ và ghi nhận metadata vào cơ sở dữ liệu. **Luồng Tải xuống (Download):** (1) Sinh viên tìm kiếm/lọc tài liệu. (2) Nhấn nút Download → hệ thống tăng `download_count`, trả về tệp. |
| **FR-11** | **Diễn đàn Hỏi & Đáp (QnA)** | Admin, Teacher, Student | **Mô tả:** Hệ thống cung cấp nền tảng hỏi đáp học thuật có cấu trúc. **Luồng Đặt câu hỏi:** (1) Student tạo câu hỏi với tiêu đề, nội dung, gắn với môn học cụ thể. (2) Câu hỏi hiển thị trên danh sách công khai, mặc định ở trạng thái `is_resolved = False`. **Luồng Trả lời:** (1) Bất kỳ người dùng nào cũng có thể đăng câu trả lời. (2) Hỗ trợ trả lời phân cấp (reply to an answer). **Luồng Chốt câu hỏi:** (1) Người đặt câu hỏi hoặc Teacher/Admin đánh dấu một câu trả lời là `is_accepted = True`. (2) Câu hỏi tự động chuyển sang `is_resolved = True`. **Tính năng Realtime:** Khi có câu trả lời mới, hệ thống phát sự kiện qua Socket.IO để cập nhật giao diện cho tất cả người dùng đang xem câu hỏi đó. |
| **FR-12** | **Tóm tắt Thảo luận tự động (Discussion Summary)** | Admin, Teacher | **Mô tả:** Teacher hoặc Admin có thể kích hoạt tính năng tổng hợp và tóm tắt toàn bộ nội dung thảo luận của một câu hỏi. **Nội dung tóm tắt bao gồm:** Văn bản tóm tắt, số lượng bình luận, số người tham gia, khoảng thời gian diễn ra, các thẻ tag liên quan. Tóm tắt được lưu vào `discussion_summaries` và hiển thị lại cho người xem. |
| **FR-13** | **Trò chuyện Trực tiếp (Real-time Chat)** | Admin, Teacher, Student | **Mô tả:** Hệ thống cung cấp tính năng nhắn tin riêng tư 1-1 thời gian thực giữa các người dùng. **Luồng:** (1) Người dùng chọn đối tượng cần nhắn từ danh sách liên lạc. (2) Phòng chat (room) được mở dựa trên cặp ID người dùng, đảm bảo tính riêng tư. (3) Tin nhắn được gửi qua Socket.IO, lưu vào `chat_messages` và hiển thị tức thì cho cả hai phía. (4) Trạng thái đã đọc (`is_read`) được cập nhật khi người nhận mở cuộc trò chuyện. |
| **FR-14** | **Hệ thống Thông báo Đa kênh** | Admin, Teacher, Student | **Mô tả:** Hệ thống tự động tạo và phân phối thông báo đến người dùng qua hai kênh: In-app (trong ứng dụng) và Email. **Các sự kiện kích hoạt thông báo:** Giao nhiệm vụ mới, yêu cầu nhiệm vụ được xử lý, có câu trả lời mới trong câu hỏi, sự kiện/lịch học sắp diễn ra (qua tiến trình nền), tài khoản được duyệt. **Luồng:** Hệ thống backend tạo bản ghi [Notification](file:///c:/Users/quocd/Documents/Task2/app/models/notification.py#5-35), phát sự kiện qua Socket.IO và đồng thời gửi email qua Flask-Mail. Người dùng có thể xem danh sách thông báo (kèm phân trang) và đánh dấu đã đọc. |
| **FR-15** | **Quản lý Năm học & Học kỳ** | Admin | **Mô tả:** Admin có thể thiết lập và quản lý cấu trúc năm học cho toàn bộ hệ thống. **Luồng:** (1) Admin tạo năm học với tên, ngày bắt đầu, ngày kết thúc. (2) Thông tin năm học được sử dụng làm dữ liệu tham chiếu khi tạo nhiệm vụ, lịch học và tài liệu, đảm bảo khả năng lọc và báo cáo theo chu kỳ học vụ. |

---

# 5. Yêu cầu phi chức năng (Non-Functional Requirements)

## 5.1. Yêu cầu Hiệu suất (Performance)

| Mã Yêu cầu | Danh mục | Mô tả Yêu cầu | Ngưỡng chấp nhận |
|------------|----------|----------------|------------------|
| NFR-P01 | Thời gian phản hồi API | Thời gian phản hồi trung bình của các REST API thông thường (GET, POST đơn giản). | ≤ 500 ms ở điều kiện tải bình thường (< 100 users đồng thời) |
| NFR-P02 | Thời gian phản hồi WebSocket | Độ trễ tối đa từ thời điểm một sự kiện được phát đến khi client nhận được. | ≤ 200 ms trên mạng nội bộ |
| NFR-P03 | Tải trang đầu tiên | Thời gian để người dùng có thể tương tác với nội dung chính (TTI – Time to Interactive). | ≤ 3 giây trên kết nối 10 Mbps |
| NFR-P04 | Tải tệp | Tốc độ xử lý upload tệp tài liệu. | Hỗ trợ tệp tối đa 50 MB; thời gian upload ≤ 10 giây trên kết nối 10 Mbps |
| NFR-P05 | Khả năng chịu tải | Số lượng người dùng đồng thời tối thiểu hệ thống phải duy trì ổn định. | Tối thiểu 200 sessions WebSocket đồng thời (có hỗ trợ Redis message queue khi scale) |

## 5.2. Yêu cầu Bảo mật (Security)

| Mã Yêu cầu | Danh mục | Mô tả Yêu cầu | Tiêu chuẩn / Cơ chế |
|------------|----------|----------------|---------------------|
| NFR-S01 | Xác thực & Ủy quyền | Toàn bộ các API endpoint (trừ `/auth/login`, `/auth/register`) đều yêu cầu JWT hợp lệ. Phân quyền RBAC được thực thi ở tầng controller. | JWT (RS256 hoặc HS256), Flask-JWT-Extended |
| NFR-S02 | Bảo vệ mật khẩu | Mật khẩu người dùng không bao giờ được lưu dưới dạng plaintext. | Werkzeug `generate_password_hash` (PBKDF2-HMAC-SHA256) |
| NFR-S03 | Content Security Policy (CSP) | Hệ thống áp dụng HTTP Security Headers để chống XSS và Clickjacking. | Flask-Talisman với CSP được cấu hình tường minh |
| NFR-S04 | Làm sạch dữ liệu đầu vào | Nội dung do người dùng nhập (đặc biệt ở QnA và Chat) phải được làm sạch HTML để ngăn chặn tấn công XSS lưu trữ (Stored XSS). | Thư viện `bleach` v6.1.0 |
| NFR-S05 | Giới hạn tần suất yêu cầu (Rate Limiting) | Các endpoint xác thực và các API nhạy cảm có cơ chế giới hạn số lần gọi để chống tấn công brute-force. | Flask-Limiter (cấu hình giới hạn theo IP và user) |
| NFR-S06 | Bảo mật kết nối WebSocket | Các kết nối WebSocket chỉ cho phép từ các nguồn gốc (origins) được khai báo tường minh trong cấu hình `CORS_ORIGINS`. | Flask-SocketIO CORS configuration |
| NFR-S07 | Ngăn chặn Path Traversal | Tên tệp được tải lên phải được kiểm tra và làm sạch (`secure_filename`) để ngăn chặn tấn công đường dẫn thư mục. | Werkzeug `secure_filename` |

## 5.3. Yêu cầu Tính sẵn sàng (Availability)

| Mã Yêu cầu | Danh mục | Mô tả Yêu cầu | Ngưỡng chấp nhận |
|------------|----------|----------------|------------------|
| NFR-A01 | Uptime | Tỷ lệ thời gian hệ thống hoạt động bình thường trong môi trường production. | ≥ 99% (tương đương < 7.3 giờ downtime/năm) |
| NFR-A02 | Khởi động lại tự động | Các container bị lỗi (crashed) phải được khởi động lại tự động bởi Docker Engine. | Cấu hình `restart: always` cho tất cả service trong [docker-compose.yml](file:///c:/Users/quocd/Documents/Task2/docker-compose.yml) |
| NFR-A03 | Tiến trình nền | Tiến trình gửi nhắc nhở qua email (`background_tasks`) phải hoạt động song song và độc lập với luồng phục vụ HTTP chính, không gây gián đoạn dịch vụ. | Background thread hoạt động liên tục, phiên kiểm tra mỗi 60 giây |

## 5.4. Yêu cầu Khả năng Mở rộng (Scalability)

| Mã Yêu cầu | Danh mục | Mô tả Yêu cầu | Cơ chế triển khai |
|------------|----------|----------------|-------------------|
| NFR-SC01 | Mở rộng ngang (Horizontal Scaling) cho WebSocket | Khi hệ thống cần chạy nhiều instance Flask-SocketIO song song, phải có cơ chế đồng bộ trạng thái kết nối giữa các instance. | Tích hợp Redis làm message queue cho Socket.IO (`REDIS_URL` trong [.env](file:///c:/Users/quocd/Documents/Task2/.env)). Biến `REDIS_URL` điều khiển chế độ hoạt động |
| NFR-SC02 | Reverse Proxy & Load Balancing | Nginx đóng vai trò reverse proxy, xử lý SSL termination và routing request đến các backend instance. | Nginx `nginx.conf` → Upstream Flask application |
| NFR-SC03 | Containerization | Toàn bộ các service (Flask App, Nginx, Prometheus, Grafana, Redis) được đóng gói thành Docker images và điều phối bởi Docker Compose, đảm bảo môi trường nhất quán. | [Dockerfile](file:///c:/Users/quocd/Documents/Task2/Dockerfile) + [docker-compose.yml](file:///c:/Users/quocd/Documents/Task2/docker-compose.yml) |
| NFR-SC04 | Giám sát & Quan sát (Observability) | Hệ thống phải cung cấp khả năng giám sát metrics thời gian thực (request rate, latency, error rate, CPU, RAM). | Prometheus + prometheus-flask-exporter; Grafana Dashboard |

---

# 6. Ràng buộc & Giả định (Constraints & Assumptions)

## 6.1. Ràng buộc Kỹ thuật

| STT | Ràng buộc | Mô tả |
|-----|-----------|-------|
| C-01 | Cơ sở dữ liệu | Hệ thống được thiết kế và tối ưu cho SQLite (phát triển) và có thể nâng cấp lên PostgreSQL/MySQL (production). Toàn bộ truy vấn sử dụng SQLAlchemy ORM, đảm bảo tính trung lập với CSDL. |
| C-02 | Môi trường chạy | Ứng dụng được thiết kế để chạy trong môi trường Docker container trên hệ điều hành Linux. |
| C-03 | Trình duyệt hỗ trợ | Hệ thống hỗ trợ các trình duyệt hiện đại (Chrome ≥ 90, Firefox ≥ 88, Edge ≥ 90). Không cam kết tương thích với Internet Explorer. |
| C-04 | Kích thước tệp | Tệp tải lên bị giới hạn bởi cấu hình Nginx (`client_max_body_size`) và Flask, mặc định là 50 MB mỗi tệp. |
| C-05 | Phụ thuộc ngoài | Chức năng gửi email phụ thuộc vào dịch vụ SMTP bên ngoài (cấu hình trong [.env](file:///c:/Users/quocd/Documents/Task2/.env)). Nếu SMTP không khả dụng, thông báo email sẽ bị bỏ qua nhưng thông báo in-app vẫn hoạt động. |
| C-06 | Ngôn ngữ | Toàn bộ giao diện người dùng và tài liệu hệ thống hiện tại chỉ hỗ trợ Tiếng Việt. |

## 6.2. Giả định Nghiệp vụ

| STT | Giả định | Lý do |
|-----|----------|-------|
| A-01 | Mỗi người dùng chỉ thuộc một vai trò cố định (Admin, Teacher, hoặc Student) trong suốt vòng đời tài khoản. Việc thay đổi vai trò do Admin thực hiện thủ công. | Mô hình phân quyền RBAC đơn role được thiết kế theo cơ chế này. |
| A-02 | Sinh viên không thể tự tạo nhiệm vụ. Tất cả nhiệm vụ đều được khởi tạo bởi Admin hoặc Teacher. | Đảm bảo tính kiểm soát và tránh nhiễu loạn dữ liệu trong môi trường giảng dạy. |
| A-03 | Mọi người dùng đều có kết nối Internet ổn định để sử dụng đầy đủ các tính năng Real-time (WebSocket). | Tính năng core phụ thuộc vào WebSocket; chế độ ngoại tuyến không được hỗ trợ. |
| A-04 | Admin là người duy nhất thiết lập cấu trúc năm học, học kỳ trước khi các giảng viên có thể bắt đầu tạo nhiệm vụ và lịch học. | Các thực thể nhiệm vụ và lịch có trường tham chiếu `academic_year` và `semester`. |
| A-05 | Hệ thống hoạt động trên môi trường mạng nội bộ (Intranet) của trường là kịch bản triển khai chính. Truy cập từ Internet phải thông qua VPN hoặc cấu hình bảo mật bổ sung. | Phù hợp với mô hình bảo mật đã áp dụng (CORS hạn chế, CSP). |

---

# 7. Thuật ngữ (Glossary)

| Thuật ngữ / Viết tắt | Giải thích |
|-----------------------|-----------|
| **BRD** | Business Requirements Document – Tài liệu Yêu cầu Nghiệp vụ |
| **API** | Application Programming Interface – Giao diện lập trình ứng dụng, cho phép các thành phần phần mềm giao tiếp với nhau |
| **REST API** | Representational State Transfer API – Kiến trúc API phổ biến sử dụng các phương thức HTTP (GET, POST, PUT, DELETE) |
| **JWT** | JSON Web Token – Tiêu chuẩn mã hóa token được sử dụng để xác thực và truyền thông tin an toàn giữa các bên |
| **WebSocket** | Giao thức truyền thông song công toàn phần (full-duplex) cho phép giao tiếp hai chiều liên tục giữa client và server |
| **Socket.IO** | Thư viện JavaScript/Python xây dựng trên WebSocket, bổ sung khả năng dự phòng (fallback) và chia phòng (rooms) |
| **RBAC** | Role-Based Access Control – Kiểm soát truy cập dựa trên vai trò người dùng |
| **Redis** | Remote Dictionary Server – Cơ sở dữ liệu in-memory được sử dụng làm message queue cho Socket.IO khi scale ngang |
| **Docker** | Nền tảng containerization cho phép đóng gói ứng dụng và môi trường chạy vào các container độc lập |
| **Nginx** | Web server và reverse proxy hiệu suất cao, đóng vai trò lớp trung gian giữa người dùng và ứng dụng Flask |
| **Prometheus** | Hệ thống thu thập và lưu trữ metrics dạng time-series, dùng để giám sát ứng dụng |
| **Grafana** | Nền tảng trực quan hóa dữ liệu metrics, tích hợp với Prometheus để hiển thị Dashboard giám sát |
| **ORM** | Object-Relational Mapping – Kỹ thuật ánh xạ các đối tượng trong code sang các bảng trong cơ sở dữ liệu quan hệ (SQLAlchemy trong dự án này) |
| **CSP** | Content Security Policy – Chính sách bảo mật nội dung, kiểm soát các nguồn tài nguyên được phép tải trong trang web |
| **XSS** | Cross-Site Scripting – Lỗ hổng bảo mật cho phép kẻ tấn công chèn mã độc vào trang web |
| **SMTP** | Simple Mail Transfer Protocol – Giao thức chuẩn để gửi email |
| **SRS** | Software Requirements Specification – Tài liệu Đặc tả Yêu cầu Phần mềm (tài liệu kỹ thuật bổ sung cho BRD) |
| **KPI** | Key Performance Indicator – Chỉ số hiệu suất cốt yếu dùng để đo lường mức độ đạt được mục tiêu |
| **TTI** | Time to Interactive – Thời gian để trang web có thể tương tác được sau khi tải |
| **Subtask** | Công việc con – Các bước công việc nhỏ hơn được phân cấp bên trong một nhiệm vụ tổng. |
| **Kanban Board** | Bảng Kanban – Công cụ quản lý trực quan thể hiện luồng công việc qua các cột trạng thái |
| **Uptime** | Thời gian hoạt động liên tục của hệ thống, không bị gián đoạn |
| **CORS** | Cross-Origin Resource Sharing – Cơ chế bảo mật trình duyệt kiểm soát việc chia sẻ tài nguyên giữa các miền khác nhau |
| **Bleach** | Thư viện Python dùng để lọc và làm sạch HTML, ngăn chặn nội dung độc hại do người dùng tạo ra |
| **Admin** | Quản trị viên – Vai trò người dùng có quyền cao nhất trong hệ thống |
| **Teacher** | Giảng viên – Vai trò người dùng phụ trách tổ chức học tập |
| **Student** | Sinh viên – Vai trò người dùng thực hiện các nhiệm vụ học tập |

---

*Tài liệu này được soạn thảo bởi Business Analysis Team dựa trên phân tích codebase của dự án EduTask Manager. Mọi thắc mắc hoặc đề xuất thay đổi vui lòng liên hệ trực tiếp với nhóm phát triển để tiến hành cập nhật phiên bản.*

*Phiên bản: 1.0 | Ngày: 25/03/2026 | Trạng thái: Bản Chính thức*
