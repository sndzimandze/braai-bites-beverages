import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Flask Configuration
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    FLASK_ENV = os.environ.get('FLASK_ENV', 'development')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False') == 'True'

    # Database Configuration
    DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///braaibites.db')
    # Fix for platforms that use 'postgres://' instead of 'postgresql://'
    if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
        DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,  # Verify connections before using
        'pool_recycle': 300,    # Recycle connections after 5 minutes
    }

    # AliExpress API Configuration
    ALIEXPRESS_APP_KEY = os.environ.get('ALIEXPRESS_APP_KEY')
    ALIEXPRESS_APP_SECRET = os.environ.get('ALIEXPRESS_APP_SECRET')
    ALIEXPRESS_API_URL = os.environ.get('ALIEXPRESS_API_URL', 'https://gw.api.alibaba.com/openapi/')

    # OAuth Configuration
    ALIEXPRESS_REDIRECT_URI = os.environ.get('ALIEXPRESS_REDIRECT_URI', 'https://braaibitesbeverages.com/auth/callback')
    ALIEXPRESS_AUTH_URL = os.environ.get('ALIEXPRESS_AUTH_URL', 'https://sandbox.oauth.alibaba.com/authorize')
    ALIEXPRESS_TOKEN_URL = os.environ.get('ALIEXPRESS_TOKEN_URL', 'https://sandbox.oauth.alibaba.com/token')
    ALIEXPRESS_HOST = os.environ.get('ALIEXPRESS_HOST', 'https://sandbox.api.alibaba.com')

    # Pagination
    PRODUCTS_PER_PAGE = 20

    @staticmethod
    def validate_config():
        """Validate that required environment variables are set"""
        required_vars = ['ALIEXPRESS_APP_KEY', 'ALIEXPRESS_APP_SECRET']
        missing_vars = [var for var in required_vars if not os.environ.get(var)]

        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                f"Please check your .env file."
            )
