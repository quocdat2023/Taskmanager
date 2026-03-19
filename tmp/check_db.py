from app import create_app
from app.extensions import db
from app.models.user import User

app = create_app()
with app.app_context():
    try:
        user_count = User.query.count()
        print(f"User count: {user_count}")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"Admin found: {admin.username}, role: {admin.role}, is_active: {admin.is_active}")
        else:
            print("Admin NOT found!")
    except Exception as e:
        print(f"Error: {e}")
