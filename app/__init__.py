from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

import os

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()

def create_app():
    app = Flask(__name__)
    
    # Configuración
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'gina_2025_secure')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # ✅ FORZAR pg8000 explícitamente
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
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

    # Configuración JWT
    jwt.init_app(app)
    
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id
    
    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User  # ✅ IMPORTAR DENTRO DE LA FUNCIÓN
        identity = jwt_data['sub']
        return User.query.filter_by(id=identity).first()
    
    cors.init_app(app)
    
    # Rutas
    from app.routes import main
    app.register_blueprint(main)
    
    # Crear tablas Y usuario maestro
    with app.app_context():
        try:
            print("🔄 Creando tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente")
            
            # ✅ CREAR USUARIO MAESTRO SI NO EXISTE
            from app.models import User  # Importar aquí para evitar circular imports
            import hashlib
            
            master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
            if not User.query.filter_by(email=master_email).first():
                master_password = os.environ.get('MASTER_PASSWORD', 'Master123!')
                pwd_hash = hashlib.sha256(master_password.encode()).hexdigest()
                
                master_user = User(
                    email=master_email,
                    name='Administrador Maestro',
                    phone='+593 99 999 9999',
                    city='Quito',
                    country='Ecuador',
                    password_hash=pwd_hash,
                    tenant='master',
                    role='MASTER',
                    status='active'
                )
                db.session.add(master_user)
                db.session.commit()
                print(f"🎯 USUARIO MAESTRO CREADO: {master_email}")
            else:
                print("✅ Usuario maestro ya existe")
            
        except Exception as e:
            print(f"❌ Error en inicialización: {e}")

    # ✅ FUNCIÓN para configuración de tenants
    def get_tenant_config(tenant):
        from app.models import CondominioConfig
        config = CondominioConfig.query.get(tenant)
        if not config:
            config = CondominioConfig(
                tenant=tenant,
                primary_color='#2c5aa0',
                nombre_comercial=tenant.title()
            )
            db.session.add(config)
            db.session.commit()
            print(f"✅ Configuración creada automáticamente para: {tenant}")
        return config

    app.get_tenant_config = get_tenant_config

    return app