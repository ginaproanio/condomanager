from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
import sys

db = SQLAlchemy()

def create_app():
    print("🚀 Iniciando create_app...", file=sys.stderr)
    
    app = Flask(__name__)
    
    # Configuración básica
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gina_2025_secure')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # CONEXIÓN DIRECTA a PostgreSQL de Railway
    database_url = os.environ.get('DATABASE_URL')
    
    # Si no hay DATABASE_URL, usar la URL directa de tu PostgreSQL
    if not database_url:
        database_url = "postgresql://postgres:aJPvUmFIgozAjhuKLPOUZTlsSQVvnJZU@centerbeam.proxy.rlwy.net:11700/railway"
        print("⚠️  Usando DATABASE_URL manual", file=sys.stderr)
    else:
        print("✅ DATABASE_URL de variables", file=sys.stderr)
    
    # Arreglar formato si es necesario
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"📊 DATABASE_URL: {database_url}", file=sys.stderr)

    # Inicializar DB
    db.init_app(app)
    print("✅ DB inicializada", file=sys.stderr)
    
    try:
        print("🔄 Importando rutas...", file=sys.stderr)
        from app.routes import main
        print("✅ Rutas importadas", file=sys.stderr)
        
        app.register_blueprint(main)
        print("✅ Blueprint registrado", file=sys.stderr)
        
        print("🔄 Creando tablas...", file=sys.stderr)
        with app.app_context():
            db.create_all()
        print("✅ Tablas creadas", file=sys.stderr)
            
    except Exception as e:
        print(f"❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)

    print("🎉 App creada exitosamente", file=sys.stderr)
    return app