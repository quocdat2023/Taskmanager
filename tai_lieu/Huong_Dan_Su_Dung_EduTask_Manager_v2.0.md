# 📘 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG
# EduTask Manager – Hệ thống Quản lý Học vụ và Nhiệm vụ Trực tuyến

---

**Phiên bản tài liệu:** 2.0

**Ngày soạn thảo:** 29/03/2026

**Phiên bản trước:** 1.0 (27/03/2026)

**Đối tượng sử dụng:** Quản trị viên, Giảng viên, Sinh viên

**Liên hệ hỗ trợ:** Quản trị viên hệ thống của trường bạn

---

## MỤC LỤC

1. [Giới thiệu](#1-giới-thiệu)
2. [Bắt đầu sử dụng](#2-bắt-đầu-sử-dụng)
3. [Tổng quan giao diện](#3-tổng-quan-giao-diện)
4. [Hướng dẫn sử dụng theo từng chức năng](#4-hướng-dẫn-sử-dụng-theo-từng-chức-năng)
   - 4.1. [Đăng ký tài khoản](#41-đăng-ký-tài-khoản)
   - 4.2. [Đăng nhập hệ thống](#42-đăng-nhập-hệ-thống)
   - 4.3. [Trang chủ (Dashboard)](#43-trang-chủ-dashboard)
   - 4.4. [Quản lý Công việc (Tasks)](#44-quản-lý-công-việc-tasks)
   - 4.5. [Bảng Kanban – Theo dõi tiến độ trực quan](#45-bảng-kanban--theo-dõi-tiến-độ-trực-quan)
   - 4.6. [Lịch học & Sự kiện](#46-lịch-học--sự-kiện)
   - 4.7. [Kho Tài liệu](#47-kho-tài-liệu)
   - 4.8. [Diễn đàn Hỏi & Đáp (QnA)](#48-diễn-đàn-hỏi--đáp-qna)
   - 4.9. [Thông báo](#49-thông-báo)
   - 4.10. [Cài đặt cá nhân](#410-cài-đặt-cá-nhân)
   - 4.11. [Quản lý Người dùng (Dành cho Quản trị viên)](#411-quản-lý-người-dùng-dành-cho-quản-trị-viên)
   - 4.12. [Quản lý Năm học (Dành cho Quản trị viên)](#412-quản-lý-năm-học-dành-cho-quản-trị-viên)
   - 4.13. [Kiểm duyệt Thảo luận QnA (Dành cho Quản trị viên)](#413-kiểm-duyệt-thảo-luận-qna-dành-cho-quản-trị-viên)
   - 4.14. [Phê duyệt Yêu cầu công việc (Dành cho Quản trị viên)](#414-phê-duyệt-yêu-cầu-công-việc-dành-cho-quản-trị-viên)
5. [Các tình huống thường gặp](#5-các-tình-huống-thường-gặp)
6. [Mẹo sử dụng (Tips)](#6-mẹo-sử-dụng-tips)
7. [Hỗ trợ](#7-hỗ-trợ)

---

# 1. Giới thiệu

## Hệ thống này dùng để làm gì?

**EduTask Manager** là một trang web giúp nhà trường, giảng viên và sinh viên **quản lý công việc học tập** trên cùng một nền tảng. Thay vì phải liên hệ qua nhiều kênh khác nhau (email, Zalo, nhóm Facebook...), tất cả mọi thứ đều được tập trung tại đây:

- 📋 **Giao và theo dõi bài tập** – Giảng viên giao bài, sinh viên cập nhật tiến độ
- 📅 **Quản lý lịch học** – Xem lịch, nhận nhắc nhở trước giờ học qua email
- 📂 **Kho tài liệu** – Tải lên và tải xuống giáo trình, bài giảng
- ❓ **Hỏi đáp** – Sinh viên đặt câu hỏi, giảng viên giải đáp
- 🔔 **Thông báo tức thì** – Nhận biết ngay khi có thay đổi mà không cần tải lại trang

## Ai nên đọc tài liệu này?

- **Sinh viên** – muốn biết cách xem bài tập, cập nhật tiến độ, hỏi đáp
- **Giảng viên** – muốn biết cách tạo công việc, quản lý lịch, tải tài liệu
- **Quản trị viên (Admin)** – muốn biết cách quản lý người dùng, năm học, kiểm duyệt nội dung

---

# 2. Bắt đầu sử dụng

## Bạn cần chuẩn bị gì?

| Yêu cầu | Chi tiết |
|----------|----------|
| 🌐 Trình duyệt web | Chrome (phiên bản 90 trở lên), Firefox, hoặc Microsoft Edge |
| 🔗 Đường dẫn truy cập | Địa chỉ website do nhà trường cung cấp |
| 📧 Email | Email cá nhân đang hoạt động (để nhận thông báo) |
| 📱 Kết nối Internet | Cần ổn định để sử dụng các tính năng cập nhật tức thì |

> ⚠️ Hệ thống **không hỗ trợ** trình duyệt Internet Explorer. Nên sử dụng Chrome để có trải nghiệm tốt nhất.

---

# 3. Tổng quan giao diện

Sau khi đăng nhập thành công, bạn sẽ thấy giao diện chính gồm các khu vực sau:

```
┌──────────────────────────────────────────────────────────────┐
│  [THANH TIÊU ĐỀ]  ☰ Menu | Tên trang      🔔 💬  👤 Tên  │
├──────────┬───────────────────────────────────────────────────┤
│          │                                                   │
│  THANH   │                                                   │
│  ĐIỀU    │           KHU VỰC NỘI DUNG CHÍNH                │
│  HƯỚNG   │                                                   │
│  BÊN     │   (Hiển thị nội dung tùy theo trang bạn chọn)   │
│  TRÁI    │                                                   │
│          │                                                   │
└──────────┴───────────────────────────────────────────────────┘
```

### Giải thích từng khu vực:

| Khu vực | Mô tả |
|---------|-------|
| **Thanh tiêu đề (trên cùng)** | Hiển thị tên trang hiện tại, nút chuông thông báo 🔔, nút vào diễn đàn QnA 💬, và avatar người dùng 👤 |
| **Thanh điều hướng bên trái (Sidebar)** | Danh sách các trang bạn có thể truy cập. Nhấn vào tên trang để chuyển đến |
| **Khu vực nội dung chính** | Hiển thị nội dung của trang bạn đang xem (ví dụ: danh sách công việc, lịch học...) |

### Các mục trên thanh điều hướng (tùy thuộc vai trò):

| Mục menu | Ai thấy | Chức năng |
|----------|---------|-----------|
| 🏠 Dashboard | Tất cả | Trang tổng quan, xem số liệu nhanh |
| 📋 Danh sách công việc | Admin, Giảng viên | Xem, tạo, quản lý công việc |
| 📊 Kanban Board | Admin, Giảng viên | Bảng theo dõi tiến độ trực quan |
| 📅 Lịch học | Tất cả | Xem và quản lý lịch học, sự kiện |
| 📂 Tài liệu | Tất cả | Kho tài liệu học tập |
| 👥 Quản lý người dùng | Chỉ Admin | Duyệt, khóa, phân quyền tài khoản |
| 📆 Quản lý năm học | Chỉ Admin | Tạo và quản lý năm học |
| 💬 Quản lý thảo luận | Chỉ Admin | Kiểm duyệt nội dung QnA |
| ✅ Yêu cầu phê duyệt | Chỉ Admin | Xử lý yêu cầu giao/xóa công việc |
| ⚙️ Cài đặt | Tất cả | Chỉnh sửa hồ sơ cá nhân |

---

# 4. Hướng dẫn sử dụng theo từng chức năng

---

## 4.1. Đăng ký tài khoản

**Mục đích:** Tạo tài khoản mới để sử dụng hệ thống. Hiện tại, trang đăng ký dành cho **Sinh viên**. Tài khoản Giảng viên và Admin do Quản trị viên tạo.

**Các bước thực hiện:**

1. Mở trình duyệt, truy cập địa chỉ hệ thống do nhà trường cung cấp.
2. Tại trang đăng nhập, nhấn vào dòng chữ **"Đăng ký ngay"** ở phía dưới.
3. Điền đầy đủ thông tin vào biểu mẫu:
   - **Tên đăng nhập** *(bắt buộc)* – tên bạn sẽ dùng để đăng nhập
   - **Họ và tên** *(bắt buộc)* – tên hiển thị trong hệ thống
   - **Email** *(bắt buộc)* – dùng để nhận thông báo (cần là email đang hoạt động)
   - **Mật khẩu** *(bắt buộc)* – nên đặt mật khẩu đủ mạnh
   - **Mã sinh viên** *(tùy chọn)* – nhập đúng MSV để xác minh danh tính
   - **Khoa/Ngành** *(tùy chọn)* – giúp hệ thống phân nhóm
4. Nhấn nút **"Đăng ký"**.
5. Chờ Quản trị viên **phê duyệt** tài khoản. Bạn sẽ nhận email xác nhận khi được duyệt.

**Hình minh họa:**

> [Screenshot: Màn hình Đăng ký, hiển thị biểu mẫu với các ô nhập liệu: Tên đăng nhập, Họ và tên, Email, Mật khẩu, Mã sinh viên, Khoa/Ngành. Phía dưới có nút "Đăng ký" màu tím và dòng "Đã có tài khoản? Đăng nhập"]

**Lưu ý:**
- ⚠️ Tài khoản **chưa được duyệt** sẽ **không thể đăng nhập**. Nếu chờ quá 1 ngày làm việc, liên hệ Quản trị viên.
- ⚠️ Hãy nhớ chính xác tên đăng nhập và mật khẩu. Hiện chưa có tính năng tự đặt lại mật khẩu.
- ⚠️ **Không** chia sẻ mật khẩu cho người khác.

---

## 4.2. Đăng nhập hệ thống

**Mục đích:** Truy cập vào hệ thống sau khi đã có tài khoản được duyệt.

**Các bước thực hiện:**

1. Mở trình duyệt, truy cập địa chỉ hệ thống.
2. Tại màn hình đăng nhập, nhập:
   - **Tên đăng nhập hoặc Email** vào ô đầu tiên
   - **Mật khẩu** vào ô thứ hai
3. Nhấn nút **"Đăng nhập"**.
4. Nếu thông tin đúng, bạn sẽ được chuyển đến **Trang chủ (Dashboard)**.

**Hình minh họa:**

> [Screenshot: Màn hình Đăng nhập với logo EduTask, tiêu đề "Hệ thống quản lý công việc và học tập", hai ô nhập Tên đăng nhập và Mật khẩu, nút "Đăng nhập", và dòng "Chưa có tài khoản? Đăng ký ngay"]

**Lưu ý:**
- Nếu quên mật khẩu → liên hệ **Quản trị viên** để được cấp lại.
- Nên **đăng xuất** khi dùng xong, đặc biệt trên máy tính công cộng.
- Để đăng xuất: nhấn vào **avatar** ở góc trên phải → chọn **"Đăng xuất"** (chữ đỏ ở cuối menu).

---

## 4.3. Trang chủ (Dashboard)

**Mục đích:** Xem nhanh tổng quan về tình hình hoạt động, số liệu thống kê.

### Dành cho Quản trị viên (Admin):

Trang chủ hiển thị:
- **Hàng thống kê phía trên:** Tổng người dùng, Tổng giảng viên, Tổng sinh viên, Yêu cầu phê duyệt Task, Tài khoản chờ duyệt
- **Hàng thống kê công việc:** Tổng số công việc, Công việc quá hạn, Đã hoàn thành
- **Bảng yêu cầu chưa xử lý:** Danh sách các yêu cầu giao/xóa việc đang chờ Admin duyệt
- **Trạng thái hệ thống:** Kiểm tra Database, Storage, Mail đang hoạt động bình thường hay không

**Hình minh họa:**

> [Screenshot: Dashboard Admin với 5 thẻ thống kê ở trên (Tổng Người dùng, Tổng Giảng viên, Tổng Sinh viên, Yêu cầu phê duyệt, Tài khoản chờ duyệt), 3 thẻ công việc ở giữa, bảng Yêu cầu chưa xử lý bên trái và trạng thái Hệ thống bên phải]

### Dành cho Giảng viên và Sinh viên:

Trang chủ hiển thị tổng quan các công việc được giao, tiến độ cá nhân, và sự kiện sắp tới.

---

## 4.4. Quản lý Công việc (Tasks)

**Mục đích:** Tạo, giao, theo dõi và cập nhật tiến độ các nhiệm vụ/bài tập.

### 🧑‍🏫 Dành cho Giảng viên / Admin – Tạo công việc mới

**Các bước thực hiện:**

1. Nhấn vào **"Danh sách công việc"** trên thanh điều hướng bên trái.
2. Nhấn nút **"+ Tạo công việc"** ở góc trên bên phải.
3. Một cửa sổ bật lên (popup) sẽ hiện ra. Điền thông tin:
   - **Tên công việc** *(bắt buộc)* – ví dụ: "Bài tập tuần 5 – Lập trình Web"
   - **Mô tả** *(tùy chọn)* – giải thích chi tiết yêu cầu
   - **Trạng thái** – Chưa bắt đầu / Đang làm / Hoàn thành
   - **Độ ưu tiên** – Thấp / Trung bình / Cao / Khẩn cấp
   - **Hạn cuối** – chọn ngày nộp bài
4. *(Tùy chọn)* Điền thêm thông tin môn học:
   - Môn học, Mã môn, Nhóm lớp, Học kỳ, Năm học
5. Chọn **Người thực hiện** – tích chọn sinh viên sẽ nhận công việc này.
6. Nhấn **"Lưu công việc"**.

**Hình minh họa:**

> [Screenshot: Popup "Thêm công việc" với các ô: Tên công việc, Mô tả, Trạng thái (dropdown), Độ ưu tiên (dropdown), Hạn cuối (ô chọn ngày). Phần dưới có thông tin Môn học, Mã môn, Nhóm lớp, Học kỳ, Năm học và danh sách checkbox Người thực hiện]

**Lưu ý:**
- ⚠️ Với vai trò **Giảng viên**, việc giao cho sinh viên cần **được Admin phê duyệt** trước khi sinh viên nhận được. Admin giao trực tiếp (không cần phê duyệt).
- ⚠️ Muốn **xóa** công việc → phải gửi **yêu cầu xóa** để Admin duyệt.
- ⚠️ Điền đúng **Môn học** và **Năm học** để dễ tìm kiếm và lọc sau này.

### 🧑‍🎓 Dành cho Sinh viên – Xem và cập nhật tiến độ

**Các bước thực hiện:**

1. Vào **Dashboard** hoặc nhấn vào thông báo công việc mới.
2. Nhấn vào **thẻ công việc** để xem chi tiết.
3. Cập nhật trạng thái cá nhân:
   - 🔵 **Chưa bắt đầu** → 🟡 **Đang làm** → 🟢 **Hoàn thành**
4. Có thể viết **ghi chú** hoặc **bình luận** để báo cáo giảng viên.
5. Nhấn **Lưu** để hệ thống ghi nhận.

**Lưu ý:**
- ⚠️ Bạn **chỉ thấy công việc được giao cho mình** – không thấy công việc của sinh viên khác.
- ⚠️ Nếu bạn bị **xóa khỏi danh sách** thực hiện, công việc đó sẽ **biến mất** khỏi màn hình của bạn.

### Tìm kiếm và lọc công việc

Phía trên danh sách công việc có **thanh lọc** giúp tìm nhanh:
- **Ô tìm kiếm** – gõ tên công việc hoặc môn học
- **Lọc theo Học kỳ** – HK1, HK2, HK3
- **Lọc theo Năm học** – chọn năm học cụ thể
- **Lọc theo Trạng thái** – Chưa bắt đầu, Đang làm, Hoàn thành
- **Nút "Đặt lại"** – xóa tất cả bộ lọc, hiển thị lại toàn bộ

---

## 4.5. Bảng Kanban – Theo dõi tiến độ trực quan

**Mục đích:** Xem tiến độ công việc một cách trực quan dưới dạng bảng 3 cột, giống như bảng dán giấy nhớ.

**Giải thích bảng Kanban:**

| Cột | Ý nghĩa |
|-----|---------|
| 📋 **Chưa làm (To Do)** | Công việc mới, chưa ai bắt đầu |
| ⚙️ **Đang thực hiện (In Progress)** | Công việc đang được làm |
| ✅ **Hoàn thành (Done)** | Công việc đã xong |

**Các bước thực hiện (Giảng viên / Admin):**

1. Nhấn **"Kanban Board"** trên thanh điều hướng.
2. Xem tổng quan các thẻ công việc trong 3 cột.
3. **Kéo và thả** thẻ công việc từ cột này sang cột khác để cập nhật trạng thái.

**Hình minh họa:**

> [Screenshot: Bảng Kanban với 3 cột dọc: "To Do", "In Progress", "Done". Mỗi cột chứa các thẻ công việc nhỏ hiển thị tên, mức ưu tiên, hạn nộp và avatar người thực hiện]

**Lưu ý:**
- ⚠️ **Sinh viên chỉ xem**, không kéo thả được.
- ⚠️ Mọi thay đổi cập nhật **tức thì** – người khác sẽ thấy ngay mà không cần tải lại trang.

---

## 4.6. Lịch học & Sự kiện

**Mục đích:** Quản lý lịch giảng dạy, lịch thi, cuộc họp và các sự kiện quan trọng. Hệ thống sẽ nhắc nhở qua email trước khi sự kiện diễn ra.

### 🧑‍🏫 Dành cho Giảng viên / Admin – Tạo lịch mới

**Các bước thực hiện:**

1. Nhấn **"Lịch học"** trên thanh điều hướng.
2. Nhấn nút **"+ Thêm mới"** ở góc trên.
3. Điền thông tin trong popup:
   - **Tên môn học / Sự kiện** *(bắt buộc)* – ví dụ: "Toán cao cấp – Tiết 1-3"
   - **Loại** *(bắt buộc)* – Dạy chính / Dạy bù / Sinh hoạt chủ nhiệm / Đã báo vắng / Dạy thay / Sự kiện khác
   - **Mã phòng học** – ví dụ: B303
   - **Thời gian bắt đầu và kết thúc** *(bắt buộc)*
   - **Mã học phần, Tên học phần, Nhóm lớp** *(tùy chọn)*
   - **Mô tả thêm** *(tùy chọn)*
4. Thiết lập **Nhắc nhở qua Email** – chọn một hoặc nhiều mốc: 5 Phút, 15 Phút, 1 Giờ, 1 Ngày, 1 Tuần
5. Nhấn **"Lưu"**.

**Hình minh họa:**

> [Screenshot: Popup "Thêm lịch giảng dạy" với các ô nhập liệu. Phía dưới có phần "Nhắc nhở qua Email" với các nút chip: 5 Phút, 15 Phút, 1 Giờ, 1 Ngày, 1 Tuần có thể bật/tắt]

**Bảng chú thích màu sắc trên lịch:**

| Màu | Loại sự kiện |
|-----|-------------|
| 🟡 Vàng | Dạy chính |
| 🔵 Xanh dương | Dạy bù |
| 🟣 Tím | Sinh hoạt chủ nhiệm |
| 🔴 Đỏ | Đã báo vắng |
| 🟢 Xanh lá | Dạy thay |
| 🟢 Xanh ngọc | Sự kiện khác |

### 🧑‍🎓 Dành cho Sinh viên – Xem lịch học

1. Nhấn **"Lịch học"** trên thanh điều hướng.
2. Xem lịch theo dạng **tháng** hoặc **tuần**.
3. Nhấp vào sự kiện trên lịch để xem **chi tiết** (phòng học, ghi chú...).

**Lưu ý:**
- ⚠️ Kiểm tra **giờ** kỹ trước khi lưu – hệ thống dùng giờ Việt Nam (GMT+7).
- ⚠️ Nhắc nhở email chỉ gửi nếu email của bạn đã được cấu hình đúng và dịch vụ mail đang hoạt động.

---

## 4.7. Kho Tài liệu

**Mục đích:** Lưu trữ và chia sẻ tài liệu học tập (giáo trình, bài tập, slide bài giảng...).

### 🧑‍🏫 Dành cho Giảng viên / Admin – Tải lên tài liệu

**Các bước thực hiện:**

1. Nhấn **"Tài liệu"** trên thanh điều hướng.
2. Nhấn nút **"Tải tài liệu"** ở góc trên phải.
3. Trong popup, điền:
   - **Chọn file** *(bắt buộc)* – chọn từ máy tính
   - **Tiêu đề tài liệu** *(bắt buộc)* – đặt tên dễ nhớ
   - **Danh mục** – Bài giảng / Bài tập / Tài liệu tham khảo / Khác
   - **Mô tả thêm** *(tùy chọn)*
   - Thông tin Môn học: Tên môn, Mã môn, Nhóm lớp *(tùy chọn)*
4. Nhấn **"Bắt đầu tải lên"**.

**Hình minh họa:**

> [Screenshot: Popup "Tải lên Học liệu" với nút chọn file, ô nhập Tiêu đề, dropdown Danh mục, ô Mô tả, và 3 ô Thông tin Môn học]

### 🧑‍🎓 Dành cho Sinh viên – Tìm và tải tài liệu

1. Vào **"Tài liệu"** trên thanh điều hướng.
2. Dùng **ô tìm kiếm** để gõ tên tài liệu hoặc môn học.
3. Nhấn nút **Tải xuống** bên cạnh tài liệu cần lấy.

**Lưu ý:**
- ⚠️ Dung lượng tối đa: **16 MB** mỗi file.
- ⚠️ Các định dạng hỗ trợ: PDF, DOCX, XLSX, PPTX, PNG, JPG, ZIP, RAR, TXT...

---

## 4.8. Diễn đàn Hỏi & Đáp (QnA)

**Mục đích:** Đặt câu hỏi về bài học, môn học và nhận câu trả lời từ giảng viên hoặc bạn bè.

### Đặt câu hỏi mới

**Các bước thực hiện:**

1. Nhấn vào **biểu tượng 💬** trên thanh tiêu đề, hoặc vào trang Hỏi & Đáp.
2. Nhấn nút **"Đặt câu hỏi mới"** (nút đỏ ở góc phải).
3. Điền:
   - **Tiêu đề câu hỏi** *(bắt buộc)* – ngắn gọn, rõ ràng
   - **Nội dung chi tiết** *(bắt buộc)* – mô tả đầy đủ vấn đề
   - **Môn học** liên quan *(tùy chọn)* – giúp giảng viên tìm thấy câu hỏi
4. Nhấn **"Gửi câu hỏi"**.

### Trả lời câu hỏi

1. Trong danh sách, nhấn vào câu hỏi muốn trả lời.
2. Kéo xuống cuối, gõ câu trả lời vào ô bình luận.
3. Nhấn **"Gửi"** – câu trả lời hiển thị ngay tức thì.

### Chấp nhận câu trả lời tốt nhất (Người hỏi / Giảng viên / Admin)

- Nhấn dấu ✅ bên cạnh câu trả lời được cho là đúng nhất.
- Câu hỏi tự động chuyển sang trạng thái **"Đã giải quyết"**.

**Hình minh họa:**

> [Screenshot: Trang Hỏi & Đáp với banner tìm kiếm "Xin chào, chúng tôi có thể giúp gì cho bạn?", danh sách câu hỏi bên trái (mỗi câu hỏi hiển thị tiêu đề, trạng thái, tên người hỏi, số câu trả lời), và thanh thống kê bên phải (Tổng câu hỏi, Đã giải quyết, Tỷ lệ trả lời)]

**Lưu ý:**
- ⚠️ Đặt câu hỏi **đúng môn học** để giảng viên phụ trách dễ tìm thấy.
- ⚠️ Đọc kỹ câu hỏi cũ trước khi đăng – tránh trùng lặp.
- ⚠️ Nội dung không phù hợp có thể bị Admin **ẩn hoặc xóa**.

---

## 4.9. Thông báo

**Mục đích:** Nhận biết ngay khi có thay đổi liên quan đến bạn (công việc mới, phê duyệt, câu trả lời...).

### Các loại thông báo:

| Kênh | Khi nào nhận |
|------|-------------|
| 🔔 **Trên màn hình** (In-app) | Ngay khi có: công việc mới được giao, yêu cầu được duyệt/từ chối, câu trả lời mới, bình luận mới |
| 📧 **Qua Email** | Khi: tài khoản được duyệt, sắp đến lịch học (theo nhắc nhở đã cài), công việc được giao |

### Cách xem thông báo:

1. Nhấn vào **biểu tượng chuông 🔔** ở góc trên bên phải.
2. Danh sách thông báo hiện ra. Nhấn vào từng thông báo để đi đến nội dung liên quan.
3. Nhấn **"Đánh dấu đã đọc"** để xóa số đỏ trên chuông.

**Lưu ý:**
- ⚠️ Thông báo chỉ gửi cho **người liên quan** – bạn không nhận thông báo cho hành động do chính mình thực hiện.
- ⚠️ Nếu không nhận email → kiểm tra thư mục **Spam/Junk**.

---

## 4.10. Cài đặt cá nhân

**Mục đích:** Cập nhật thông tin cá nhân và tùy chỉnh cách nhận nhắc nhở.

**Các bước thực hiện:**

1. Nhấn vào **avatar** (hình tròn) ở góc trên phải → chọn **"Cài đặt"**.
2. Tại trang Cài đặt, bạn có thể:
   - **Chọn mốc nhắc hẹn mặc định** – hệ thống sẽ tự chọn sẵn các mốc này khi bạn tạo lịch mới (5 Phút / 15 Phút / 1 Giờ / 1 Ngày / 1 Tuần)
   - Cập nhật **Họ và tên**
   - Cập nhật **Số điện thoại**
   - Cập nhật **Khoa / Phòng ban**
3. Nhấn **"Lưu thay đổi"**.

**Hình minh họa:**

> [Screenshot: Trang Cài đặt, bên trái có form với phần "Mốc nhắc hẹn mặc định" (5 nút chip bật/tắt), form Họ và tên - Số điện thoại - Khoa, nút "Lưu thay đổi". Bên phải hiển thị thẻ hồ sơ cá nhân (avatar, tên, vai trò)]

**Lưu ý:**
- ⚠️ Mốc nhắc hẹn mới chỉ áp dụng cho **lịch tạo sau** khi lưu – lịch cũ giữ nguyên.
- ⚠️ Không thể tự đổi **Tên đăng nhập** – cần liên hệ Admin.

---

## 4.11. Quản lý Người dùng (Dành cho Quản trị viên)

**Mục đích:** Duyệt tài khoản mới, khóa/mở khóa, thay đổi vai trò, và quản lý toàn bộ người dùng trong hệ thống.

**Các bước thực hiện:**

1. Nhấn **"Quản lý người dùng"** trên thanh điều hướng (chỉ Admin mới thấy).
2. Xem danh sách tất cả tài khoản trong hệ thống (có tìm kiếm theo tên, email, MSV).
3. Các thao tác cho từng người dùng:
   - **Duyệt tài khoản** – cho tài khoản đang chờ duyệt
   - **Khóa / Mở khóa** – tạm ngưng hoặc kích hoạt lại tài khoản
   - **Thay đổi vai trò** – chuyển từ Sinh viên sang Giảng viên (hoặc ngược lại)
   - **Chỉnh sửa thông tin** – cập nhật email, tên, mật khẩu, khoa...
   - **Xóa tài khoản** – xóa vĩnh viễn (cẩn thận!)
4. Nhấn **"+ Thêm người dùng"** nếu muốn tạo tài khoản mới trực tiếp (thường dùng cho tài khoản Giảng viên).

**Hình minh họa:**

> [Screenshot: Trang Quản lý người dùng với ô tìm kiếm, nút "Thêm người dùng", và bảng danh sách hiển thị: Tên – Vai trò – Ngành – Trạng thái – Thao tác (các nút Duyệt/Sửa/Khóa/Xóa)]

**Lưu ý:**
- ⚠️ Mật khẩu mặc định khi tạo tài khoản mới là **123456** – hãy yêu cầu người dùng đổi ngay.
- ⚠️ Chỉ một vai trò duy nhất cho mỗi tài khoản (Admin / Giảng viên / Sinh viên).

---

## 4.12. Quản lý Năm học (Dành cho Quản trị viên)

**Mục đích:** Tạo và quản lý danh sách năm học cho toàn hệ thống. Năm học được dùng làm dữ liệu tham chiếu khi tạo công việc và lịch học.

**Các bước thực hiện:**

1. Nhấn **"Quản lý năm học"** trên thanh điều hướng.
2. Xem danh sách năm học hiện có và năm học **đang hoạt động** (dùng làm mặc định).
3. Nhấn **"+ Thêm Năm học"** để tạo mới:
   - Nhập **Năm bắt đầu** (ví dụ: 2025) → Năm kết thúc tự động điền (2026)
   - Nhập **Mô tả** *(tùy chọn)*
   - Bật **"Đặt làm năm học hiện tại"** nếu muốn dùng năm này làm mặc định
4. Nhấn **"Tạo năm học"**.

**Các thao tác khác:**
- ✅ **Đặt làm hiện tại** – nhấn nút tick xanh bên cạnh năm học
- ✏️ **Sửa** – nhấn nút bút chì để chỉnh sửa mô tả
- 🗑️ **Xóa** – nhấn nút thùng rác (chỉ xóa được năm học chưa ai sử dụng)

**Lưu ý:**
- ⚠️ **Không thể xóa** năm học đang có công việc liên kết – hệ thống sẽ báo lỗi rõ ràng.
- ⚠️ **Không thể xóa** năm học đang ở trạng thái "hoạt động" – cần chuyển sang năm khác trước.
- ⚠️ Chỉ **một năm học** có thể ở trạng thái "Đang hoạt động" tại một thời điểm.

---

## 4.13. Kiểm duyệt Thảo luận QnA (Dành cho Quản trị viên)

**Mục đích:** Xem, tìm kiếm và kiểm duyệt nội dung trong diễn đàn Hỏi & Đáp – ẩn hoặc xóa những nội dung không phù hợp.

**Các bước thực hiện:**

1. Nhấn **"Quản lý thảo luận"** trên thanh điều hướng.
2. Xem danh sách tất cả các câu hỏi kèm theo bình luận.
3. Dùng **ô tìm kiếm** ở trên cùng để tìm nhanh nội dung cần kiểm duyệt.
4. Các thao tác cho từng câu trả lời/bình luận:
   - **Ẩn** – ẩn nội dung khỏi diễn đàn (vẫn lưu trong hệ thống)
   - **Hiện** – bỏ ẩn nội dung đã ẩn trước đó
   - **Xóa** – xóa mềm nội dung không phù hợp (có cửa sổ xác nhận)
5. Nhấn **"Tải thêm thảo luận"** nếu muốn xem các bài cũ hơn.

**Hình minh họa:**

> [Screenshot: Trang Quản lý thảo luận với ô tìm kiếm phía trên, danh sách các câu hỏi dạng card. Mỗi card hiển thị: avatar người hỏi, tên, thời gian, nội dung câu hỏi, và bên dưới là các bình luận kèm nút Ẩn/Xóa]

---

## 4.14. Phê duyệt Yêu cầu công việc (Dành cho Quản trị viên)

**Mục đích:** Xử lý (duyệt hoặc từ chối) các yêu cầu liên quan đến công việc: giao thêm thành viên, xóa công việc, rút khỏi công việc.

**Các bước thực hiện:**

1. Nhấn **"Yêu cầu phê duyệt"** trên thanh điều hướng (hoặc xem ở trang Dashboard).
2. Xem danh sách yêu cầu đang chờ xử lý.
3. Nhấn vào **biểu tượng xử lý** (✨) bên cạnh yêu cầu.
4. Cửa sổ hiện ra hiển thị:
   - Loại yêu cầu (Giao việc / Xóa việc / Rút khỏi)
   - Người gửi yêu cầu
   - Tên công việc liên quan
   - Đối tượng bị ảnh hưởng
5. Nhập **ghi chú phản hồi** *(tùy chọn)*.
6. Nhấn **"Phê duyệt"** hoặc **"Từ chối"**.

**Lưu ý:**
- ⚠️ Sau khi phê duyệt, hệ thống tự động **gửi thông báo** cho người yêu cầu và người liên quan.
- ⚠️ Nên kiểm tra kỹ thông tin trước khi duyệt – hành động phê duyệt **không thể hoàn tác**.

---

# 5. Các tình huống thường gặp

| Tình huống | Giải pháp |
|------------|-----------|
| ❓ **Quên mật khẩu** | Liên hệ Quản trị viên để được cấp lại mật khẩu mới. Hiện chưa có tính năng tự đặt lại. |
| ❓ **Đăng ký rồi nhưng không đăng nhập được** | Tài khoản chưa được Admin phê duyệt. Chờ email xác nhận hoặc liên hệ Admin. |
| ❓ **Không thấy công việc đã từng thấy** | Có thể bạn đã bị xóa khỏi danh sách thực hiện. Liên hệ giảng viên hoặc Admin. |
| ❓ **Không nhận được email nhắc nhở** | Kiểm tra thư mục Spam/Junk. Đảm bảo email đăng ký đúng và đang hoạt động. |
| ❓ **Tải file lên báo lỗi** | Kiểm tra dung lượng (tối đa 16 MB) và định dạng file (PDF, DOCX, XLSX, PPTX, PNG, JPG, ZIP...). |
| ❓ **Không xóa được năm học** | Năm học đang được sử dụng bởi công việc hoặc đang ở trạng thái "hoạt động". Cần gỡ liên kết hoặc chuyển trạng thái trước. |
| ❓ **Không xóa được công việc (Giảng viên)** | Giảng viên không xóa trực tiếp được. Cần gửi **yêu cầu xóa** để Admin phê duyệt. |
| ❓ **Sinh viên muốn rút khỏi công việc** | Vào chi tiết công việc → gửi **yêu cầu rút** → chờ Admin duyệt. |
| ❓ **Bình luận/câu trả lời biến mất** | Nội dung có thể đã bị Admin ẩn hoặc xóa do vi phạm quy định. |
| ❓ **Trang không tải được / báo lỗi** | Thử tải lại trang (F5) hoặc xóa cache trình duyệt. Nếu vẫn lỗi, liên hệ Admin. |

---

# 6. Mẹo sử dụng (Tips)

### 💡 Mẹo chung
- **Dùng thanh tìm kiếm** – hầu hết các trang đều có ô tìm kiếm, giúp bạn tìm nhanh thay vì cuộn tìm.
- **Kiểm tra chuông thông báo** thường xuyên – đừng bỏ lỡ thông tin quan trọng.
- **Luôn nhấn Lưu** sau khi thay đổi – thay đổi chưa lưu sẽ bị mất.

### 💡 Dành cho Giảng viên
- **Tạo công việc theo template:** Điền đầy đủ Môn học, Nhóm lớp, Học kỳ → giúp quản lý và lọc dễ dàng hơn.
- **Dùng Kanban Board** để nắm nhanh tiến độ lớp – chỉ cần liếc qua 3 cột là biết tình hình.
- **Đặt nhắc nhở lịch** trước 1 ngày cho các bài kiểm tra quan trọng.

### 💡 Dành cho Sinh viên
- **Cập nhật trạng thái thường xuyên** – giảng viên sẽ đánh giá cao sự chủ động.
- **Đọc câu hỏi cũ** trên QnA trước khi đặt câu mới – có thể câu trả lời đã có sẵn.
- **Lọc công việc theo Trạng thái** = "Chưa bắt đầu" → để biết công việc nào cần ưu tiên.

### 💡 Dành cho Quản trị viên
- **Duyệt tài khoản sớm** – sinh viên mới đăng ký sẽ không vào được nếu chưa duyệt.
- **Thiết lập năm học** đầu tiên trước khi giảng viên tạo công việc/lịch.
- **Kiểm tra Dashboard thường xuyên** – theo dõi yêu cầu phê duyệt và sức khỏe hệ thống.

---

# 7. Hỗ trợ

## Khi gặp vấn đề, bạn nên:

1. **Đọc lại tài liệu này** – phần lớn câu hỏi đã được trả lời trong mục [Tình huống thường gặp](#5-các-tình-huống-thường-gặp).
2. **Tải lại trang** (nhấn F5) – một số lỗi hiển thị có thể tự khắc phục.
3. **Liên hệ Quản trị viên** – nếu vấn đề liên quan đến tài khoản, quyền truy cập, hoặc lỗi hệ thống.
4. **Gửi email hỗ trợ** – theo địa chỉ email được nhà trường thông báo.

## Thông tin liên hệ:

| Hạng mục | Thông tin |
|----------|-----------|
| 📧 Email hỗ trợ | Liên hệ Quản trị viên hệ thống của trường |
| 🕐 Giờ hỗ trợ | Giờ hành chính (Thứ Hai – Thứ Sáu) |
| 📋 Kênh hỗ trợ bổ sung | Diễn đàn Hỏi & Đáp trong hệ thống |

---

## Phụ lục: Bảng tóm tắt quyền hạn theo vai trò

| Chức năng | Sinh viên | Giảng viên | Quản trị viên |
|-----------|:---------:|:----------:|:-------------:|
| Đăng ký tài khoản | ✅ | ❌ (Admin tạo) | ❌ (sẵn có) |
| Xem Dashboard | ✅ | ✅ | ✅ |
| Xem công việc được giao | ✅ | ✅ | ✅ (tất cả) |
| Tạo công việc | ❌ | ✅ | ✅ |
| Giao công việc (trực tiếp) | ❌ | ❌ (qua phê duyệt) | ✅ |
| Cập nhật trạng thái cá nhân | ✅ | ✅ | ✅ |
| Kéo thả Kanban | ❌ | ✅ | ✅ |
| Tạo lịch học / sự kiện | ❌ | ✅ | ✅ |
| Xem lịch học | ✅ | ✅ | ✅ |
| Tải lên tài liệu | ❌ | ✅ | ✅ |
| Tải xuống tài liệu | ✅ | ✅ | ✅ |
| Đặt câu hỏi QnA | ✅ | ✅ | ✅ |
| Trả lời câu hỏi | ✅ | ✅ | ✅ |
| Chấp nhận câu trả lời | ✅ (câu mình hỏi) | ✅ | ✅ |
| Kiểm duyệt QnA | ❌ | ❌ | ✅ |
| Quản lý người dùng | ❌ | ❌ | ✅ |
| Quản lý năm học | ❌ | ❌ | ✅ |
| Phê duyệt yêu cầu | ❌ | ❌ | ✅ |
| Cài đặt cá nhân | ✅ | ✅ | ✅ |

---

*📄 Tài liệu này được soạn thảo bởi Business Analysis & Technical Writing Team – EduTask Manager*

*Phiên bản: 2.0 | Ngày: 29/03/2026 | Trạng thái: Bản Chính thức*

*Dựa trên BRD v2.0 và phân tích giao diện thực tế của hệ thống.*
