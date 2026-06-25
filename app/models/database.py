from app import db
from datetime import datetime

class ChatSession(db.Model):
    """Chat session model"""
    __tablename__ = 'chat_sessions'
    
    session_id = db.Column(db.String(255), primary_key=True)
    user_id = db.Column(db.Integer, nullable=True)
    visitor_id = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(50), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='session', lazy=True, cascade='all, delete-orphan')
    context = db.relationship('ChatContext', backref='session', uselist=False, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'user_id': self.user_id,
            'visitor_id': self.visitor_id,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ChatMessage(db.Model):
    """Chat message model"""
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(255), db.ForeignKey('chat_sessions.session_id'), nullable=False)
    sender_type = db.Column(db.Enum('user', 'bot', 'admin'), default='user')
    message = db.Column(db.Text, nullable=False)
    intent = db.Column(db.String(100), nullable=True)
    confidence = db.Column(db.Float, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'session_id': self.session_id,
            'sender_type': self.sender_type,
            'message': self.message,
            'intent': self.intent,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ChatContext(db.Model):
    """Chat context model"""
    __tablename__ = 'chat_context'
    
    session_id = db.Column(db.String(255), db.ForeignKey('chat_sessions.session_id'), primary_key=True)
    current_intent = db.Column(db.String(100), nullable=True)
    last_action = db.Column(db.String(100), nullable=True)
    context_data = db.Column(db.JSON, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'session_id': self.session_id,
            'current_intent': self.current_intent,
            'last_action': self.last_action,
            'context_data': self.context_data,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }