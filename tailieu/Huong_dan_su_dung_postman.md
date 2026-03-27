# 📖 Hướng Dẫn Sử Dụng Postman Collection - EduTask Manager

## 📁 Các file đã tạo

| File | Mục đích |
|------|----------|
| `EduTask_Manager_API_Collection.postman_collection.json` | Bộ test 79 API endpoints |
| `EduTask_Dev.postman_environment.json` | Biến môi trường Development |
| `EduTask_Staging.postman_environment.json` | Biến môi trường Staging |
| `EduTask_Production.postman_environment.json` | Biến môi trường Production |

---

## Bước 1: Mở Postman và Import Collection

1. Mở ứng dụng **Postman** (tải tại [postman.com/downloads](https://www.postman.com/downloads/) nếu chưa có)
2. Click nút **Import** ở góc trên bên trái

   ![Import button location](https://learning.postman.com/docs/img/import-export-import-ui-v10-2.jpg)

3. Kéo thả file `EduTask_Manager_API_Collection.postman_collection.json` vào cửa sổ Import
4. Click **Import** để xác nhận

> [!TIP]
> Bạn cũng có thể vào **File → Import** hoặc dùng phím tắt `Ctrl + O`

---

## Bước 2: Import Environment

1. Click **Import** lần nữa
2. Kéo thả file `EduTask_Dev.postman_environment.json` vào
3. Click **Import**
4. **Chọn environment**: Ở góc trên bên phải, click dropdown environment và chọn **"EduTask Manager - Development"**

> [!IMPORTANT]
> Nếu không chọn environment, biến `{{base_url}}` sẽ không có giá trị và các request sẽ lỗi!

---

## Bước 3: Khởi động Server

Trước khi test, đảm bảo server đang chạy:

```bash
# Cách 1: Chạy trực tiếp
cd c:\Users\quocd\Documents\Task2
python run.py

# Cách 2: Dùng Docker
docker-compose up -d
```

Server sẽ chạy tại `http://localhost:7860`

---

## Bước 4: Chạy Từng Request (Manual Testing)

### 4.1 — Đăng nhập trước tiên

1. Mở sidebar trái → Expand thư mục **"01. Authentication & User Profile"**
2. Click vào **"Login as Admin"**
3. Kiểm tra tab **Body** — đã có sẵn username/password:
   ```json
   {
     "username": "admin",
     "password": "123456"
   }
   ```
4. Click nút **Send** (màu xanh)
5. Xem kết quả ở panel dưới:
   - Tab **Body**: Response JSON chứa `token`
   - Tab **Test Results**: Hiện các test đã pass ✅

> [!NOTE]
> Sau khi Login thành công, token sẽ **tự động được lưu** vào biến `{{auth_token}}` và `{{admin_token}}`. Mọi request sau đó sẽ tự dùng token này.

### 4.2 — Test các API khác

Sau khi login, bạn có thể test bất kỳ request nào:

1. Mở thư mục module muốn test (ví dụ **"04. Task Management"**)
2. Click request (ví dụ **"Create Task (Admin)"**)
3. Kiểm tra:
   - **Headers**: Đã có `Authorization: Bearer {{admin_token}}` tự động
   - **Body**: Dữ liệu mẫu sẵn sàng
4. Click **Send**
5. Xem tab **Test Results** để kiểm tra kết quả

---

## Bước 5: Chạy Toàn Bộ Test Suite (Automated)

Đây là cách mạnh nhất — chạy tất cả 79 request tự động theo thứ tự:

### 5.1 — Chạy Collection Runner

1. Click chuột phải vào collection **"EduTask Manager - Complete API Test Suite"** ở sidebar
2. Chọn **"Run collection"**
3. Trong cửa sổ Runner:
   - **Order**: Giữ nguyên thứ tự (quan trọng vì các request phụ thuộc nhau)
   - **Delay**: Đặt `200ms` giữa các request
   - **Iterations**: `1` (hoặc nhiều hơn nếu muốn stress test)
4. Click **"Run EduTask Manager..."**

### 5.2 — Đọc kết quả

Sau khi chạy xong, bạn sẽ thấy:

```
✅ Pass: 75 tests
❌ Fail: 2 tests  
⏭ Skip: 0 tests

Total run duration: ~15s
```

- **Xanh ✅** = Test pass
- **Đỏ ❌** = Test fail (click vào để xem lý do)
- Click từng request để xem chi tiết response

---

## Bước 6: Kiểm Tra Biến (Variables)

### Xem Collection Variables:

1. Click vào tên collection ở sidebar
2. Chọn tab **"Variables"**
3. Bạn sẽ thấy 26 biến như `auth_token`, `task_id`, `question_id`...
4. Sau khi chạy, các biến sẽ được tự động điền giá trị

### Xem Environment Variables:

1. Click icon **👁 (Eye)** ở góc trên phải
2. Hoặc click **Environments** ở sidebar trái → chọn "EduTask Manager - Development"
3. Có thể sửa `base_url` nếu server chạy ở port/URL khác

---

## Bước 7: Chạy Từ Command Line (Newman — CI/CD)

### Cài Newman:
```bash
npm install -g newman
npm install -g newman-reporter-htmlextra
```

### Chạy test:
```bash
cd c:\Users\quocd\Documents\Task2

# Chạy cơ bản (output trên terminal)
newman run EduTask_Manager_API_Collection.postman_collection.json ^
  -e EduTask_Dev.postman_environment.json

# Chạy với HTML report
newman run EduTask_Manager_API_Collection.postman_collection.json ^
  -e EduTask_Dev.postman_environment.json ^
  --reporters cli,htmlextra ^
  --reporter-htmlextra-export ./test-report.html
```

### Kết quả sẽ hiện:
```
┌─────────────────────────┬──────────┬──────────┐
│                         │ executed │   failed │
├─────────────────────────┼──────────┼──────────┤
│              iterations │        1 │        0 │
│                requests │       79 │        0 │
│            test-scripts │      158 │        0 │
│      prerequest-scripts │       79 │        0 │
│              assertions │      200+│        0 │
├─────────────────────────┼──────────┼──────────┤
│          total run time │    ~25s  │          │
└─────────────────────────┴──────────┴──────────┘
```

---

## 💡 Mẹo Sử Dụng

### Thứ tự chạy đúng (nếu test thủ công):

```
1. Login as Admin       → lấy admin_token
2. Login as Teacher     → lấy teacher_token  
3. Login as Student     → lấy student_token
4. Rồi test bất kỳ module nào
```

### Test 1 module cụ thể:

1. Chuột phải vào **thư mục** module (ví dụ "04. Task Management")
2. Chọn **"Run folder"**
3. Chỉ các request trong folder đó sẽ chạy

> [!WARNING]
> Nhớ chạy **Login** trước khi chạy bất kỳ folder nào, vì mọi request đều cần `auth_token`!

### Đổi môi trường (Dev → Staging → Production):

1. Import thêm file `EduTask_Staging.postman_environment.json`
2. Chuyển dropdown environment sang **"EduTask Manager - Staging"**
3. Tất cả request sẽ tự chuyển sang URL staging

---

## 🔍 Cấu Trúc Mỗi Request

Mỗi request đã được cấu hình sẵn:

| Tab | Nội dung |
|-----|----------|
| **Headers** | `Authorization: Bearer {{auth_token}}` + `Content-Type: application/json` |
| **Body** | Dữ liệu JSON mẫu thực tế |
| **Tests** | Script kiểm tra status code, schema, business logic |
| **Pre-request** | Auto-set variables khi cần |

Ví dụ tab **Tests** của "Create Task":
```javascript
pm.test("Status code is 201", function () { 
    pm.response.to.have.status(201); 
});
pm.test("Response is JSON", function () { 
    pm.response.to.be.json; 
});
pm.test("Has task", function () { 
    var d = pm.response.json(); 
    pm.expect(d).to.have.property("task"); 
});
// Tự lưu task_id cho request tiếp theo
var d = pm.response.json(); 
pm.collectionVariables.set("task_id", d.task.id);
```
