from app import create_app
from app.extensions import db
from sqlalchemy import inspect

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    print("Tables in database:", tables)
    if 'task_history' in tables and 'task_requests' in tables:
        print("Success: New tables found.")
    else:
        print("Error: Missing tables!")
