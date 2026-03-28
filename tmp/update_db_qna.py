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
    cursor.execute("PRAGMA table_info(answers)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if 'parent_id' not in columns:
        print("Adding 'parent_id' column to 'answers' table...")
        cursor.execute("ALTER TABLE answers ADD COLUMN parent_id INTEGER REFERENCES answers(id)")
        conn.commit()
        print("Successfully added column.")
    else:
        print("'parent_id' column already exists.")
        
    conn.close()
except Exception as e:
    print(f"Error: {e}")
    exit(1)
