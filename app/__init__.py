from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os

from config import Config
# from app.models import User, Condominium, Unit, CondominioConfig  # Mover esta importación

db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_SESSION_COOKIE'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False

    database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    elif database_url.startswith('postgresql://') and not 'pg8000' in database_url:
        database_url = database_url.replace('postgresql://', 'postgresql+pg8000://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    print(f"URL de base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)

    # Importar modelos aquí para evitar importación circular
    from app import models

    with app.app_context():
        try:
            print("Creando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente")

            import hashlib

            master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
            if not models.User.query.filter_by(email=master_email).first():
                master_password = os.environ.get('MASTER_PASSWORD', 'Master2025!')
                pwd_hash = hashlib.sha256(master_password.encode()).hexdigest()

                master = models.User(
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

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return user.id

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return models.User.query.get(identity)

    from app.routes import main
    app.register_blueprint(main)

    def get_tenant_config(tenant):
        config = models.CondominioConfig.query.get(tenant)
        if not config:
            config = models.CondominioConfig(
                tenant=tenant,
                primary_color='#2c5aa0',
                nombre_comercial=tenant.replace('_', ' ').title()
            )
            db.session.add(config)
            db.session.commit()
            print(f"Configuración automática creada para: {tenant}")
        return config

    app.get_tenant_config = get_tenant_config

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app