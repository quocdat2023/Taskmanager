from app.repositories.base_repository import BaseRepository
from app.models.user import User
from app.extensions import db


class UserRepository(BaseRepository):
    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username):
        return User.query.filter_by(username=username).first()

    def get_by_email(self, email):
        return User.query.filter_by(email=email).first()

    def get_by_role(self, role):
        return User.query.filter_by(role=role).all()

    def get_students(self):
        return User.query.filter_by(role='student', is_active=True).all()

    def get_teachers(self):
        return User.query.filter_by(role='teacher', is_active=True).all()

    def create_user(self, username, email, password, full_name, role='student', **kwargs):
        user = User(
            username=username,
            email=email,
            full_name=full_name,
            role=role,
            **kwargs
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def update_user(self, user_id, **kwargs):
        user = self.get_by_id(user_id)
        if not user:
            return None
        password = kwargs.pop('password', None)
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                setattr(user, key, value)
        if password:
            user.set_password(password)
        db.session.commit()
        return user

    def search_users(self, query_text, page=1, per_page=20):
        search = f'%{query_text}%'
        query = User.query.filter(
            db.or_(
                User.full_name.ilike(search),
                User.username.ilike(search),
                User.email.ilike(search),
                User.student_id.ilike(search)
            )
        )
        return query.paginate(page=page, per_page=per_page, error_out=False)
