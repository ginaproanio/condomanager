from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'gina_2025_secure')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Obtener DATABASE_URL
    database_url = os.environ.get('DATABASE_URL', 'sqlite:///app.db')  # Fallback incluido
    
    # Arreglar URL de PostgreSQL si es necesario
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    # Inicializar la base de datos
    db.init_app(app)
    
    with app.app_context():
        from app.routes import main  # ✅ Import absoluto
        app.register_blueprint(main)
        
        # Crear tablas
        db.create_all()

    return app