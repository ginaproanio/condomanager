from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


def create_app():
    app = Flask(__name__)

    # ========================
    # CONFIGURACIÓN CLAVE
    # ========================
    app.config['SECRET_KEY'] = os.environ.get('-secret_key', 'gina2025-super-secreto-cambia-en-produccion')
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'gina2025-jwt-ultra-secreto-123456789')

    # JWT con cookies (el estándar moderno y seguro)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = True          # Obligatorio en producción (HTTPS)
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_SESSION_COOKIE'] = False        # ← DESACTIVA la sesión tradicional de Flask
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)   # Token de acceso dura 12h
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)   # Refresh opcional
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False   # Puedes activarlo después si quieres

    # Base de datos
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    database_url = os.environ.get('DATABASE_URL', '')
    if database_url.startswith(('postgres://', 'postgresql://')):
        database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"URL de base de datos: {database_url}")

    # Inicializaciones
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)  # Importante para cookies JWT

    # ========================
    # JWT: Cargar usuario actual
    # ========================
    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        from app.models import User
        identity = jwt_data["sub"]
        return User.query.get(identity)

    # ========================
    # Registrar rutas
    # ========================
    from app.routes import main
    app.register_blueprint(main)

    # ========================
    # Crear tablas + usuario maestro (solo si no existe)
    # ========================
    with app.app_context():
        try:
            print("Creando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente")

            from app.models import User
            import hashlib

            master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
            if not User.query.filter_by(email=master_email).first():
                master_password = os.environ.get('MASTER_PASSWORD', 'Master2025!')
                pwd_hash = hashlib.sha256(master_password.encode()).hexdigest()

                master = User(
                    email=master_email,
                    name='Administrador Maestro',
                    phone='+593999999999',
                    city='Guayaquil',
                    country='Ecuador',
                    password_hash=pwd_hash,
                    tenant='master',
                    role='MASTER',
                    status='active'
                )
                db.session.add(master)
                db.session.commit()
                print(f"USUARIO MAESTRO CREADO: {master_email}")
            else:
                print("Usuario maestro ya existe")

        except Exception as e:
            print(f"Error en inicialización: {e}")

    # ========================
    # Configuración automática de tenant
    # ========================
    def get_tenant_config(tenant):
        from app.models import CondominioConfig
        config = CondominioConfig.query.get(tenant)
        if not config:
            config = CondominioConfig(
                tenant=tenant,
                primary_color='#2c5aa0',
                nombre_comercial=tenant.replace('_', ' ').title()
            )
            db.session.add(config)
            db.session.commit()
            print(f"Configuración automática creada para: {tenant}")
        return config

    app.get_tenant_config = get_tenant_config

    return app