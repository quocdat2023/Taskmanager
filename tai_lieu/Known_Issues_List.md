# DANH SÁCH VẤN ĐỀ ĐÃ BIẾT (KNOWN ISSUES LIST)

**EduTask Manager – Hệ thống Quản lý Học vụ và Nhiệm vụ Trực tuyến**  
**Phiên bản:** v1.0  
**Ngày phát hành:** 27 tháng 3, 2026  

---

## TÓM TẮT TÌNH TRẠNG ỔN ĐỊNH HỆ THỐNG

Hệ thống EduTask Manager v1.0 đã đạt được mức độ ổn định cao với tỷ lệ thành công kiểm tra là 89.2%. Tất cả các vấn đề được liệt kê dưới đây đều ở mức độ thấp hoặc trung bình, không ảnh hưởng đến khả năng sử dụng cốt lõi của hệ thống. Người dùng có thể tiếp tục hoạt động bình thường trong khi các vấn đề này được khắc phục trong các phiên bản cập nhật sắp tới.

---

## VẤN ĐỀ THEO MODULE

### 1. XÁC THỰC & QUẢN LÝ NGƯỜI DÙNG

| ID Vấn đề | Mô tả | Mức độ | Tác động | Giải pháp Tạm thời | Kế hoạch Khắc phục |
|-----------|--------|---------|----------|-------------------|-------------------|
| FAIL-007 | Thời gian khóa tài khoản sau nhiều lần thử đăng nhập thất bại là 10 phút thay vì 15 phút theo cấu hình | Trung bình | Người dùng bị khóa có thể thử lại sớm hơn 5 phút, không ảnh hưởng nghiêm trọng đến bảo mật | Chờ thời gian khóa tự động hết hoặc liên hệ quản trị viên để reset | Cập nhật cấu hình bảo mật trong phiên bản 1.1 (Tháng 6/2026) |

### 2. GÁN NHIỆM VỤ & PHÊ DUYỆT

| ID Vấn đề | Mô tả | Mức độ | Tác động | Giải pháp Tạm thời | Kế hoạch Khắc phục |
|-----------|--------|---------|----------|-------------------|-------------------|
| FAIL-003 | Không hỗ trợ phê duyệt một phần cho các yêu cầu gán nhiệm vụ (chỉ có thể phê duyệt toàn bộ hoặc từ chối toàn bộ) | Trung bình | Người phê duyệt phải xử lý từng yêu cầu riêng biệt thay vì chọn lọc, gây bất tiện nhỏ | Phê duyệt từng yêu cầu riêng lẻ hoặc từ chối toàn bộ và tạo lại yêu cầu mới | Thêm giao diện phê duyệt chọn lọc trong phiên bản 1.1 (Tháng 6/2026) |

### 3. QUẢN LÝ LỊCH BIỂU & HỌC KỲ

| ID Vấn đề | Mô tả | Mức độ | Tác động | Giải pháp Tạm thời | Kế hoạch Khắc phục |
|-----------|--------|---------|----------|-------------------|-------------------|
| FAIL-004 | Không phát hiện xung đột khi đặt lịch trùng lặp thời gian và địa điểm | Trung bình | Có thể xảy ra đặt phòng trùng lặp, yêu cầu kiểm tra thủ công hoặc điều chỉnh lịch | Kiểm tra lịch trước khi đặt hoặc liên hệ quản trị viên để điều chỉnh | Thêm logic phát hiện xung đột trong phiên bản 1.1 (Tháng 6/2026) |

### 4. Q&A & THẢO LUẬN

| ID Vấn đề | Mô tả | Mức độ | Tác động | Giải pháp Tạm thời | Kế hoạch Khắc phục |
|-----------|--------|---------|----------|-------------------|-------------------|
| FAIL-009 | Cho phép đánh dấu nhiều câu trả lời là "được chấp nhận" cho cùng một câu hỏi (thay vì chỉ một câu trả lời duy nhất) | Trung bình | Người dùng có thể nhầm lẫn về câu trả lời chính thức, gây hiểu lầm nhỏ | Tham khảo các câu trả lời được đánh dấu hoặc liên hệ người hỏi để xác nhận | Thêm ràng buộc chỉ cho phép một câu trả lời được chấp nhận trong phiên bản 1.1 (Tháng 6/2026) |

### 5. QUẢN LÝ TÀI LIỆU

| ID Vấn đề | Mô tả | Mức độ | Tác động | Giải pháp Tạm thời | Kế hoạch Khắc phục |
|-----------|--------|---------|----------|-------------------|-------------------|
| FAIL-010 | Không hỗ trợ tải lên tài liệu hàng loạt (chỉ có thể tải từng tệp một) | Thấp | Giáo viên phải tải từng tài liệu riêng biệt, tốn thời gian với nhiều tệp | Tải lên từng tệp hoặc sử dụng công cụ bên ngoài để nén và tải lên | Thêm tính năng tải lên hàng loạt trong phiên bản 1.1 (Tháng 6/2026) |

---

## GHI CHÚ QUAN TRỌNG

- **Tất cả vấn đề đều không ảnh hưởng đến chức năng cốt lõi** của hệ thống. Người dùng có thể tiếp tục sử dụng EduTask Manager bình thường.
- **Hỗ trợ kỹ thuật** sẽ được cung cấp 24/7 trong 30 ngày đầu sau khi phát hành để xử lý bất kỳ vấn đề nào phát sinh.
- **Các bản cập nhật** sẽ được triển khai theo kế hoạch để khắc phục các vấn đề này, với phiên bản 1.1 dự kiến vào tháng 6/2026.
- Để được hỗ trợ, vui lòng liên hệ đội ngũ kỹ thuật qua email hoặc hotline được cung cấp trong tài liệu hướng dẫn sử dụng.

---

*Tài liệu này được cập nhật lần cuối vào ngày 27 tháng 3, 2026 và phản ánh tình trạng của phiên bản v1.0. Các vấn đề có thể được khắc phục trong các phiên bản cập nhật mà không cần thông báo trước.*