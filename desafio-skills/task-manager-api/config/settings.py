import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-only-insecure-key')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tasks.db')
PORT = int(os.environ.get('PORT', 5000))
DEBUG = os.environ.get('DEBUG', 'true').lower() == 'true'
