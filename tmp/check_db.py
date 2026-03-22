from app import create_app
from app.models.user import User

app = create_app()
with app.app_context():
    count = User.query.count()
    print(f"User count: {count}")
    if count > 0:
        admin = User.query.filter_by(username='admin').first()
        print(f"Admin found: {admin.full_name if admin else 'No'}")
