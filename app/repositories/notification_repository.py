from app.repositories.base_repository import BaseRepository
from app.models.notification import Notification
from app.extensions import db


class NotificationRepository(BaseRepository):
    def __init__(self):
        super().__init__(Notification)

    def get_by_user(self, user_id, limit=50):
        return Notification.query.filter_by(user_id=user_id)\
            .order_by(Notification.created_at.desc()).limit(limit).all()

    def get_unread(self, user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False)\
            .order_by(Notification.created_at.desc()).all()

    def get_unread_count(self, user_id):
        return Notification.query.filter_by(user_id=user_id, is_read=False).count()

    def mark_as_read(self, notification_id):
        notification = self.get_by_id(notification_id)
        if notification:
            notification.is_read = True
            db.session.commit()
        return notification

    def mark_all_read(self, user_id):
        Notification.query.filter_by(user_id=user_id, is_read=False)\
            .update({'is_read': True})
        db.session.commit()

    def create_notification(self, user_id, title, message, notification_type='info', **kwargs):
        notification = Notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            **kwargs
        )
        db.session.add(notification)
        db.session.commit()
        return notification

    def create_bulk(self, user_ids, title, message, notification_type='info', **kwargs):
        notifications = []
        for uid in user_ids:
            n = Notification(
                user_id=uid, title=title, message=message,
                notification_type=notification_type, **kwargs
            )
            db.session.add(n)
            notifications.append(n)
        db.session.commit()
        return notifications
