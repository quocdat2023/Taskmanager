from flask import request
from flask_socketio import emit, join_room, leave_room
from app.extensions import socketio
from flask_jwt_extended import decode_token
from app.services.chat_service import ChatService

chat_service = ChatService()

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    if not token:
        return False
    
    try:
        decoded_token = decode_token(token)
        user_id = decoded_token['sub']
        join_room(f"user_{user_id}")
        print(f"User {user_id} connected to WebSocket")
    except Exception as e:
        print(f"WebSocket connection error: {e}")
        return False

@socketio.on('disconnect')
def handle_disconnect():
    print("User disconnected from WebSocket")

@socketio.on('send_message')
def handle_send_message(data):
    # This event is triggered when a user sends a message via WebSocket
    receiver_id = data.get('receiver_id')
    content = data.get('content')
    token = data.get('token')
    
    if not receiver_id or not content or not token:
        return
        
    try:
        decoded_token = decode_token(token)
        sender_id = decoded_token['sub']
        
        # Save to database
        message = chat_service.send_message(sender_id, receiver_id, content)
        
        if message:
            msg_dict = message.to_dict()
            # Send to receiver
            emit('new_message', msg_dict, room=f"user_{receiver_id}")
            # Send back to sender for confirmation/sync
            emit('message_sent', msg_dict, room=f"user_{sender_id}")
            
    except Exception as e:
        print(f"Error handling send_message: {e}")
