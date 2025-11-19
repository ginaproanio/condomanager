# app/routes/__init__.py
from .public_routes import public_bp
from .user_routes import user_bp
from .admin_routes import admin_bp
from .master_routes import master_bp
from .api_routes import api_bp
from .dev_routes import dev_bp # <-- AÑADIR ESTA LÍNEA

def init_app(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(master_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(dev_bp) # <-- Y AÑADIR ESTA