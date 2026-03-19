from app.repositories.notification_repository import NotificationRepository
from flask_mail import Message
from app.extensions import mail
from flask import current_app


class NotificationService:
    def __init__(self):
        self.repo = NotificationRepository()

    def get_notifications(self, user_id, limit=50):
        return self.repo.get_by_user(user_id, limit)

    def get_unread(self, user_id):
        return self.repo.get_unread(user_id)

    def get_unread_count(self, user_id):
        return self.repo.get_unread_count(user_id)

    def mark_as_read(self, notification_id):
        return self.repo.mark_as_read(notification_id)

    def mark_all_read(self, user_id):
        self.repo.mark_all_read(user_id)

    def create_notification(self, user_id, title, message, notification_type='info', **kwargs):
        return self.repo.create_notification(
            user_id=user_id,
            title=title,
            message=message,
            notification_type=notification_type,
            **kwargs
        )

    def send_email_notification(self, to_email, subject, body):
        """Send an email notification. Fails silently if mail is not configured."""
        try:
            if not current_app.config.get('MAIL_USERNAME'):
                return False
            msg = Message(
                subject=subject,
                recipients=[to_email],
                body=body,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            mail.send(msg)
            return True
        except Exception as e:
            current_app.logger.error(f'Email send error: {e}')
            return False

    def notify_and_email(self, user, title, message, notification_type='info', **kwargs):
        """Create in-app notification and send email."""
        notification = self.create_notification(
            user_id=user.id,
            title=title,
            message=message,
            notification_type=notification_type,
            **kwargs
        )

        email_sent = self.send_email_notification(user.email, title, message)
        if email_sent:
            notification.is_email_sent = True
            from app.extensions import db
            db.session.commit()

        return notification
