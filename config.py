import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'your-secret-key-here'  # In production, use os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///jobtracker.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=24) 