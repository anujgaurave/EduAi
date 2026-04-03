from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.chat import Chat
from app.models.user import User
from app.services.ai_service import ai_service
from app.utils.helpers import sanitize_input, validate_required_fields
import logging

logger = logging.getLogger(__name__)

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_chat_sessions():
    """Get all chat sessions for user"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        
        chats = Chat.find_by_user(user_id, limit=limit, skip=(page-1)*limit)
        
        return jsonify({
            'chats': [chat.to_dict() for chat in chats],
            'page': page,
            'limit': limit
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching chat sessions: {e}")
        return jsonify({'error': 'Could not fetch chat sessions'}), 500

@chat_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_chat_session():
    """Create new chat session"""
    try:
        user_id = get_jwt_identity()
        user = User.find_by_id(user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        title = sanitize_input(data.get('title', 'New Chat'))
        
        chat = Chat(user_id=user_id, title=title)
        chat_id = chat.save()
        
        return jsonify({
            'message': 'Chat session created',
            'chat': chat.to_dict()
        }), 201
    
    except Exception as e:
        logger.error(f"Error creating chat session: {e}")
        return jsonify({'error': 'Could not create chat session'}), 500

@chat_bp.route('/sessions/<chat_id>', methods=['GET'])
@jwt_required()
def get_chat(chat_id):
    """Get specific chat session"""
    try:
        user_id = get_jwt_identity()
        
        chat = Chat.find_by_id(chat_id)
        if not chat or str(chat.user_id) != user_id:
            return jsonify({'error': 'Chat not found'}), 404
        
        return jsonify({
            'chat': chat.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching chat: {e}")
        return jsonify({'error': 'Could not fetch chat'}), 500

@chat_bp.route('/sessions/<chat_id>/message', methods=['POST'])
@jwt_required()
def send_message(chat_id):
    """Send message to chat"""
    try:
        user_id = get_jwt_identity()
        
        chat = Chat.find_by_id(chat_id)
        if not chat or str(chat.user_id) != user_id:
            return jsonify({'error': 'Chat not found'}), 404
        
        data = request.get_json()
        
        # Validate input
        is_valid, error = validate_required_fields(data, ['message'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        message_text = sanitize_input(data['message'])
        
        if len(message_text) == 0:
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        if len(message_text) > 5000:
            return jsonify({'error': 'Message too long'}), 400
        
        # Add user message
        chat.add_message('user', message_text)
        
        # Get AI response
        recent_context = chat.get_recent_context(num_messages=3)
        context_text = ' '.join([msg['content'] for msg in recent_context if msg['role'] == 'user'])
        
        ai_response = ai_service.generate_response(
            message_text,
            context=context_text,
            temperature=0.7
        )
        
        if ai_response['success']:
            chat.add_message('assistant', ai_response['response'])
            chat.save()
            
            return jsonify({
                'message': 'Message received',
                'chat': chat.to_dict(),
                'ai_response': {
                    'response': ai_response['response'],
                    'fallback': ai_response.get('fallback', False)
                }
            }), 200
        else:
            return jsonify({
                'error': ai_response.get('error', 'Could not generate response'),
                'fallback': True
            }), 503
    
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return jsonify({'error': 'Could not process message'}), 500

@chat_bp.route('/sessions/<chat_id>', methods=['DELETE'])
@jwt_required()
def delete_chat(chat_id):
    """Delete chat session"""
    try:
        user_id = get_jwt_identity()
        
        chat = Chat.find_by_id(chat_id)
        if not chat or str(chat.user_id) != user_id:
            return jsonify({'error': 'Chat not found'}), 404
        
        chat.delete_soft()
        
        return jsonify({'message': 'Chat deleted'}), 200
    
    except Exception as e:
        logger.error(f"Error deleting chat: {e}")
        return jsonify({'error': 'Could not delete chat'}), 500

@chat_bp.route('/sessions/<chat_id>/title', methods=['PUT'])
@jwt_required()
def update_chat_title(chat_id):
    """Update chat title"""
    try:
        user_id = get_jwt_identity()
        
        chat = Chat.find_by_id(chat_id)
        if not chat or str(chat.user_id) != user_id:
            return jsonify({'error': 'Chat not found'}), 404
        
        data = request.get_json()
        
        is_valid, error = validate_required_fields(data, ['title'])
        if not is_valid:
            return jsonify({'error': error}), 400
        
        chat.title = sanitize_input(data['title'])
        chat.save()
        
        return jsonify({
            'message': 'Chat title updated',
            'chat': chat.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error updating chat title: {e}")
        return jsonify({'error': 'Could not update chat title'}), 500

@chat_bp.route('/search', methods=['GET'])
@jwt_required()
def search_chats():
    """Search chats by query"""
    try:
        user_id = get_jwt_identity()
        query = sanitize_input(request.args.get('q', ''))
        
        if len(query) < 2:
            return jsonify({'error': 'Query too short'}), 400
        
        from app.db import db
        from bson.objectid import ObjectId
        
        chat_collection = db.db['chats']
        chats = chat_collection.find({
            'user_id': ObjectId(user_id),
            'is_deleted': False,
            '$text': {'$search': query}
        }).limit(10)
        
        results = [Chat(**chat).to_dict() for chat in chats]
        
        return jsonify({
            'results': results
        }), 200
    
    except Exception as e:
        logger.error(f"Error searching chats: {e}")
        return jsonify({'error': 'Could not search chats'}), 500
