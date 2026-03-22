import os
import shutil
import zipfile
import datetime
import time

# --- Cấu hình (Configuration) ---
# Tự động lấy path dự án để script có thể chạy từ bất cứ đâu
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_DB = os.path.join(BASE_DIR, "instance", "task_management.db")
BACKUP_DIR = os.path.join(BASE_DIR, "backups")
RETENTION_DAYS = 30  # Số ngày giữ lại bản backup

def backup_database():
    """Thực hiện sao lưu database, nén lại và xóa các bản backup cũ."""
    
    # 1. Tạo thư mục backup nếu chưa tồn tại
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"[*] Đã tạo thư mục: {BACKUP_DIR}")

    # 2. Tạo tên file backup với timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"backup_{timestamp}.db"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    zip_path = f"{backup_path}.zip"

    try:
        # 3. Kiểm tra file nguồn
        if not os.path.exists(SOURCE_DB):
            print(f"[!] Không tìm thấy file database tại: {SOURCE_DB}")
            return

        # Copy ra bản tạm thời
        shutil.copy2(SOURCE_DB, backup_path)
        
        # 4. Nén file backup lại để tiết kiệm dung lượng
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(backup_path, arcname=backup_filename)
        
        # 5. Xóa file .db tạm (chỉ giữ lại file .zip)
        os.remove(backup_path)
        
        print(f"[+] Backup thành công: {zip_path}")
        
        # 6. Dọn dẹp các bản backup cũ
        cleanup_old_backups()

    except Exception as e:
        print(f"[!] Lỗi khi thực hiện backup: {str(e)}")

def cleanup_old_backups():
    """Xóa các bản backup cũ hơn số ngày quy định."""
    now = time.time()
    retention_seconds = RETENTION_DAYS * 86400

    print(f"[*] Đang dọn dẹp các bản backup cũ hơn {RETENTION_DAYS} ngày...")
    
    for filename in os.listdir(BACKUP_DIR):
        file_path = os.path.join(BACKUP_DIR, filename)
        
        # Chỉ xét các file .zip có tiền tố backup_
        if filename.startswith("backup_") and filename.endswith(".zip"):
            file_age = os.path.getmtime(file_path)
            
            if (now - file_age) > retention_seconds:
                try:
                    os.remove(file_path)
                    print(f"[-] Đã xóa backup cũ: {filename}")
                except Exception as e:
                    print(f"[!] Lỗi khi xóa file {filename}: {str(e)}")

if __name__ == "__main__":
    backup_database()
