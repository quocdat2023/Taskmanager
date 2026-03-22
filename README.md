---
title: TaskManager
emoji: ⚡
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: openrail
short_description: Task ManageAr
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference

# Task Management System

## Giới thiệu
Task Management System là một ứng dụng web giúp quản lý công việc, lịch, tài liệu, hệ thống hỏi đáp và nhắn tin nội bộ, được thiết kế cho môi trường giáo dục (quản trị viên, giảng viên, sinh viên).

Tính năng chính:
- Quản lý nhiệm vụ: tạo, giao, cập nhật trạng thái, lịch sử, yêu cầu xóa/rút
- Quản lý lịch và nhắc nhở
- Quản lý tài liệu (upload/download)
- Hệ thống Q&A (câu hỏi & trả lời)
- Thông báo trong ứng dụng và gửi email
- Chat thời gian thực bằng Socket.IO
- Giao diện HTML cho admin/teacher/student

---

## Cài đặt

Yêu cầu phần mềm:
- Python 3.10
- pip
- (Tùy chọn) Docker & Docker Compose
- (Tùy chọn) Redis nếu muốn scale Socket.IO

1. Clone repository và chuyển vào thư mục dự án:

```bash
git clone <repo-url>
cd task-management
```

2. Tạo virtual environment và cài dependencies:

```bash
python -m venv .venv
# Windows
.venv\\Scripts\\activate
# Unix
source .venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt
```

3. Cấu hình biến môi trường (hoặc tạo file `.env`):

Ví dụ `.env`:

```
FLASK_APP=run.py
FLASK_CONFIG=development
SECRET_KEY=change-me
JWT_SECRET_KEY=change-jwt
DATABASE_URL=sqlite:///task_management.db
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=youremail@example.com
MAIL_PASSWORD=yourpassword
MAIL_DEFAULT_SENDER=youremail@example.com
REDIS_URL=redis://localhost:6379/0
```

4. Khởi tạo database (mặc định: SQLite file `task_management.db`). Ứng dụng sẽ tự tạo bảng khi chạy lần đầu. Nếu dùng Flask-Migrate:

```bash
flask db init
flask db migrate -m "Initial"
flask db upgrade
```

5. Chạy ứng dụng (local):

```bash
python run.py
```

6. Chạy bằng Docker Compose (tùy chọn):

```bash
docker-compose up --build
```

---

## Cấu hình

- Các cấu hình chính nằm tại `app/config.py`.
- Thay đổi `SQLALCHEMY_DATABASE_URI` để dùng DB khác (Postgres, MySQL).
- Cấu hình email (MAIL_*), `SECRET_KEY`, `JWT_SECRET_KEY` cần được thiết lập cho môi trường production.
- `REDIS_URL` để bật Redis cho Socket.IO nếu muốn scale WebSocket across multiple instances.
- `UPLOAD_FOLDER`, `ALLOWED_EXTENSIONS`, `MAX_CONTENT_LENGTH` điều khiển upload files.

Seeding dữ liệu: khi khởi động lần đầu, app sẽ tự tạo một số user mẫu (admin, vài teacher và student) với mật khẩu mặc định được hash (xem `app/__init__.py`).

---

## Hướng dẫn sử dụng

API base: `/api`

Xác thực:
- Đăng ký: `POST /api/register` (JSON: `username`, `email`, `password`, `full_name`, `role`)
- Đăng nhập: `POST /api/login` (JSON: `username`, `password`) → nhận JWT token
- Đính kèm header `Authorization: Bearer <token>` cho endpoint bảo vệ `@jwt_required()`

Các endpoint chính (tóm tắt):
- Auth: `POST /api/register`, `POST /api/login`, `POST /api/logout`, `GET /api/me`, `GET /api/users` (admin)
- Tasks: `POST /api/tasks`, `GET /api/tasks`, `GET /api/tasks/<id>`, `PUT /api/tasks/<id>`, `DELETE /api/tasks/<id>`, `PUT /api/tasks/<id>/status`, `GET /api/tasks/all` (admin)
- Task requests: `GET /api/tasks/requests` (admin), `POST /api/tasks/requests/<id>/process` (admin)
- Chat: `GET /api/chat/contacts`, `GET /api/chat/messages/<contact_id>`, `POST /api/chat/send`, `GET /api/chat/recent`

WebSocket (Socket.IO):
- Khi kết nối, client truyền `token` (JWT) trong query string.
- Events:
  - Client → server: `send_message` với payload `{receiver_id, content, token}`
  - Server → receiver: `new_message`
  - Server → sender: `message_sent`

Giao diện HTML (session-based):
- Trang chính: `/`
- Trang đăng nhập: `/login` (session được set khi login qua API)
- Dashboard: `/dashboard` (render khác nhau theo role)
- Các trang quản lý: `/tasks`, `/schedules`, `/documents`, `/qna`, `/users` (admin), `/chat`...

Upload files: thư mục lưu là `uploads/` theo `UPLOAD_FOLDER`.

Notifications & Email: hệ thống tạo thông báo trong DB và gửi email dựa trên cấu hình SMTP.

Background worker: một thread daemon nội bộ (`app.utils.background_tasks.start_reminder_worker`) gửi email nhắc lịch theo `ScheduleReminder`.

---

## Kiểm thử

- Repo hiện không có test suite chính thức. Có một vài script trong `tmp/` để debug như `test_login.py`.
- Thử API bằng curl / Postman:

Ví dụ login:
```bash
curl -X POST http://127.0.0.1:7860/api/login \\
 -H "Content-Type: application/json" \\
 -d '{"username":"admin","password":"123456"}'
```

Ví dụ gọi endpoint bảo vệ:
```bash
curl -X GET http://127.0.0.1:7860/api/me \\
 -H "Authorization: Bearer <TOKEN>"
```

Nếu muốn viết test, gợi ý:
- Dùng `pytest` và Flask test client (tạo app bằng `create_app()`), cấu hình SQLite tạm thời cho test.

---

## Làm việc nhóm / Góp phần

- Fork → tạo branch feature/fix → PR.
- Tuân thủ PEP8, viết commit rõ ràng: `feat:`, `fix:`, `docs:`, `refactor:`...
- Nếu thay đổi DB, tạo migration bằng Flask-Migrate.
- Kiểm tra tính năng realtime và Redis khi thay đổi liên quan Socket.IO.

---

## Liên hệ

- Thông tin tác giả/đóng góp viên xuất hiện trong mã nguồn (ví dụ email cấu hình: `quocdatforwork@gmail.com`).
- Tạo issue trong repository nếu cần hỗ trợ hoặc muốn báo lỗi.

---

## Ghi chú ngắn về triển khai

- Mặc định app chạy port `7860` (Dockerfile & docker-compose).
- Docker Compose file có cấu hình `web`, `nginx`, `redis`, `prometheus`, `grafana`.
- Lưu ý: background worker hiện là thread nội bộ — nếu cần production scale, nên dùng giải pháp worker riêng (Celery + Redis/Kafka).

---

Nếu bạn muốn, tôi có thể:
- Commit file `README.md` vào git cho bạn.
- Thêm hướng dẫn cài đặt nhanh cho Windows/PowerShell.
- Sinh Postman collection mẫu cho các endpoint chính.
- ---
title: TaskManager
emoji: ⚡
colorFrom: blue
colorTo: green
sdk: docker
pinned: false
license: openrail
short_description: Task ManageAr
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference