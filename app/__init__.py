import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_cors import CORS

# Create db instance without initializing with app yet
db = SQLAlchemy()
migrate = Migrate()
session = Session()

def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database configuration - using SQLite for simplicity (or MySQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'  # This creates ecommerce.db file
    # If you want to use MySQL, use this instead:
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/ecommerceApp'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Session configuration
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    session.init_app(app)
    CORS(app)
    
    # Register blueprints
    from app.routes.main import main_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    
    # Create tables
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
    
    return app