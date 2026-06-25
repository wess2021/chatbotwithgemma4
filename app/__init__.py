import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_session import Session
from flask_cors import CORS
from dotenv import load_dotenv
from config import Config

load_dotenv()

db = SQLAlchemy()
migrate = Migrate()
session = Session()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    app.config.from_object(Config)
    
    # Use utf8 instead of utf8mb4 to avoid key length issues
    db_uri = Config.get_database_uri()
    if 'utf8mb4' in db_uri:
        db_uri = db_uri.replace('utf8mb4', 'utf8')
    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True
    
    db.init_app(app)
    migrate.init_app(app, db)
    session.init_app(app)
    CORS(app)
    
    from app.routes.main import main_bp
    from app.routes.chat import chat_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(chat_bp)
    
    with app.app_context():
        db.create_all()
        print("✅ Database tables created/verified")
        print(f"📊 Connected to: {Config.DB_NAME} on {Config.DB_HOST}")
    
    return app