from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()  # ✅ SOLO UNA instancia aquí

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gina_2025_secure')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # PostgreSQL
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:aJPvUmFIgozAjhuKLPOUZTlsSQVvnJZU@centerbeam.proxy.rlwy.net:11700/railway')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    # ✅ Inicializar DB con la app
    db.init_app(app)
    
    # Rutas
    from app.routes import main
    app.register_blueprint(main)
    
    # Tablas
    with app.app_context():
        db.create_all()

    return app