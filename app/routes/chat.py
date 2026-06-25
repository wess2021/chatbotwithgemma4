from flask import Blueprint, request, jsonify, session
from app.services.openrouter_service import OpenRouterService
from app.models.database import db, ChatSession, ChatMessage, ChatContext
import uuid
import os
from datetime import datetime

chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize OpenRouter with Gemma 4 (Google's free model)
openrouter = None
try:
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if api_key:
        openrouter = OpenRouterService(
            api_key=api_key,
            model="google/gemma-4-31b-it:free"
        )
        print("✅ OpenRouter initialized with Google Gemma 4 31B (Free)!")
    else:
        print("⚠️  OPENROUTER_API_KEY not found")
except Exception as e:
    print(f"❌ Error initializing OpenRouter: {e}")
    openrouter = None

@chat_bp.route('/start', methods=['POST'])
def start_chat():
    """Start a new chat session"""
    try:
        data = request.json or {}
        visitor_id = data.get('visitor_id') or session.get('visitor_id', str(uuid.uuid4())[:8])
        session['visitor_id'] = visitor_id
        
        # Create new session
        session_id = str(uuid.uuid4())
        chat_session = ChatSession(
            session_id=session_id,
            visitor_id=visitor_id,
            status='active'
        )
        db.session.add(chat_session)
        db.session.commit()
        
        # Create context
        context = ChatContext(
            session_id=session_id,
            current_intent='greeting',
            last_action='start_chat',
            context_data={'state': 'initial'}
        )
        db.session.add(context)
        db.session.commit()
        
        session['chat_session_id'] = session_id
        
        return jsonify({
            'session_id': session_id,
            'is_new': True,
            'messages': []
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in start_chat: {e}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/message', methods=['POST'])
def send_message():
    """Send a message and get response"""
    try:
        data = request.json
        message = data.get('message')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Get or create session
        session_id = session.get('chat_session_id')
        if not session_id:
            visitor_id = session.get('visitor_id', str(uuid.uuid4())[:8])
            session_id = str(uuid.uuid4())
            chat_session = ChatSession(
                session_id=session_id,
                visitor_id=visitor_id,
                status='active'
            )
            db.session.add(chat_session)
            db.session.commit()
            session['chat_session_id'] = session_id
        
        # Save user message
        user_msg = ChatMessage(
            session_id=session_id,
            sender_type='user',
            message=message
        )
        db.session.add(user_msg)
        db.session.commit()
        
        # Get AI response
        bot_response = "I'm here to help!"
        
        if openrouter:
            try:
                # Get context
                context = ChatContext.query.get(session_id)
                context_data = context.context_data if context else {}
                
                result = openrouter.send_message(message, context_data)
                if result.get('success'):
                    bot_response = result.get('response', "I'm here to help!")
                    # Update context
                    if context:
                        context.current_intent = result.get('intent', 'general_query')
                        context.last_action = 'sent_message'
                        db.session.commit()
                else:
                    bot_response = result.get('response', "I'm having trouble. Please try again.")
                    print(f"⚠️  OpenRouter error: {result}")
            except Exception as e:
                print(f"⚠️  OpenRouter exception: {e}")
                bot_response = "I'm sorry, I'm having trouble. Please try again."
        else:
            bot_response = get_fallback_response(message)
        
        # Save bot response
        bot_msg = ChatMessage(
            session_id=session_id,
            sender_type='bot',
            message=bot_response
        )
        db.session.add(bot_msg)
        db.session.commit()
        
        return jsonify({
            'user_message': {
                'message': message
            },
            'bot_response': {
                'message': bot_response
            }
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in send_message: {e}")
        return jsonify({'error': str(e)}), 500

def get_fallback_response(message: str) -> str:
    """Simple fallback responses"""
    message_lower = message.lower()
    
    responses = {
        'bonjour': "Bonjour! Comment puis-je vous aider aujourd'hui?",
        'hello': "Hello! How can I help you today?",
        'hi': "Hi there! What can I do for you?",
        'help': "I'm here to assist you. What do you need help with?",
        'product': "We have many great products. What are you looking for?",
        'order': "I can help with order inquiries. Do you have an order number?",
        'price': "Our prices are competitive. Which product interests you?",
        'thanks': "You're welcome! Anything else I can help with?",
        'bye': "Goodbye! Have a great day!",
        'merci': "De rien! Heureux de vous aider!"
    }
    
    for key, response in responses.items():
        if key in message_lower:
            return response
    
    return "I'm here to help! Could you please provide more details about what you need?"

@chat_bp.route('/history', methods=['GET'])
def get_history():
    """Get chat history"""
    try:
        session_id = session.get('chat_session_id')
        if not session_id:
            return jsonify({'messages': []})
        
        messages = ChatMessage.query.filter_by(session_id=session_id)\
            .order_by(ChatMessage.created_at.asc()).limit(50).all()
        
        return jsonify({
            'messages': [msg.to_dict() for msg in messages]
        })
        
    except Exception as e:
        print(f"❌ Error in get_history: {e}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/close', methods=['POST'])
def close_chat():
    """Close chat session"""
    try:
        session_id = session.get('chat_session_id')
        if session_id:
            chat_session = ChatSession.query.get(session_id)
            if chat_session:
                chat_session.status = 'closed'
                db.session.commit()
        
        session.pop('chat_session_id', None)
        return jsonify({'success': True, 'message': 'Session closed'})
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error in close_chat: {e}")
        return jsonify({'error': str(e)}), 500

@chat_bp.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    try:
        if openrouter:
            models = openrouter.list_models()
            free_models = [
                m for m in models 
                if m.get('pricing', {}).get('prompt', '0') == '0'
                and 'free' in m.get('id', '').lower()
            ]
            return jsonify({
                'current_model': openrouter.model,
                'free_models': [m.get('id') for m in free_models[:20]]
            })
        return jsonify({'error': 'OpenRouter not initialized'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500