from app.models.chat import ChatMessage
from app.extensions import db
from sqlalchemy import or_, and_
from datetime import datetime

class ChatRepository:
    def create_message(self, sender_id, receiver_id, content):
        message = ChatMessage(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()
        return message

    def get_conversation(self, user1_id, user2_id, limit=50, offset=0):
        # Retrieve messages between user1 and user2
        return ChatMessage.query.filter(
            or_(
                and_(ChatMessage.sender_id == user1_id, ChatMessage.receiver_id == user2_id),
                and_(ChatMessage.sender_id == user2_id, ChatMessage.receiver_id == user1_id)
            )
        ).order_by(ChatMessage.created_at.asc()).limit(limit).offset(offset).all()

    def mark_as_read(self, sender_id, receiver_id):
        # Mark all messages SENT BY sender_id TO receiver_id as read
        ChatMessage.query.filter_by(sender_id=sender_id, receiver_id=receiver_id, is_read=False).update({'is_read': True})
        db.session.commit()

    def get_unread_count(self, user_id):
        return ChatMessage.query.filter_by(receiver_id=user_id, is_read=False).count()

    def get_last_messages(self, user_id):
        # Get the latest message for each unique conversation of user_id
        # This is complex in SQLite without analytics window functions, so we'll do it efficiently
        from sqlalchemy import func
        # Find all users who have exchanged messages with user_id
        subq = db.session.query(
            func.max(ChatMessage.id).label('max_id')
        ).filter(
            or_(ChatMessage.sender_id == user_id, ChatMessage.receiver_id == user_id)
        ).group_by(
            # Group by the OTHER user ID
            func.case(
                [(ChatMessage.sender_id == user_id, ChatMessage.receiver_id)],
                else_=ChatMessage.sender_id
            )
        ).subquery()

        return ChatMessage.query.join(subq, ChatMessage.id == subq.c.max_id).order_by(ChatMessage.created_at.desc()).all()

    def cleanup_old_messages(self, days=14):
        from datetime import timedelta
        cutoff = datetime.utcnow() - timedelta(days=days)
        deleted = ChatMessage.query.filter(ChatMessage.created_at < cutoff).delete()
        db.session.commit()
        return deleted
