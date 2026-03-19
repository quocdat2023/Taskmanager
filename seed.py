import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.task import Task, TaskAssignment
from app.models.schedule import Schedule
from app.models.document import Document
from app.models.qna import Question, Answer

app = create_app()

def seed_data():
    with app.app_context():
        # Clean current DB
        db.drop_all()
        db.create_all()

        print("=== Seeding Data ===")
        # 1. Create Users
        admin_pass = generate_password_hash('123456')
        user_pass = generate_password_hash('123456')
        
        admin = User(username='admin', email='admin@edutask.com', password_hash=admin_pass, full_name='Quản Trị Viên', role='admin')
        gv1 = User(username='gv1', email='gv1@edutask.com', password_hash=user_pass, full_name='Giảng Viên A', role='teacher', department='CNTT')
        gv2 = User(username='gv2', email='gv2@edutask.com', password_hash=user_pass, full_name='Giảng Viên B', role='teacher', department='Kinh Tế')
        
        sv1 = User(username='sv1', email='sv1@edutask.com', password_hash=user_pass, full_name='Sinh Viên 1', role='student', student_id='SV001', department='CNTT')
        sv2 = User(username='sv2', email='sv2@edutask.com', password_hash=user_pass, full_name='Sinh Viên 2', role='student', student_id='SV002', department='CNTT')
        sv3 = User(username='sv3', email='sv3@edutask.com', password_hash=user_pass, full_name='Sinh Viên 3', role='student', student_id='SV003', department='Kinh Tế')
        
        db.session.add_all([admin, gv1, gv2, sv1, sv2, sv3])
        db.session.commit()
        print("✓ Created 1 Admin, 2 Teachers, 3 Students")

        # 2. Create Tasks (Assigned to Students AND Teachers)
        now = datetime.utcnow()
        task1 = Task(
            title='Chấm bài giữa kỳ Cấu trúc dữ liệu',
            description='Đề nghị thầy cô chấm xong trước cuối tuần',
            status='todo', priority='high',
            due_date=now + timedelta(days=5),
            course_name='Cấu trúc dữ liệu',
            course_code='CTDL01',
            class_group='N01',
            semester='HK1',
            academic_year='2024-2025',
            created_by=admin.id
        )
        task2 = Task(
            title='Làm bài tập nhóm Project Flask',
            description='Dựng REST API bằng Flask và SQLite',
            status='in_progress', priority='urgent',
            due_date=now + timedelta(days=2),
            course_name='Lập trình Web',
            course_code='WEB101',
            semester='HK2',
            academic_year='2023-2024',
            created_by=gv1.id
        )
        db.session.add_all([task1, task2])
        db.session.commit()

        # Assignments
        # Admin giao việc cho Giảng Viên A (gv1)
        db.session.add(TaskAssignment(task_id=task1.id, user_id=gv1.id))
        # Admin giao việc cho Giảng Viên B (gv2)
        db.session.add(TaskAssignment(task_id=task2.id, user_id=gv2.id, status='in_progress'))
        db.session.commit()
        print("✓ Created Tasks for Teachers (Students removed from tasks)")

        # 3. Create Schedules
        s1 = Schedule(
            title='Họp bộ môn CNTT',
            description='Thảo luận đề thi cuối kỳ',
            event_type='meeting',
            start_time=now + timedelta(days=1, hours=9),
            end_time=now + timedelta(days=1, hours=11),
            location='Phòng 301',
            created_by=admin.id,
            color='#e74c3c'
        )
        s2 = Schedule(
            title='Học bù Lập trình Web',
            event_type='class',
            start_time=now + timedelta(days=2, hours=13),
            end_time=now + timedelta(days=2, hours=16),
            course_name='Lập trình Web',
            location='Lab 02',
            created_by=gv1.id,
            color='#3498db'
        )
        db.session.add_all([s1, s2])
        db.session.commit()
        print("✓ Created Schedules")

        # 4. Create Documents
        doc1 = Document(
            title='Slide bài giảng Flask API',
            file_path='uploads/slide_flask.pdf',
            file_name='slide_flask.pdf',
            file_type='pdf',
            file_size=1024000,
            course_name='Lập trình Web',
            uploaded_by=gv1.id
        )
        db.session.add(doc1)
        db.session.commit()
        print("✓ Created Documents")

        # 5. Create Q&A
        q1 = Question(
            title='Lỗi ImportError Flask-SQLAlchemy',
            content='Em chạy pip install nhưng bị báo sqlalchemy no attribute __all__? Giúp em với.',
            course_name='Lập trình Web',
            asked_by=sv1.id
        )
        db.session.add(q1)
        db.session.commit()

        ans1 = Answer(
            content='Đây là lỗi phiên bản cũ, em upgrade thư viện bằng requirements.txt nhé.',
            question_id=q1.id,
            answered_by=gv1.id
        )
        db.session.add(ans1)
        
        # Resolve it
        q1.is_resolved = True
        db.session.commit()
        print("✓ Created Q&A threads")
        
        print("=== Database Seeded Successfully! ===")
        print("Accounts: admin (123456) | gv1 (123456) | sv1 (123456)")

if __name__ == '__main__':
    seed_data()
