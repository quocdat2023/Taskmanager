import os
from flask import Flask
from app.config import config
from app.extensions import db, jwt, mail, cors, migrate, socketio

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_CONFIG', 'default')

    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'templates'),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    )
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    cors.init_app(app)
    migrate.init_app(app, db)
    # Initialize Prometheus Metrics
    from prometheus_flask_exporter import PrometheusMetrics
    metrics = PrometheusMetrics(app)

    # Initialize SocketIO with Redis if available
    message_queue = os.environ.get('REDIS_URL')
    if message_queue:
        socketio.init_app(app, message_queue=message_queue)
    else:
        socketio.init_app(app)

    # Ensure upload folder exists
    os.makedirs(app.config.get('UPLOAD_FOLDER', 'uploads'), exist_ok=True)

    # Import models/handlers to register them
    from app.models import User, Task, TaskAssignment, Schedule, ScheduleReminder, Document, Question, Answer, Notification, AcademicYear
    from app.models.chat import ChatMessage
    from app.utils import socket_handlers

    # Register blueprints - API
    from app.controllers.auth_controller import auth_bp
    from app.controllers.task_controller import task_bp
    from app.controllers.schedule_controller import schedule_bp
    from app.controllers.document_controller import document_bp
    from app.controllers.qna_controller import qna_bp
    from app.controllers.notification_controller import notification_bp
    from app.controllers.user_management_controller import user_manage_bp
    from app.controllers.reminder_controller import reminder_bp
    from app.controllers.academic_year_controller import academic_year_bp
    from app.controllers.chat_controller import chat_bp
    from werkzeug.security import generate_password_hash

    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(schedule_bp)
    app.register_blueprint(document_bp)
    app.register_blueprint(qna_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(user_manage_bp)
    app.register_blueprint(reminder_bp)
    app.register_blueprint(academic_year_bp)
    app.register_blueprint(chat_bp)

    # Register blueprints - Pages
    from app.views.page_views import pages
    app.register_blueprint(pages)

    # Create tables
    with app.app_context():
        db.create_all()
        
        # Seed default admin if not exists
        from app.models.user import User
        from sqlalchemy import inspect
        
        try:
            inspector = inspect(db.engine)
            columns = [c['name'] for c in inspector.get_columns('users')]
            has_approved_col = 'is_approved' in columns
            
            if not User.query.filter_by(username='admin').first():
                print("=== Seeding Data ===")
                admin_pass = generate_password_hash('123456')
                user_pass = generate_password_hash('123456')
                
                def create_user_safe(**kwargs):
                    if not has_approved_col:
                        kwargs.pop('is_approved', None)
                    return User(**kwargs)

                admin = create_user_safe(username='admin', email='quocdatforwork.com', password_hash=admin_pass, full_name='Quản Trị Viên', role='admin', is_active=True, is_approved=True)
                gv1 = create_user_safe(username='gv1', email='quocdat2001.999@gmail.com', password_hash=user_pass, full_name='Giảng Viên A', role='teacher', department='CNTT', is_active=True, is_approved=True)
                gv2 = create_user_safe(username='gv2', email='iphonequocdat@gmail.com', password_hash=user_pass, full_name='Giảng Viên B', role='teacher', department='Kinh Tế', is_active=True, is_approved=True)
                
                sv1 = create_user_safe(username='sv1', email='itdatit12@gmail.com', password_hash=user_pass, full_name='Sinh Viên 1', role='student', student_id='SV001', department='CNTT', is_active=True, is_approved=True)
                sv2 = create_user_safe(username='sv2', email='quocdatforworkv2@gmail.com', password_hash=user_pass, full_name='Sinh Viên 2', role='student', student_id='SV002', department='CNTT', is_active=True, is_approved=True)
                sv3 = create_user_safe(username='sv3', email='legalmind2025@gmail.com', password_hash=user_pass, full_name='Sinh Viên 3', role='student', student_id='SV003', department='Kinh Tế', is_active=True, is_approved=True)
                
                db.session.add_all([admin, gv1, gv2, sv1, sv2, sv3])
                db.session.commit()
                print("✓ Created default users")
        except Exception as e:
            print(f"Skipping seeding due to schema mismatch or error: {e}")
            db.session.rollback()


            


    # Start automated reminder worker
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        from app.utils.background_tasks import start_reminder_worker
        start_reminder_worker(app)

    return app
