from flask import Blueprint, render_template, session, request, jsonify
import uuid

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """Home page with chat widget"""
    if 'visitor_id' not in session:
        session['visitor_id'] = str(uuid.uuid4())[:8]
    
    return render_template('index.html')

@main_bp.route('/chat')
def chat_page():
    """Full chat page"""
    if 'visitor_id' not in session:
        session['visitor_id'] = str(uuid.uuid4())[:8]
    
    return render_template('chat.html')