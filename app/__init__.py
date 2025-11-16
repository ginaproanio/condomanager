from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gina_2025_secure')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ✅ FORZAR pg8000 explícitamente
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        # Reemplazar postgresql:// por postgresql+pg8000://
        if database_url.startswith('postgresql://'):
            database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
        elif database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
    else:
        database_url = 'postgresql+pg8000://postgres:aJPvUmFIgozAjhuKLPOUZTlsSQVvnJZU@centerbeam.proxy.rlwy.net:11700/railway'
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"🔧 URL de base de datos: {database_url}")

    # Inicializar DB
    db.init_app(app)
    
    # Rutas
    from app.routes import main
    app.register_blueprint(main)
    
    # Crear tablas
    with app.app_context():
        try:
            print("🔄 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
        except Exception as e:
            print(f"❌ Error creando tablas: {e}")

    return app