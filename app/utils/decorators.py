from functools import wraps
from flask import jsonify, session, redirect, url_for, request
from flask_jwt_extended import verify_jwt_in_request, get_jwt


def role_required(*roles):
    """Decorator for API routes requiring specific roles."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            from flask_jwt_extended import get_jwt_identity
            from app.models.user import User
            
            user_id = get_jwt_identity()
            user = User.query.get(user_id)
            user_role = user.role if user else ''
            
            if user_role not in roles:
                return jsonify({'error': 'Unauthorized. Required role: ' + ', '.join(roles)}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def login_required_page(fn):
    """Decorator for page routes requiring login via session."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page'))
        return fn(*args, **kwargs)
    return wrapper


def admin_required_page(fn):
    """Decorator for page routes requiring admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page'))
            
        from app.models.user import User
        user = User.query.get(session['user_id'])
        current_role = user.role if user else session.get('role')
        
        # Sync session
        if current_role and current_role != session.get('role'):
            session['role'] = current_role
            
        if current_role != 'admin':
            return redirect(url_for('pages.dashboard'))
        return fn(*args, **kwargs)
    return wrapper


def teacher_required_page(fn):
    """Decorator for page routes requiring teacher or admin role."""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('pages.login_page'))
            
        from app.models.user import User
        user = User.query.get(session['user_id'])
        current_role = user.role if user else session.get('role')
        
        # Sync session
        if current_role and current_role != session.get('role'):
            session['role'] = current_role
            
        if current_role not in ('admin', 'teacher'):
            return redirect(url_for('pages.dashboard'))
        return fn(*args, **kwargs)
    return wrapper
