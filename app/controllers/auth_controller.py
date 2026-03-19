from flask import Blueprint, request, jsonify, session
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services.user_service import UserService
from app.utils.decorators import role_required
from app.models.user import User # Added for direct query if needed
from app.extensions import db # Added for delete operations

auth_bp = Blueprint('auth', __name__, url_prefix='/api')
user_service = UserService()


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['username', 'email', 'password', 'full_name']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    user, error = user_service.register(
        username=data['username'],
        email=data['email'],
        password=data['password'],
        full_name=data['full_name'],
        role=data.get('role', 'student'),
        phone=data.get('phone'),
        student_id=data.get('student_id'),
        department=data.get('department')
    )

    if error:
        return jsonify({'error': error}), 400

    return jsonify({'message': 'Registration successful', 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password are required'}), 400

    user, token, error = user_service.login(data['username'], data['password'])

    if error:
        return jsonify({'error': error}), 401

    # Also set session for page-based auth
    session['user_id'] = user.id
    session['username'] = user.username
    session['role'] = user.role
    session['full_name'] = user.full_name
    session['token'] = token
    session['reminder_preference'] = user.reminder_preference

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': user.to_dict()
    }), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = user_service.get_user(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user.to_dict()}), 200


@auth_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    paginated = user_service.get_all_users(page=page, per_page=per_page)
    return jsonify({
        'users': [u.to_dict() for u in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'per_page': paginated.per_page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }), 200


@auth_bp.route('/users/<int:user_id>', methods=['PUT'])
@jwt_required()
@role_required('admin')
def update_user(user_id):
    data = request.get_json()
    user = user_service.update_user(user_id, **data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User updated', 'user': user.to_dict()}), 200


@auth_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
@role_required('admin')
def delete_user(user_id):
    # Ensure admin isn't deleting themselves
    current_user_id = get_jwt_identity()
    if current_user_id == user_id:
        return jsonify({'error': 'Cannot delete yourself'}), 400
        
    result = user_service.delete_user(user_id)
    if not result:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User deleted'}), 200


@auth_bp.route('/users/<int:user_id>/toggle', methods=['PUT'])
@jwt_required()
@role_required('admin')
def toggle_user(user_id):
    user = user_service.toggle_active(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'message': 'User status updated', 'user': user.to_dict()}), 200


@auth_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    # Updated: Only return TEACHERS for task assignment as students are no longer assigned tasks
    users = User.query.filter(User.role == 'teacher', User.is_active == True).all()
    return jsonify({
        'students': [{
            'id': u.id,
            'username': u.username,
            'full_name': u.full_name,
            'role': u.role,
            'student_id': u.student_id
        } for u in users]
    }), 200


@auth_bp.route('/teachers', methods=['GET'])
@jwt_required()
def get_teachers():
    teachers = user_service.get_teachers()
    return jsonify({'teachers': [t.to_dict() for t in teachers]}), 200

@auth_bp.route('/settings', methods=['PUT'])
@jwt_required()
def update_settings():
    user_id = get_jwt_identity()
    data = request.get_json()
    
    # Allowed fields for self-update
    allowed = ['reminder_preference', 'full_name', 'phone', 'department']
    update_data = {k: v for k, v in data.items() if k in allowed}
    
    user = user_service.update_user(user_id, **update_data)
    if not user:
        return jsonify({'error': 'User not found'}), 404
        
    # Sync session
    session['reminder_preference'] = user.reminder_preference
    session['full_name'] = user.full_name
        
    return jsonify({'message': 'Cập nhật cài đặt thành công', 'user': user.to_dict()}), 200
