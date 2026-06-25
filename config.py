import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'ecommerceapp')
    DB_PORT = os.environ.get('DB_PORT', 3306)
    
    # Gemini API
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    
    # Session
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    
    # Application
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    CHAT_HISTORY_LIMIT = int(os.environ.get('CHAT_HISTORY_LIMIT', 50))
    
    @staticmethod
    def get_database_uri():
        """Get database connection URI"""
        return f"mysql+pymysql://{Config.DB_USER}:{Config.DB_PASSWORD}@{Config.DB_HOST}:{Config.DB_PORT}/{Config.DB_NAME}?charset=utf8mb4"

config = {
    'development': Config,
    'production': Config,
    'default': Config
}