from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.qna_service import QnAService
from app.utils.decorators import role_required

qna_bp = Blueprint('qna', __name__, url_prefix='/api/qna')
qna_service = QnAService()


@qna_bp.route('/questions', methods=['POST'])
@jwt_required()
def create_question():
    data = request.get_json()
    if not data.get('title') or not data.get('content'):
        return jsonify({'error': 'Title and content are required'}), 400

    user_id = get_jwt_identity()
    question = qna_service.create_question(
        title=data['title'],
        content=data['content'],
        asked_by=user_id,
        course_name=data.get('course_name'),
        course_code=data.get('course_code'),
    )

    return jsonify({'message': 'Question created', 'question': question.to_dict()}), 201


@qna_bp.route('/questions', methods=['GET'])
@jwt_required(optional=True)
def get_questions():
    questions = qna_service.get_all_questions()
    return jsonify({'questions': [q.to_dict() for q in questions]}), 200


@qna_bp.route('/admin/questions', methods=['GET'])
@jwt_required()
@role_required('admin')
def get_admin_questions():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    search = request.args.get('search')
    
    paginated = qna_service.get_paginated_questions(page=page, per_page=per_page, search=search)
    
    return jsonify({
        'questions': [q.to_dict() for q in paginated.items],
        'total': paginated.total,
        'pages': paginated.pages,
        'current_page': paginated.page,
        'has_next': paginated.has_next,
        'has_prev': paginated.has_prev
    }), 200


@qna_bp.route('/questions/<int:question_id>', methods=['GET'])
@jwt_required(optional=True)
def get_question(question_id):
    question = qna_service.get_question(question_id)
    if not question:
        return jsonify({'error': 'Question not found'}), 404
    return jsonify({'question': question.to_dict()}), 200


@qna_bp.route('/answers', methods=['POST'])
@jwt_required()
def create_answer():
    data = request.get_json()
    if not data.get('content') or not data.get('question_id'):
        return jsonify({'error': 'Content and question_id are required'}), 400

    user_id = get_jwt_identity()
    answer = qna_service.create_answer(
        content=data['content'],
        question_id=data['question_id'],
        answered_by=user_id,
        parent_id=data.get('parent_id')
    )

    return jsonify({'message': 'Answer created', 'answer': answer.to_dict()}), 201


@qna_bp.route('/questions/<int:question_id>/resolve', methods=['PUT'])
@jwt_required()
def resolve_question(question_id):
    user_id = get_jwt_identity()
    from app.services.user_service import UserService
    user = UserService().get_user(user_id)
    question = qna_service.get_question(question_id)

    if not question:
        return jsonify({'error': 'Question not found'}), 404

    if user.role != 'admin' and question.asked_by != user_id:
        return jsonify({'error': 'Permission denied'}), 403

    question = qna_service.mark_resolved(question_id)
    return jsonify({'message': 'Question resolved', 'question': question.to_dict()}), 200


@qna_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
def delete_question(question_id):
    user_id = get_jwt_identity()
    from app.services.user_service import UserService
    user = UserService().get_user(user_id)
    question = qna_service.get_question(question_id)

    if not question:
        return jsonify({'error': 'Question not found'}), 404

    if user.role != 'admin' and question.asked_by != user_id:
        return jsonify({'error': 'Permission denied'}), 403

    result = qna_service.delete_question(question_id)
    return jsonify({'message': 'Question deleted'}), 200
    

@qna_bp.route('/answers/<int:answer_id>', methods=['DELETE'])
@jwt_required()
def delete_answer(answer_id):
    user_id = get_jwt_identity()
    from app.services.user_service import UserService
    user = UserService().get_user(user_id)
    answer = qna_service.get_answer(answer_id)
    
    if not answer:
        return jsonify({'error': 'Answer not found'}), 404
        
    if user.role != 'admin' and answer.answered_by != user_id:
        return jsonify({'error': 'Permission denied'}), 403
        
    result = qna_service.delete_answer(answer_id)
    if not result:
        return jsonify({'error': 'Answer not found'}), 404
    return jsonify({'message': 'Answer deleted'}), 200
