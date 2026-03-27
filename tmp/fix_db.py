import sqlite3
import os

def migrate(db_path):
    print(f"Checking database: {db_path}")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if task_comments table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='task_comments'")
        if not cursor.fetchone():
            print(f"Skipping {db_path}: task_comments table not found.")
            conn.close()
            return

        # Try to add parent_id column
        try:
            cursor.execute('ALTER TABLE task_comments ADD COLUMN parent_id INTEGER REFERENCES task_comments(id)')
            print(f"Successfully added parent_id to task_comments in {db_path}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"Column parent_id already exists in {db_path}")
            else:
                print(f"Error migrating {db_path}: {e}")
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error processing {db_path}: {e}")

def run():
    # Find all .db files
    db_files = []
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.db'):
                db_files.append(os.path.join(root, file))
    
    if not db_files:
        print("No .db files found.")
        return

    for db_path in db_files:
        migrate(db_path)

if __name__ == "__main__":
    run()
