import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Config:
    """Application configuration settings"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_ENV', 'development') == 'development'
    
    # IMAP Configuration (Free Gmail Access)
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    
    # Ollama Configuration
    OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen2.5:3b')
    
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/emails.db')
    
    # Email Processing Configuration
    EMAIL_FETCH_LIMIT = int(os.getenv('EMAIL_FETCH_LIMIT', '100'))
    EMAIL_FETCH_DAYS = int(os.getenv('EMAIL_FETCH_DAYS', '30'))
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration variables"""
        required_vars = [
            'GMAIL_EMAIL',
            'GMAIL_APP_PASSWORD'
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
