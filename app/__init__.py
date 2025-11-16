from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración desde config.py
    from config import Config
    app.config.from_object(Config)
    
    # Inicializar la base de datos
    db.init_app(app)
    
    with app.app_context():
        from app.routes import main
        app.register_blueprint(main)
        
        # Crear tablas
        db.create_all()

    return app