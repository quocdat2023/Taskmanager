from app.extensions import db
from datetime import datetime


class Question(db.Model):
    __tablename__ = 'questions'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    course_name = db.Column(db.String(150), nullable=True)
    course_code = db.Column(db.String(20), nullable=True)
    asked_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_resolved = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    answers = db.relationship('Answer', backref='question', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'course_name': self.course_name,
            'course_code': self.course_code,
            'asked_by': self.asked_by,
            'asker_name': self.asker.full_name if self.asker else None,
            'asker_role': self.asker.role if self.asker else None,
            'is_resolved': self.is_resolved,
            'answers_count': self.answers.count(),
            'answers': [a.to_dict() for a in self.answers.order_by(Answer.created_at.asc())],
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Question {self.title}>'


class Answer(db.Model):
    __tablename__ = 'answers'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'), nullable=False)
    answered_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'content': self.content,
            'question_id': self.question_id,
            'answered_by': self.answered_by,
            'answerer_name': self.answerer.full_name if self.answerer else None,
            'answerer_role': self.answerer.role if self.answerer else None,
            'is_accepted': self.is_accepted,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<Answer {self.id}>'
