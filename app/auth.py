from flask import (
    Blueprint, render_template, flash, redirect, url_for, g, current_app, make_response, request
)
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import check_password_hash, generate_password_hash
 
from app.models import User, Condominium
from app.forms import LoginForm, RegistrationForm
from app.extensions import limiter, db

auth_bp = Blueprint('auth', __name__)

def get_current_user():
    """
    Devuelve la instancia User asociada con el JWT actual si existe,
    o None si no hay token/usuario.
    """
    try:
        # Usar verify_jwt_in_request(optional=True) para no forzar un error si no hay token
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if not identity:
            return None
        # La identidad se guarda como str(user.id), por eso se convierte a int
        user = User.query.get(int(identity))
        return user
    except Exception as e:
        current_app.logger.debug(f"get_current_user error: {e}")
        return None

@auth_bp.route('/ingresar', methods=['GET', 'POST'])
@limiter.limit("5 per minute", key_func=lambda: request.remote_addr or "test")
def login():
    form = LoginForm()

    if form.validate_on_submit():
        email_lower = form.email.data.lower()
        try:
            # --- LÓGICA DE BÚSQUEDA CORREGIDA ---
            if g.get('condominium'):
                # Si estamos en un subdominio, la búsqueda es estricta para ese tenant.
                user = User.query.filter_by(email=email_lower, condominium_id=g.condominium.id).first()
            else:
                # Si estamos en el dominio principal, buscamos el usuario por email en CUALQUIER tenant.
                user = User.query.filter_by(email=email_lower).first()
 
            if user and check_password_hash(user.password_hash, form.password.data):
                if user.status != 'active':
                    flash('Tu cuenta se encuentra pendiente de aprobación o ha sido desactivada.', 'warning')
                    current_app.logger.warning(f"Login denied for inactive/pending user: {email_lower}")
                    return render_template('auth/login.html', form=form)
                else:
                    access_token = create_access_token(identity=str(user.id))
                    # Redirección segura para evitar Open Redirect
                    next_url = request.args.get('next') # TODO: Añadir validación is_safe_url

                    # --- SOLUCIÓN ARQUITECTURAL: Redirección por Rol ---
                    redirect_url = url_for('user.dashboard') # Destino por defecto para USER
                    
                    if user.role == 'MASTER':
                        redirect_url = url_for('master.master_panel')
                    elif user.role == 'ADMIN':
                        admin_condo = Condominium.query.filter_by(admin_user_id=user.id).first()
                        if admin_condo:
                            # --- ARQUITECTURA PATH-BASED PARA RAILWAY ---
                            # Redirigir a /<slug_condominio>/admin/panel
                            redirect_url = url_for('admin.admin_condominio_panel', tenant_slug=admin_condo.subdomain)
                    response = make_response(redirect(next_url or redirect_url))
                    set_access_cookies(response, access_token)
                    
                    log_context = f"en subdominio {g.condominium.subdomain}" if g.condominium else "en dominio global"
                    current_app.logger.info(f"Successful login for user_id={user.id} in context: {log_context}.")
                    return response
            # Mensaje de error genérico fuera del bloque `if user` para evitar enumeración de usuarios
            flash('Usuario o contraseña incorrectos.', 'danger')
            current_app.logger.warning(f"Failed login attempt for email: {email_lower}.")
 
        except Exception as e:
            current_app.logger.error(f"Database error during login: {str(e)}")
            flash('Error interno del servidor.', 'danger')

    # Para peticiones GET o si la validación del formulario falla, SIEMPRE se pasa el 'form'.
    return render_template('auth/login.html', form=form)

@auth_bp.route('/registro', methods=['GET', 'POST'])
@limiter.limit("3 per hour") # REGLA: Previene spam de registros
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data)
            new_user = User(
                first_name=form.first_name.data,
                last_name=form.last_name.data,
                cedula=form.cedula.data,
                email=form.email.data.lower(),
                password_hash=hashed_password,
                role='USER',
                status='pending', # REGLA DE NEGOCIO: Los usuarios nuevos esperan aprobación
                condominium_id=g.condominium.id if g.condominium else None
            )
            db.session.add(new_user)
            db.session.commit() # REGLA: Transacción atómica
            flash('¡Registro exitoso! Tu cuenta está pendiente de aprobación por el administrador.', 'success')
            return redirect(url_for('auth.login'))
        except ValueError as e:
            flash(str(e), 'danger')
        except Exception as e:
            db.session.rollback() # REGLA: Atomicidad en caso de error
            current_app.logger.error(f"Error inesperado durante el registro: {str(e)}")
            flash('Ocurrió un error al procesar tu registro. Por favor, inténtalo de nuevo.', 'danger')
            
    return render_template('auth/registro.html', form=form)

@auth_bp.route('/salir')
def logout():
    response = make_response(redirect(url_for('public.home')))
    unset_jwt_cookies(response)
    flash('Has cerrado sesión exitosamente.', 'success')
    return response
