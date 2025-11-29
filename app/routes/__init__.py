# app/routes/__init__.py
from .public_routes import public_bp
from .user_routes import user_bp
from ..auth import auth_bp
from .admin_routes import admin_bp
from .master_routes import master_bp
from .api_routes import api_bp
from .document_routes import document_bp
from .payment_routes import payment_bp
from .petty_cash_routes import petty_cash_bp
from .google_drive_routes import google_drive_bp

# Lista única y centralizada de todos los blueprints de la aplicación.
# A prueba de fallos: si un blueprint se añade aquí, se registrará.
all_blueprints = [
    public_bp, user_bp, auth_bp, admin_bp, master_bp, 
    api_bp, document_bp, payment_bp, petty_cash_bp, google_drive_bp
]