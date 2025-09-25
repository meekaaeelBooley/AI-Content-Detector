import os

class Config:
    # Basic Flask configuration settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')
    # Used for session security. Tries to get from environment variable, otherwise uses a default (should be changed in production...)
    
    UPLOAD_FOLDER = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'uploads')
    # Defines where uploaded files will be stored
    # Creates an 'uploads' folder in the same directory as this config file
    
    MAX_CONTENT_LENGTH = 500 * 1024  # 500KB
    # Security measure to prevent large file uploads
    
    # Redis configuration for session storage and caching
    REDIS_HOST = 'localhost'        # Redis server address
    REDIS_PORT = 6379              # Default Redis port
    REDIS_DB = 0                   # Database number (0-15)
    REDIS_PASSWORD = None          # No password required

class DevelopmentConfig(Config):
    DEBUG = True
    # Development-specific settings
    # Enables debug mode: better error messages, auto-reload on code changes

class ProductionConfig(Config):
    DEBUG = False
    # Production settings - debug mode disabled for security
    # Prevent sensitive information leakage in error messages

# Configuration registry allows easy switching between environments
config = {
    'development': DevelopmentConfig,  # Used during development
    'production': ProductionConfig,    # Used in live deployment
    'default': DevelopmentConfig       # Fallback option
}