import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'gina_2025_secure')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Railway inyecta DATABASE_URL automáticamente
    database_url = os.getenv('DATABASE_URL')
    
    # Arreglar URL de PostgreSQL si es necesario
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    SQLALCHEMY_DATABASE_URI = database_url or 'sqlite:///default.db'