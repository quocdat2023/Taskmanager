from app.repositories.user_repository import UserRepository
from flask_jwt_extended import create_access_token


class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def register(self, username, email, password, full_name, role='student', **kwargs):
        # Check if user already exists
        if self.repo.get_by_username(username):
            return None, 'Username already exists'
        if self.repo.get_by_email(email):
            return None, 'Email already exists'

        user = self.repo.create_user(
            username=username,
            email=email,
            password=password,
            full_name=full_name,
            role=role,
            **kwargs
        )
        return user, None

    def login(self, username, password):
        user = self.repo.get_by_username(username)
        if not user:
            user = self.repo.get_by_email(username)

        if not user or not user.check_password(password):
            return None, None, 'Invalid credentials'

        if not user.is_active:
            return None, None, 'Account is deactivated'

        token = create_access_token(
            identity=user.id,
            additional_claims={
                'role': user.role,
                'username': user.username,
                'full_name': user.full_name
            }
        )
        return user, token, None

    def get_user(self, user_id):
        return self.repo.get_by_id(user_id)

    def get_all_users(self, page=1, per_page=20):
        return self.repo.get_paginated(page=page, per_page=per_page)

    def get_students(self):
        return self.repo.get_students()

    def get_teachers(self):
        return self.repo.get_teachers()

    def update_user(self, user_id, **kwargs):
        return self.repo.update_user(user_id, **kwargs)

    def delete_user(self, user_id):
        return self.repo.delete(user_id)

    def search_users(self, query, page=1, per_page=20):
        return self.repo.search_users(query, page=page, per_page=per_page)

    def toggle_active(self, user_id):
        user = self.repo.get_by_id(user_id)
        if user:
            user.is_active = not user.is_active
            from app.extensions import db
            db.session.commit()
        return user
