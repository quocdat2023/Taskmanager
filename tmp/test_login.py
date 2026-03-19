from app import create_app
from app.services.user_service import UserService

app = create_app()
with app.app_context():
    service = UserService()
    user, token, error = service.login('admin', '123456')
    if error:
        print(f"Login failed: {error}")
    else:
        print(f"Login success! Token: {token[:20]}...")
        print(f"User: {user.username}, role: {user.role}")
