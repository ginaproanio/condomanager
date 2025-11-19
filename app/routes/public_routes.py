from flask import (
    Blueprint, request, render_template, redirect, url_for,
    current_app, flash, make_response
)
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies
)
from app import db
from app.models import User
import hashlib
from datetime import timedelta

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
        email = request.form['email'].strip()
        name = request.form.get('name', '').strip()
        password = request.form['password']
        phone = request.form.get('phone', '')
        city = request.form.get('city', '')
        country = request.form.get('country', 'Ecuador')

        if User.query.filter_by(email=email).first():
            flash("Este email ya está registrado", "error")
            return render_template('auth/registro.html', config=config)

        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        user = User(
            email=email,
            name=name or email.split('@')[0],
            phone=phone,
            city=city,
            country=country,
            password_hash=pwd_hash,
            tenant=tenant,
            role='USER',
            status='pending'
        )
        db.session.add(user)
        db.session.commit()
        flash("Registro exitoso. Tu cuenta está pendiente de aprobación.", "success")
        return render_template('auth/registro.html', config=config)

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
    response = make_response(redirect('/login'))
    unset_jwt_cookies(response)
    flash("Has cerrado sesión correctamente", "info")
    return response

@public_bp.route('/health')
def health():
    return "OK", 200
