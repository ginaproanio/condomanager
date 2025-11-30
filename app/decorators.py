from functools import wraps
from flask import abort, g
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request

def login_required(f):
    """
    Decorador simple que solo verifica que un usuario esté autenticado vía JWT.
    Es un alias para @jwt_required() para mantener la consistencia.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # La validación la hace @jwt_required, aquí solo pasamos la ejecución.
        return f(*args, **kwargs)
    return decorated_function

# El decorador admin_tenant_required ya está aquí y es correcto.
# ...

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
        # Importación local para romper dependencias circulares
        from app.models import User
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id)) if user_id else None

        condominium = getattr(g, 'condominium', None)

        if not condominium:
            abort(404, "Se requiere un contexto de condominio (subdominio).")

        if not (user and user.role == 'ADMIN' and condominium.admin_user_id == user.id):
            abort(403, "Acceso denegado. No eres el administrador de este condominio.")
        
        return f(*args, **kwargs)
    return decorated_function

# El decorador master_required ya está aquí y es correcto.
# ...
def master_required(f):
    """
    Decorador para rutas del panel MASTER.
    Verifica que el usuario esté autenticado y tenga el rol 'MASTER'.
    """
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        # Importación local para romper dependencias circulares
        from app.models import User
        user_id = get_jwt_identity()
        user = User.query.get(int(user_id)) if user_id else None

        if not (user and user.role == 'MASTER'):
            abort(403, "Acceso denegado. Se requiere rol de MASTER.")
        
        # Opcional: Verificar que no haya un contexto de tenant
        if getattr(g, 'condominium', None):
            abort(400, "Las rutas MASTER no deben tener un contexto de condominio.")

        return f(*args, **kwargs)
    return decorated_function

def module_required(module_name):
    """
    Decorador factory para verificar si un módulo específico está activo
    para el condominio actual en el contexto `g`.
    """
    def decorator(f):
        @wraps(f)
        # Este decorador asume que otro decorador como @admin_tenant_required ya se ha ejecutado
        # y ha validado el usuario y el condominio.
        def decorated_function(*args, **kwargs):
            condominium = getattr(g, 'condominium', None)
            if not condominium:
                abort(403, "Se requiere un contexto de condominio para verificar el módulo.")

            # Importación local para evitar ciclos
            from app.models import Module

            # Verificar si el módulo está activo para este condominio
            module_is_active = Module.query.filter_by(
                condominium_id=condominium.id,
                name=module_name,
                is_active=True
            ).first()

            if not module_is_active:
                abort(403, f"El módulo '{module_name}' no está activo o no existe para este condominio.")
            
            return f(*args, **kwargs)
        return decorator
    return decorator
