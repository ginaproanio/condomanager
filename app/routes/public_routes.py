from flask import (
    Blueprint, request, render_template, redirect, url_for,
    current_app, flash, make_response, g
)
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies
)
from app.models import User, db, Condominium
from app.extensions import limiter
import hashlib
from werkzeug.security import generate_password_hash # ✅ Importar la función correcta
from datetime import datetime, timedelta
import secrets # Para generar tokens seguros

public_bp = Blueprint('public', __name__)

@public_bp.route('/')
def home():
    condo = getattr(g, 'condominium', None)
    tenant_subdomain = condo.subdomain if condo else None
    config = current_app.get_tenant_config(tenant_subdomain)
    return render_template('home.html', config=config)

@public_bp.route('/solicitar-demo', methods=['GET', 'POST'])
def demo_request():
    config = current_app.get_tenant_config(getattr(g, 'condominium', None).subdomain if getattr(g, 'condominium', None) else None)

    if request.method == 'POST':
        # Recoger datos
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        cedula = request.form.get('cedula', '').strip()
        cellphone = request.form.get('cellphone', '').strip()
        password = request.form.get('password', '')

        # Validaciones básicas
        if not password:
            flash("La contraseña es obligatoria.", "warning")
            return redirect(url_for('public.demo_request'))
            
        if User.query.filter_by(email=email).first():
            flash("Este correo ya está registrado. Por favor inicia sesión.", "warning")
            return redirect(url_for('public.login'))
        
        if User.query.filter_by(cedula=cedula).first():
            flash("Esta cédula ya está registrada.", "warning")
            return redirect(url_for('public.login'))

        try:
            # 1. Crear Condominio Demo
            # Usar timestamp con segundos y sufijo aleatorio para evitar colisiones de unicidad
            timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
            random_suffix = secrets.token_hex(2) # Agrega 4 caracteres hex aleatorios
            safe_name = "".join([c for c in first_name if c.isalnum()])
            demo_subdomain = f"demo-{safe_name.lower()}-{timestamp}-{random_suffix}"
            
            # Token de validación simulado
            token = secrets.token_urlsafe(32)

            new_user = User(
                first_name=first_name,
                last_name=last_name,
                email=email,
                cedula=cedula,
                cellphone=cellphone,
                password_hash=generate_password_hash(password), # ✅ Usar el hashing seguro
                role='ADMIN', # Admin de su propia demo
                status='active', # Activo para que pueda entrar ya
                tenant=demo_subdomain,
                email_verified=False, # Pendiente validar
                verification_token=token,
                created_at=datetime.utcnow()
            )
            db.session.add(new_user)
            db.session.flush() # Para obtener el ID del usuario
            
            demo_condo = Condominium(
                name=f"Demo Condominio de {first_name}",
                legal_name=f"Demo {first_name} {last_name}",
                subdomain=demo_subdomain,
                status='DEMO', 
                environment='demo', # Separación estricta
                is_demo=True,       # Flag explícito
                admin_user_id=new_user.id,
                created_by=new_user.id,
                main_street="Calle Demo 1",
                cross_street="Av. Pruebas",
                city="Quito",
                country="Ecuador",
                trial_start_date=datetime.utcnow().date(),
                trial_end_date=(datetime.utcnow() + timedelta(days=15)).date(),
                has_documents_module=True,
                has_billing_module=True,
                has_requests_module=True
            )
            db.session.add(demo_condo)
            db.session.commit()

            # --- SIMULACIÓN DE ENVÍO DE CORREO Y SMS ---
            # En producción aquí se llamaría a send_email() y send_sms()
            current_app.logger.info(f"AUDIT: DEMO CREADA para {email}. Token: {token}")
            current_app.logger.info(f"AUDIT: SMS simulado enviado a {cellphone} con código 123456")

            flash(f"¡Tu demo está lista! Hemos enviado un correo de validación a {email}. (Simulado: Tu cuenta está activa por ahora)", "success")
            
            # Auto-Login opcional o redirección
            return redirect(url_for('public.login'))

        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error creando demo: {e}")
            flash("Ocurrió un error al crear tu demo. Intenta nuevamente.", "error")
            return redirect(url_for('public.demo_request'))

    return render_template('public/demo_request.html', config=config)

@public_bp.route('/verificar-email/<token>')
def verify_email(token):
    user = User.query.filter_by(verification_token=token).first()
    if not user:
        flash("Token de verificación inválido o expirado.", "error")
        return redirect(url_for('public.login'))
    
    user.email_verified = True
    user.verification_token = None # Consumir token
    db.session.commit()
    
    flash("¡Correo verificado correctamente! Ya puedes usar tu cuenta.", "success")
    return redirect(url_for('public.login'))

@public_bp.route('/health')
def health():
    return "OK", 200
