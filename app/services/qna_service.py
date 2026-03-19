from app.repositories.qna_repository import QnARepository
from app.repositories.notification_repository import NotificationRepository


class QnAService:
    def __init__(self):
        self.repo = QnARepository()
        self.notification_repo = NotificationRepository()

    def create_question(self, title, content, asked_by, **kwargs):
        question = self.repo.create_question(
            title=title,
            content=content,
            asked_by=asked_by,
            **kwargs
        )
        return question

    def create_answer(self, content, question_id, answered_by):
        answer = self.repo.create_answer(
            content=content,
            question_id=question_id,
            answered_by=answered_by
        )

        # Notify question asker
        question = self.repo.get_by_id(question_id)
        if question and question.asked_by != answered_by:
            self.notification_repo.create_notification(
                user_id=question.asked_by,
                title='Câu trả lời mới',
                message=f'Câu hỏi "{question.title}" đã có câu trả lời mới',
                notification_type='qna',
                reference_type='question',
                reference_id=question.id
            )

        return answer

    def get_question(self, question_id):
        return self.repo.get_by_id(question_id)

    def get_all_questions(self):
        return self.repo.get_all_questions()

    def get_questions_by_user(self, user_id):
        return self.repo.get_questions_by_user(user_id)

    def get_unresolved_questions(self):
        return self.repo.get_unresolved_questions()

    def mark_resolved(self, question_id):
        return self.repo.mark_resolved(question_id)

    def accept_answer(self, answer_id):
        return self.repo.accept_answer(answer_id)

    def delete_question(self, question_id):
        return self.repo.delete(question_id)
