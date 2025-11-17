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

    # ✅ FUNCIÓN para configuración de tenants (¡IMPORTANTE: ANTES del return!)
    def get_tenant_config(tenant):
        from app.models import CondominioConfig  # Import aquí para evitar circular imports
        config = CondominioConfig.query.get(tenant)
        if not config:
            # ✅ CREAR AUTOMÁTICAMENTE con valores por defecto
            config = CondominioConfig(
                tenant=tenant,
                primary_color='#2c5aa0',
                nombre_comercial=tenant.title()
            )
            db.session.add(config)
            db.session.commit()
            print(f"✅ Configuración creada automáticamente para: {tenant}")
        return config

    # Hacer la función disponible en la app
    app.get_tenant_config = get_tenant_config

    return app  # ✅ ÚNICO return - todo lo demás VA ANTES