from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

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

    # Inicializar DB
    db.init_app(app)
    
    # ✅ AGREGAR DEBUG PARA VER QUÉ PASA
    print("🔧 Inicializando base de datos...")
    
    # Rutas
    from app.routes import main
    app.register_blueprint(main)
    
    # Crear tablas CON MANEJO DE ERRORES
    with app.app_context():
        try:
            print("🔄 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")
            # No relanzar el error para que la app siga funcionando

    return app