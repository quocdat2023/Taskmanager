import sqlite3
import os

db_path = r'c:\Users\quocd\Documents\Task2 - ok\instance\task_management.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'last_login' not in columns:
        print("Adding 'last_login' column to 'users' table...")
        cursor.execute("ALTER TABLE users ADD COLUMN last_login DATETIME")
        conn.commit()
        print("Successfully added column.")
    else:
        print("'last_login' column already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    exit(1)
