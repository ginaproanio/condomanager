from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_migrate import Migrate
from datetime import timedelta
import os

from config import Config
from app.extensions import db

jwt = JWTManager()
cors = CORS()
migrate = Migrate()


def create_app():
    app = Flask(__name__)

    app.config.from_object(Config)

    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_SECURE'] = True
    app.config['JWT_COOKIE_SAMESITE'] = 'Lax'
    app.config['JWT_SESSION_COOKIE'] = False
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=12)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)
    app.config['JWT_COOKIE_CSRF_PROTECT'] = False # Considerar activar en producción

    database_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql+pg8000://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    print(f"Database URL: {app.config['SQLALCHEMY_DATABASE_URI']}")

    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, supports_credentials=True)

    from app import models
    
    # --- NUEVA LÓGICA: INYECCIÓN GLOBAL DE USUARIO ---
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity

    @app.context_processor
    def inject_user():
        """
        Inyecta la variable 'user' en todos los templates automáticamente.
        Verifica si existe un token JWT válido (cookie) sin romper la página si no lo hay.
        """
        try:
            # Verifica el token de forma opcional (no lanza error si falta)
            verify_jwt_in_request(optional=True)
            
            # Si hay token, buscamos el usuario
            user_id = get_jwt_identity()
            if user_id:
                current_user = models.User.query.get(int(user_id))
                return {'user': current_user}
        except Exception:
            # Si el token es inválido o expiró, simplemente no inyectamos usuario
            pass
            
        return {'user': None}

    @jwt.user_identity_loader
    def user_identity_lookup(user):
        return str(user)

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]  # "sub" es el ID del usuario
        return models.User.query.get(int(identity))

    with app.app_context():
        from . import routes
        routes.init_app(app)

    def get_tenant_config(tenant):
        if not tenant:
            return None
        config = models.CondominiumConfig.query.get(tenant)
        if not config:
            return None
        return config

    app.get_tenant_config = get_tenant_config

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()

    # --- ESTA ES LA CORRECCIÓN DE SEGURIDAD ---
    @app.after_request
    def add_security_headers(response):
        """
        Añade cabeceras a cada respuesta para prevenir el caché en el navegador.
        Esto soluciona el problema de poder usar el botón "atrás" después de cerrar sesión.
        """
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return app
