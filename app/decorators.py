from functools import wraps
from flask import flash, redirect, url_for, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Condominium # Importar modelos necesarios

def get_current_user_from_jwt():
    """Safely gets the current user from the JWT."""
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    return User.query.get(int(user_id))

def login_required(f):
    """
    Decorator para rutas que requieren que el usuario esté autenticado.
    Redirige a /login si no hay un token JWT válido o el usuario no existe.
    Pasa el objeto de usuario como argumento 'current_user' a la función de la ruta.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        user = get_current_user_from_jwt()
        if user is None:
            flash("Sesión inválida o expirada. Por favor, inicia sesión de nuevo.", "error")
            return redirect(url_for('public.login')) # Ya estaba correcto, se mantiene
        kwargs['current_user'] = user # Pasar el usuario al wrapped function
        return f(*args, **kwargs)
    return decorated_function

def master_required(f):
    """
    Decorator para rutas que requieren el rol 'MASTER'.
    Se basa en login_required para asegurar la autenticación y pasa el usuario.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = kwargs.get('current_user') # Obtener el usuario del decorador login_required
        if user is None or user.role != 'MASTER':
            flash("Acceso denegado. Se requiere rol MASTER.", "error")
            return redirect(url_for('user.dashboard')) # CORREGIDO: de 'main' a 'user'
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """
    Decorator para rutas que requieren el rol 'ADMIN' (o MASTER como superusuario).
    Se basa en login_required y pasa el usuario.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = kwargs.get('current_user')
        # Un MASTER puede acceder a las funcionalidades de ADMIN
        if user is None or user.role not in ['ADMIN', 'MASTER']:
            flash("Acceso denegado. Se requiere rol ADMIN o MASTER.", "error")
            return redirect(url_for('user.dashboard')) # CORREGIDO: de 'main' a 'user'
        return f(*args, **kwargs)
    return decorated_function

def condominium_admin_required(f):
    """
    Decorator para rutas que requieren el rol 'ADMIN' y estar asignado a un condominio específico.
    Se basa en admin_required para asegurar el rol y pasa el usuario.
    La función de la ruta debe aceptar 'condominium_id' como argumento.
    """
    @wraps(f)
    @admin_required
    def decorated_function(*args, **kwargs):
        user = kwargs.get('current_user')
        # Asume que el ID del condominio viene en los argumentos de la ruta (ej. /condo/<int:condo_id>/dashboard)
        condominium_id = kwargs.get('condo_id') or kwargs.get('condominium_id')

        if user.role == 'MASTER':
            # El rol MASTER tiene acceso a todo, no necesita más validaciones.
            return f(*args, **kwargs)

        if not condominium_id:
            current_app.logger.error(f"Ruta protegida por 'condominium_admin_required' no recibió 'condo_id'.")
            flash("Error de configuración de la ruta.", "error")
            return redirect(url_for('user.dashboard')) # CORREGIDO: de 'main' a 'user'

        condo = Condominium.query.filter_by(id=condominium_id, admin_user_id=user.id).first()
        if not condo:
            flash("Acceso denegado. No está autorizado para gestionar este condominio.", "error")
            return redirect(url_for('user.dashboard')) # CORREGIDO: de 'main' a 'user'
        return f(*args, **kwargs)
    return decorated_function
