from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gina_2025_secure')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Obtener DATABASE_URL con múltiples intentos
    database_url = os.environ.get('DATABASE_URL')
    
    if not database_url:
        # Intentar con nombre alternativo que usa Railway
        database_url = os.environ.get('POSTGRES_URL')
    
    if not database_url:
        # Fallback para desarrollo
        database_url = 'sqlite:///app.db'
    
    # Arreglar URL de PostgreSQL si es necesario
    if database_url and database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    
    # Verificación crítica
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        raise RuntimeError("SQLALCHEMY_DATABASE_URI no está configurado")

    # En __init__.py, antes de db.init_app(app)
    print(f"DATABASE_URL: {os.environ.get('DATABASE_URL')}")
    print(f"SQLALCHEMY_DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")

    db.init_app(app)
    
    with app.app_context():
        from .routes import main
        app.register_blueprint(main)
        
        db.create_all()

    return app