# app/routes/__init__.py
from .public_routes import public_bp
from .user_routes import user_bp
from .admin_routes import admin_bp
from .master_routes import master_bp
from .api_routes import api_bp
from .document_routes import document_bp
from .payment_routes import payment_bp
from .petty_cash_routes import petty_cash_bp
from .google_drive_routes import google_drive_bp

# --- REGISTRO DE BLUEPRINT DE AUTENTICACIÓN ---
from ..auth import auth_bp

def init_app(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(master_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(auth_bp) # Monta /ingresar, /registro, /salir
    app.register_blueprint(document_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(petty_cash_bp)
    app.register_blueprint(google_drive_bp)