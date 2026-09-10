import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'smartplacement_secret_key_major_project_2026')
    
    # MySQL Database Settings
    DB_HOST = os.environ.get('DB_HOST', 'localhost')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))
    DB_USER = os.environ.get('DB_USER', 'root')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', 'smartplacement_db')

    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
