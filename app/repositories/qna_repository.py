from app.repositories.base_repository import BaseRepository
from app.models.qna import Question, Answer
from app.extensions import db
from sqlalchemy import or_


class QnARepository(BaseRepository):
    def __init__(self):
        super().__init__(Question)

    def get_questions_by_user(self, user_id):
        return Question.query.filter_by(asked_by=user_id).order_by(Question.created_at.desc()).all()

    def get_questions_by_course(self, course_code):
        return Question.query.filter_by(course_code=course_code).order_by(Question.created_at.desc()).all()

    def get_unresolved_questions(self):
        return Question.query.filter_by(is_resolved=False).order_by(Question.created_at.desc()).all()

    def get_all_questions(self):
        return Question.query.order_by(Question.created_at.desc()).all()

    def get_questions_paginated(self, page=1, per_page=10, search=None):
        query = Question.query
        if search:
            query = query.filter(
                or_(
                    Question.title.ilike(f'%{search}%'),
                    Question.content.ilike(f'%{search}%')
                )
            )
        return query.order_by(Question.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)

    def create_question(self, title, content, asked_by, **kwargs):
        question = Question(
            title=title,
            content=content,
            asked_by=asked_by,
            **kwargs
        )
        db.session.add(question)
        db.session.commit()
        return question

    def create_answer(self, content, question_id, answered_by, parent_id=None):
        answer = Answer(
            content=content,
            question_id=question_id,
            answered_by=answered_by,
            parent_id=parent_id
        )
        db.session.add(answer)
        db.session.commit()
        return answer

    def delete_answer(self, answer_id):
        answer = Answer.query.get(answer_id)
        if answer:
            db.session.delete(answer)
            db.session.commit()
            return True
        return False

    def mark_resolved(self, question_id):
        question = self.get_by_id(question_id)
        if question:
            question.is_resolved = True
            db.session.commit()
        return question

    def accept_answer(self, answer_id):
        answer = Answer.query.get(answer_id)
        if answer:
            answer.is_accepted = True
            db.session.commit()
        return answer

    def get_answer_by_id(self, answer_id):
        return Answer.query.get(answer_id)
