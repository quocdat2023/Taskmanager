from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.chat_service import ChatService

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')
chat_service = ChatService()

@chat_bp.route('/contacts', methods=['GET'])
@jwt_required()
def get_contacts():
    user_id = get_jwt_identity()
    contacts = chat_service.get_contacts(user_id)
    return jsonify({'contacts': [u.to_dict() for u in contacts]}), 200

@chat_bp.route('/messages/<int:contact_id>', methods=['GET'])
@jwt_required()
def get_conversation(contact_id):
    user_id = get_jwt_identity()
    messages = chat_service.get_conversation(user_id, contact_id)
    return jsonify({'messages': [m.to_dict() for m in messages]}), 200

@chat_bp.route('/send', methods=['POST'])
@jwt_required()
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    
    if not receiver_id or not content:
        return jsonify({'error': 'Thiếu người nhận hoặc nội dung'}), 400
        
    sender_id = get_jwt_identity()
    message = chat_service.send_message(sender_id, receiver_id, content)
    
    if not message:
        return jsonify({'error': 'Không thể gửi tin nhắn'}), 400
        
    return jsonify({'message': 'Tin nhắn đã được gửi', 'chat_message': message.to_dict()}), 201

@chat_bp.route('/recent', methods=['GET'])
@jwt_required()
def get_recent():
    user_id = get_jwt_identity()
    recent = chat_service.get_recent_conversations(user_id)
    return jsonify({'recent': [m.to_dict() for m in recent]}), 200
