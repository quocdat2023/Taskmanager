import sqlite3
import os

# Check common paths
paths = ["instance/task_management.db", "task_management.db", "../task_management.db"]
for db_path in paths:
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("ALTER TABLE users ADD COLUMN reminder_preference VARCHAR(100) DEFAULT '5'")
            conn.commit()
            conn.close()
            print(f"Bổ sung cột thành công cho {db_path}")
            exit(0)
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print(f"Cột đã tồn tại trong {db_path}")
                exit(0)
            print(f"Lỗi với {db_path}: {str(e)}")
print("KHÔNG tì thấy tệp database.")
