import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

def _parse_cors_origins(value):
    origins = []
    for origin in value.split(','):
        cleaned = origin.strip().rstrip('/')
        if cleaned:
            origins.append(cleaned)
    return origins

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production-12345678901234567890')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production-12345678901234567890')
    
    # MongoDB
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/educational_platform')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'educational_platform')
    
    # JWT
    JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.getenv('JWT_EXPIRATION_HOURS', 24)))
    
    # File Upload
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 52428800))  # 50MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'pdf,docx,txt,doc').split(','))
    
    # CORS
    CORS_ORIGINS = _parse_cors_origins(
        os.getenv(
            'CORS_ORIGINS',
            'http://localhost:3000,http://localhost:5173,https://edu-ai-team.vercel.app'
        )
    )
    
    # AI Model - Groq Mixtral
    GROQ_API_KEY = os.getenv('GROQ_API_KEY', '')
    
    # AI Model - Google Gemini (DEPRECATED)
    GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY', '')
    GOOGLE_MODEL = os.getenv('GOOGLE_MODEL', 'gemini-flash-latest')
    
    # Vector DB
    USE_FAISS = os.getenv('USE_FAISS', 'True').lower() == 'true'
    VECTOR_DIM = int(os.getenv('VECTOR_DIM', 384))
    
    # Cache
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', 300))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    MONGODB_URI = 'mongodb://localhost:27017/educational_platform_test'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
