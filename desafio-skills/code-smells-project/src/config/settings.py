import os

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-default')
DATABASE_URL = os.environ.get('DATABASE_URL', 'loja.db')
PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'false').lower() == 'true'
