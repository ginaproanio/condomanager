from flask import (
    Blueprint, request, render_template, redirect, url_for,
    current_app, flash
)
from flask_jwt_extended import (
    unset_jwt_cookies
)
from app.models import User, db
import hashlib
from datetime import datetime

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('home.html', config=config)

@public_bp.route('/registro', methods=['GET', 'POST'])
def register(): # El nombre ya era correcto, se mantiene
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)

    if request.method == 'POST':
        # --- 1. Recolectar todos los datos del formulario ---
        email = request.form.get('email', '').strip().lower()
        cedula = request.form.get('cedula', '').strip()
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        password = request.form.get('password')
        cellphone = request.form.get('cellphone', '').strip()
        birth_date_str = request.form.get('birth_date')
        city = request.form.get('city', '').strip()
        country = request.form.get('country', '').strip()

        # --- 2. Validar que la cédula y el email no existan ---
        if User.query.filter_by(email=email).first():
            flash("El correo electrónico ya está registrado.", "danger")
            return render_template('auth/registro.html', config=config, **request.form)
        
        if User.query.filter_by(cedula=cedula).first():
            flash("La cédula ya está registrada.", "danger")
            return render_template('auth/registro.html', config=config, **request.form)

        # --- 3. Procesar campos especiales (como la fecha) ---
        birth_date = None
        if birth_date_str:
            try:
                birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
            except ValueError:
                flash("El formato de la fecha de nacimiento es inválido.", "danger")
                return render_template('auth/registro.html', config=config, **request.form)

        # --- 4. Crear la nueva instancia de Usuario con todos los campos ---
        new_user = User(
            cedula=cedula,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password_hash=hashlib.sha256(password.encode()).hexdigest(),
            birth_date=birth_date,
            cellphone=cellphone,
            city=city,
            country=country,
            tenant=tenant,
            role='USER',
            status='PENDING'
        )

        db.session.add(new_user)
        db.session.commit()
        flash("¡Registro exitoso! Tu cuenta está pendiente de aprobación por el administrador.", "success")
        return redirect(url_for('public.login'))

    return render_template('auth/registro.html', config=config)

@public_bp.route('/login', methods=['GET', 'POST'])
def login():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    # La lógica de procesamiento del login ahora es manejada 100% por la API
    # en /api/auth/login. Esta ruta solo muestra la plantilla.
    return render_template('auth/login.html', config=config)

@public_bp.route('/logout')
def logout():
    response = redirect(url_for('public.login'))
    unset_jwt_cookies(response)
    flash("Has cerrado sesión correctamente", "info")
    return response

@public_bp.route('/health')
def health():
    return "OK", 200
