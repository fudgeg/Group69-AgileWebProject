import os
from pathlib import Path

from dotenv import load_dotenv

# load environment from .env (project root) 
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    # secret key for session signing & CSRF protection
    SECRET_KEY = os.environ.get('SECRET_KEY', 'you-will-never-guess')

    # database URL
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{BASE_DIR / 'soulmaps.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
