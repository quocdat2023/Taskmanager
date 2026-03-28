from flask import Blueprint, render_template, session, redirect, url_for
from app.utils.decorators import login_required_page, admin_required_page, teacher_required_page

pages = Blueprint('pages', __name__)


@pages.route('/')
def index():
    return render_template('landing.html')


@pages.route('/login')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('pages.dashboard'))
    return render_template('auth/login.html')


@pages.route('/register')
def register_page():
    return render_template('auth/register.html')


@pages.route('/logout')
def logout_page():
    session.clear()
    return redirect(url_for('pages.login_page'))


@pages.route('/dashboard')
@login_required_page
def dashboard():
    from app.models.user import User
    user = User.query.get(session['user_id'])
    role = user.role if user else session.get('role', 'student')
    
    if role == 'admin':
        return render_template('dashboard/admin.html')
    elif role == 'teacher':
        return render_template('dashboard/teacher.html')
    else:
        return render_template('dashboard/student.html')


@pages.route('/tasks')
@login_required_page
@teacher_required_page
def tasks_page():
    return render_template('tasks/index.html')


@pages.route('/tasks/board')
@login_required_page
@teacher_required_page
def tasks_board():
    return render_template('tasks/board.html')


@pages.route('/schedules')
@login_required_page
def schedules_page():
    return render_template('schedules/index.html')


@pages.route('/documents')
@login_required_page
def documents_page():
    return render_template('documents/index.html')


@pages.route('/qna')
@login_required_page
def qna_page():
    return render_template('qna/index.html')


@pages.route('/users')
@admin_required_page
def users_page():
    return render_template('admin/users.html')


@pages.route('/admin/reminders')
@admin_required_page
def admin_reminders_page():
    return render_template('admin/reminders.html')
@pages.route('/settings')
@login_required_page
def settings_page():
    return render_template('settings.html')
@pages.route('/admin/tasks')
@admin_required_page
def admin_tasks_page():
    return render_template('admin/tasks.html')
@pages.route('/tasks/requests')
@admin_required_page
def task_requests_page():
    return render_template('tasks/requests.html')


@pages.route('/admin/academic-years')
@admin_required_page
def academic_years_page():
    return render_template('admin/academic_years.html')


@pages.route('/chat')
@login_required_page
def chat_page():
    return render_template('chat/index.html')
