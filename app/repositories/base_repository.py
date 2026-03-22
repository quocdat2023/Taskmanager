from app.extensions import db


class BaseRepository:
    """Base repository providing common CRUD operations."""

    def __init__(self, model):
        self.model = model

    def get_all(self):
        return self.model.query.all()

    def get_by_id(self, id):
        return self.model.query.get(id)

    def get_paginated(self, page=1, per_page=20, **filters):
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.paginate(page=page, per_page=per_page, error_out=False)

    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

    def update(self, id, **kwargs):
        instance = self.get_by_id(id)
        if instance:
            for key, value in kwargs.items():
                if hasattr(instance, key):
                    setattr(instance, key, value)
            db.session.commit()
        return instance

    def delete(self, id):
        instance = self.get_by_id(id)
        if instance:
            try:
                db.session.delete(instance)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollback()
                print(f"Error in {self.model.__name__} repository delete: {str(e)}")
                raise e
        return False

    def count(self, **filters):
        query = self.model.query
        for key, value in filters.items():
            if hasattr(self.model, key) and value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.count()
