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
    
    # AGREGAR ESTO AL FINAL del archivo config.py
    JWT_SECRET_KEY = os.getenv('JWT_SECRET', 'jwt_fallback_secret_2025')
    JWT_ACCESS_TOKEN_EXPIRES = 86400  # 24 horas en segundos