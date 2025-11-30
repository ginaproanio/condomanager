from functools import wraps
from flask import flash, redirect, url_for, current_app, abort, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request
from app.models import User, Condominium, UserSpecialRole, Module # Importar modelo Module
from datetime import date, datetime

def get_current_user_from_jwt():
    """Safely gets the current user from the JWT."""
    verify_jwt_in_request(optional=True)
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return User.query.get(int(user_id))

def admin_tenant_required(f):
    """
    Decorador definitivo para rutas de administración de un tenant.
    Verifica en orden:
    1. Autenticación JWT.
    2. Existencia de un tenant en `g.condominium`.
    3. Que el usuario sea el ADMIN asignado a ese tenant.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user = get_current_user_from_jwt()
        condominium = getattr(g, 'condominium', None)

        if not condominium:
            abort(404, "Se requiere un contexto de condominio (subdominio).")

        if not (user and user.role == 'ADMIN' and condominium.admin_user_id == user.id):
            abort(403, "Acceso denegado. No eres el administrador de este condominio.")
        
        return f(*args, **kwargs)
    return decorated_function
