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
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                email='admin@edutask.vn',
                full_name='Quản trị viên',
                role='admin',
                is_active=True
            )
            admin.set_password('123456')
            db.session.add(admin)
            db.session.commit()
            print("Default admin created: admin / 123456")

    # Start automated reminder worker
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true' or not app.debug:
        from app.utils.background_tasks import start_reminder_worker
        start_reminder_worker(app)

    return app
