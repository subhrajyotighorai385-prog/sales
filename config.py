import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'high-value-sales-3d-secret-key-super-secure-2026-xyz'
    
    # Instance folder database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'sales_intelligence.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # CSRF & Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = 3600
    
    # Upload limits
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'csv'}
    
    # Defaults
    DEFAULT_PREMIUM_THRESHOLD = 50000.0
    DEFAULT_CURRENCY = '₹'
    ITEMS_PER_PAGE = 15

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
