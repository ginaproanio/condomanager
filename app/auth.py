from flask import (
    Blueprint, render_template, flash, redirect, url_for, g, current_app, make_response
)
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies, get_jwt_identity, verify_jwt_in_request
from werkzeug.security import check_password_hash, generate_password_hash

from app.models import User
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
@limiter.limit("5 per minute") # REGLA: Previene ataques de fuerza bruta
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_lower = form.email.data.lower()
        
        try:
            # ✅ LÓGICA ANTI-PARALELISMO:
            # Si no hay subdominio (g.condominium es None), es un login "global" (MASTER en Railway/localhost).
            # Si hay subdominio, la query se filtra ESTRICTAMENTE por el condominium_id.
            user = User.query.filter_by(email=email_lower).first() if not g.condominium else \
                   User.query.filter_by(email=email_lower, condominium_id=g.condominium.id).first()
        except Exception as e:
            current_app.logger.error(f"Error DB during login: {str(e)}")
            flash('Error interno del servidor.', 'danger')
            return render_template('auth/login.html', form=form)

        if user and check_password_hash(user.password_hash, form.password.data):
            # ✅ REGLA DE ROLES: Verificar que la cuenta esté activa antes de crear la sesión.
            if user.status != 'active':
                flash('Tu cuenta se encuentra pendiente de aprobación o ha sido desactivada.', 'warning')
                current_app.logger.warning(f"Login denied for inactive/pending user: {email_lower}")
                return render_template('auth/login.html', form=form, error='Acceso denegado.')

            access_token = create_access_token(identity=str(user.id))
            response = make_response(redirect(url_for('user.dashboard'))) # Redirige al dashboard de usuario
            set_access_cookies(response, access_token)
            
            log_context = f"en subdominio {g.condominium.subdomain}" if g.condominium else "en dominio global"
            current_app.logger.info(f"Successful login for user {user.id} {log_context}.")
            if g.condominium and g.condominium.environment == 'sandbox':
                current_app.logger.info(f"Login detected in SANDBOX environment for user {user.id}.")

            return response
        else:
            current_app.logger.warning(f"Failed login attempt for {email_lower}.")
            return render_template('auth/login.html', form=form, error='Usuario o contraseña incorrectos.')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/registro', methods=['GET', 'POST'])
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
                tenant=g.condominium.subdomain if g.condominium else None,
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
