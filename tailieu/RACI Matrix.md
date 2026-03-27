# MA TRẬN RACI - DỰ ÁN EDUTASK MANAGER

## 📋 GIỚI THIỆU
Ma trận RACI này được thiết kế dựa trên cấu trúc dự án **EduTask Manager** nhằm phân định rõ ràng trách nhiệm của từng vai trò trong dự án, đảm bảo tính minh bạch và hiệu quả vận hành.

## 👥 CÁC VAI TRÒ (ROLES)
1. **PM (Project Manager):** Quản lý tiến độ, phê duyệt yêu cầu nghiệp vụ.
2. **TL (Tech Lead):** Chịu trách nhiệm kiến trúc, giải pháp kỹ thuật và chất lượng code.
3. **BE (Backend Dev):** Phát triển API Flask, Database, Logic Socket.IO.
4. **FE (Frontend Dev):** Phát triển giao diện UI/UX, Logic Client-side.
5. **QA (Quality Assurance):** Kiểm thử chức năng, bảo mật và hiệu năng.
6. **SA (System Admin / DevOps):** Quản lý Docker, Nginx, Monitoring (Grafana/Prometheus).

## 📊 MA TRẬN RACI

| Giai đoạn / Nhiệm vụ & Sản phẩm bàn giao | PM | TL | BE | FE | QA | SA |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. KHỞI TẠO & LẬP KẾ HOẠCH** | | | | | | |
| Xác định Yêu cầu Nghiệp vụ (BRD) | **A** | **C** | **I** | **I** | **C** | **I** |
| Thiết kế Kiến trúc Hệ thống & Sơ đồ ERD | **I** | **A** | **R** | **C** | **I** | **C** |
| Phê duyệt Kế hoạch & Timeline dự án | **A** | **R** | **I** | **I** | **I** | **I** |
| **2. PHÁT TRIỂN CORE BACKEND & DB** | | | | | | |
| Thiết kế Schema Database & Migrations | **I** | **A** | **R** | **I** | **I** | **C** |
| Phát triển Module Xác thực (JWT & RBAC) | **I** | **C** | **R/A** | **I** | **I** | **I** |
| Xây dựng RESTful API cho Task & Calendar | **I** | **C** | **R/A** | **C** | **I** | **I** |
| **3. PHÁT TRIỂN FRONTEND & REAL-TIME** | | | | | | |
| Xây dựng giao diện Kanban Board & Calendar | **I** | **I** | **C** | **R/A** | **I** | **I** |
| Tích hợp Socket.IO (Chat, QnA, Notifications) | **I** | **A** | **R** | **R** | **C** | **I** |
| Tối ưu CSS/UI-UX & Responsive Design | **C** | **I** | **I** | **R/A** | **R** | **I** |
| **4. HẠ TẦNG & GIÁM SÁT (OPS)** | | | | | | |
| Cấu hình Dockerization & Orchestration | **I** | **C** | **I** | **I** | **I** | **R/A** |
| Cấu hình Nginx Reverse Proxy & SSL | **I** | **I** | **I** | **I** | **I** | **R/A** |
| Thiết lập Prometheus & Grafana Middlewares | **I** | **C** | **R** | **I** | **I** | **R/A** |
| **5. KIỂM THỬ (TESTING)** | | | | | | |
| Kiểm thử đơn vị (Unit Test) & Integration | **I** | **A** | **R** | **R** | **C** | **I** |
| Kiểm thử chấp nhận người dùng (UAT) | **A** | **C** | **I** | **I** | **R** | **I** |
| Kiểm thử Bảo mật & Hiệu năng (Load Test) | **I** | **C** | **C** | **I** | **R/A** | **C** |
| **6. TRIỂN KHAI & BÀN GIAO** | | | | | | |
| Triển khai lên Production (Deployment) | **C** | **C** | **I** | **I** | **I** | **R/A** |
| Soạn thảo Tài liệu Kỹ thuật & HDSD | **I** | **I** | **R** | **R** | **I** | **A** |

## 💡 GHI CHÚ (KEYS)
*   **R (Responsible):** Người trực tiếp thực hiện công việc.
*   **A (Accountable):** Người chịu trách nhiệm cuối cùng, có quyền phê duyệt (Chỉ 1 người/nhiệm vụ).
*   **C (Consulted):** Người cung cấp ý kiến chuyên môn, hỗ trợ thông tin.
*   **I (Informed):** Người cần được cập nhật tiến độ hoặc kết quả.

---
*📄 Tài liệu này được soạn thảo bởi Technical Writing Team – EduTask Manager v1.0*
*Ngày: 27/03/2026*
