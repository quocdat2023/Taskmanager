from app.repositories.chat_repository import ChatRepository
from app.repositories.user_repository import UserRepository

class ChatService:
    def __init__(self):
        self.chat_repo = ChatRepository()
        self.user_repo = UserRepository()

    def send_message(self, sender_id, receiver_id, content):
        if not content or str(content).strip() == '':
            return None
        return self.chat_repo.create_message(sender_id, receiver_id, content)

    def get_conversation(self, user1_id, user2_id, limit=50, offset=0):
        # We also want to mark them as read when we GET the conversation
        # IF user1_id is the receiver of the last message(s) from user2_id
        self.chat_repo.mark_as_read(user2_id, user1_id)
        return self.chat_repo.get_conversation(user1_id, user2_id, limit, offset)

    def get_contacts(self, user_id):
        # Return a list of users that can be chatted with
        # Based on rules:
        # Teachers can chat with Teachers and Students
        # Students can chat with Teachers
        # Admin can chat with anyone
        
        user = self.user_repo.get_by_id(user_id)
        all_users = self.user_repo.get_all()
        
        # Filter based on roles
        if user.role == 'admin':
            return [u for u in all_users if u.id != user_id]
        elif user.role == 'teacher':
            # Teachers can chat with everyone except maybe other students who are not in their classes?
            # For simplicity, let's allow all Teachers & Students
            return [u for u in all_users if u.id != user_id and u.role in ('teacher', 'student', 'admin')]
        elif user.role == 'student':
            # Students can chat with Teachers and Admin, NOT other students (per request "giữa sinh viên với giảng viên và ngược lại")
            # "giữa các giảng viên với nhau" -> teacher-teacher
            # "sinh viên với giảng viên" -> student-teacher
            return [u for u in all_users if u.id != user_id and u.role in ('teacher', 'admin')]
            
        return []

    def get_recent_conversations(self, user_id):
        return self.chat_repo.get_last_messages(user_id)
