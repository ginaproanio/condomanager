from functools import wraps
from flask import flash, redirect, url_for, current_app, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User, Condominium, UserSpecialRole, Module # Importar modelo Module
from datetime import date, datetime

def get_current_user_from_jwt():
    """Safely gets the current user from the JWT."""
    user_id = get_jwt_identity()
    if user_id is None:
        return None
    # Usamos .with_for_update() para un bloqueo pesimista si es necesario en transacciones complejas.
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
            return redirect(url_for('auth.login'))
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
        if user is None or user.role.upper() != 'MASTER': # Usar upper() para consistencia
            flash("Acceso denegado. Se requiere rol MASTER.", "error")
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function

def module_required(module_name):
    """
    Decorator para rutas que pertenecen a un módulo contratable.
    Verifica si el módulo está activo para el condominio del usuario.
    Ejemplo de uso: @module_required('documents')
    """
    def decorator(f):
        @wraps(f)
        @login_required # Asegura que el usuario esté logueado primero
        def decorated_function(*args, **kwargs):
            user = kwargs.get('current_user')
 
            # El rol MASTER siempre tiene acceso a todos los módulos.
            if user.role.upper() == 'MASTER':
                return f(*args, **kwargs)
 
            # La lógica de tenant es la forma correcta de encontrar el condominio
            condominium = Condominium.query.filter_by(subdomain=user.tenant).first()
            if not condominium:
                flash("No estás asociado a ningún condominio.", "error")
                return redirect(url_for('user.dashboard'))
            
            # --- NUEVA LÓGICA ROBUSTA DE MANTENIMIENTO GLOBAL ---
            # 1. Verificar estado GLOBAL del módulo en el catálogo (Tabla Module)
            # Usamos el 'code' (ej. 'documents') para buscar el módulo.
            global_module = Module.query.filter_by(code=module_name).first()
            if global_module and global_module.maintenance_mode:
                flash(f"El módulo '{global_module.name}' está temporalmente en mantenimiento por mejoras en la plataforma.", "warning")
                return redirect(url_for('user.dashboard'))
 
            # --- LÓGICA DE PERMISOS CENTRALIZADA ---
            # 2. Verificar si el módulo está activo para el condominio (contratado).
            # Esta es la implementación actual. En el futuro, se consultará la tabla `CondominiumModuleActivation`.
            module_flag = f"has_{module_name}_module"
            if not getattr(condominium, module_flag, False):
                flash(f"El módulo '{module_name.replace('_', ' ').title()}' no está activado para tu condominio.", "error")
                return redirect(url_for('user.dashboard'))
 
            # 3. Si el módulo está activo, verificar si el usuario tiene un rol que le dé acceso.
            # El rol ADMIN siempre tiene acceso si el módulo está activo.
            if user.role.upper() == 'ADMIN':
                return f(*args, **kwargs)
 
            # 4. Verificar si el usuario tiene un ROL ESPECIAL vigente que le dé permiso.
            # Esta sección es clave para la escalabilidad.
            # Por ahora, definimos aquí qué roles especiales acceden a qué módulos.
            # En el futuro, esto se leerá de una tabla en la base de datos.
            special_roles_for_module = {
                'documents': ['PRESIDENTE', 'SECRETARIO']
                # 'billing': ['TESORERO'], # Ejemplo a futuro
            }.get(module_name, [])
 
            if special_roles_for_module:
                has_valid_special_role = UserSpecialRole.query.filter(
                    UserSpecialRole.user_id == user.id,
                    UserSpecialRole.condominium_id == condominium.id,
                    UserSpecialRole.role.in_(special_roles_for_module),
                    UserSpecialRole.is_active == True,
                    UserSpecialRole.start_date <= date.today(),
                    (UserSpecialRole.end_date == None) | (UserSpecialRole.end_date >= date.today())
                ).first()
 
                if has_valid_special_role:
                    return f(*args, **kwargs)
 
            # Si no es MASTER, ni ADMIN, ni tiene un rol especial válido, se deniega el acceso.
            flash("No tienes los permisos necesarios para acceder a este módulo.", "error")
            return redirect(url_for('user.dashboard'))
        return decorated_function
    return decorator

def admin_required(f):
    """
    Decorator para rutas que requieren el rol 'ADMIN' (o MASTER como superusuario).
    Se basa en login_required y pasa el usuario.
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user = kwargs.get('current_user')
        if user is None or user.role.upper() != 'ADMIN':
            flash("Acceso denegado. Se requiere rol de Administrador.", "error")
            return redirect(url_for('user.dashboard'))
        return f(*args, **kwargs)
    return decorated_function
