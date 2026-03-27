from app import create_app
from app.extensions import db
from sqlalchemy import text

def upgrade_db():
    app = create_app()
    with app.app_context():
        # Check if columns exist and add them if not
        inspector = db.inspect(db.engine)
        columns = [c['name'] for c in inspector.get_columns('tasks')]
        
        if 'progress' not in columns:
            db.session.execute(text('ALTER TABLE tasks ADD COLUMN progress INTEGER DEFAULT 0'))
            print("Added progress column to tasks")
        
        if 'estimated_time' not in columns:
            db.session.execute(text('ALTER TABLE tasks ADD COLUMN estimated_time VARCHAR(50)'))
            print("Added estimated_time column to tasks")
            
        if 'actual_time' not in columns:
            db.session.execute(text('ALTER TABLE tasks ADD COLUMN actual_time VARCHAR(50)'))
            print("Added actual_time column to tasks")

        # Check users table
        user_columns = [c['name'] for c in inspector.get_columns('users')]
        if 'is_approved' not in user_columns:
            db.session.execute(text('ALTER TABLE users ADD COLUMN is_approved BOOLEAN DEFAULT 0'))
            print("Added is_approved column to users")
            
        # Create new tables
        db.create_all()
        print("Ensured all tables are created")
        
        db.session.commit()
        print("Database upgrade successful")

if __name__ == "__main__":
    upgrade_db()
