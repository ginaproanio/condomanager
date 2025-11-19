from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import os

from config import Config
from app.extensions import db
# from app.models import User, Condominium, Unit, CondominioConfig  # Ya no se importan aquí directamente

jwt = JWTManager()
cors = CORS()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    # Imprimir variables de entorno para depuración
    print(f"DEBUG: SECRET_KEY = {app.config.get('SECRET_KEY')}")
    print(f"DEBUG: JWT_SECRET_KEY = {app.config.get('JWT_SECRET_KEY')}")

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

    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app) # Inicializar db con la app
    jwt.init_app(app)
    cors.init_app(app, supports_credentials=True)

    # Importar app.models aquí para registrar los modelos con SQLAlchemy
    # Esto debe hacerse DESPUÉS de db.init_app(app) y ANTES de que las rutas lo necesiten
    from app import models

    @jwt.user_identity_loader
    def user_identity_lookup(user_id):
        return user_id  # Ya es el ID del usuario

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return models.User.query.get(identity)

    # Importar y registrar blueprints DENTRO de la fábrica para evitar importaciones circulares
    with app.app_context():
        from . import routes
        routes.init_app(app)
    def get_tenant_config(tenant):
        config = models.CondominiumConfig.query.get(tenant)
        if not config:
            config = models.CondominiumConfig(
                tenant=tenant,
                primary_color='#2c5aa0',
                commercial_name=tenant.replace('_', ' ').title()
            )
            db.session.add(config)
            db.session.commit()
            print(f"Automatic config created for tenant: {tenant}")
        return config

    app.get_tenant_config = get_tenant_config

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    return app