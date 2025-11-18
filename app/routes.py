from flask import (
    Blueprint, request, render_template, redirect, url_for,
    current_app, jsonify, make_response, flash, Response
)
from flask_jwt_extended import (
    create_access_token, set_access_cookies, unset_jwt_cookies,
    jwt_required, get_jwt_identity
)
from app import db
from app.models import User, Condominium, Unit
import hashlib
from datetime import datetime, timedelta
import csv
import io

main = Blueprint('main', __name__)

# =============================================================================
# RUTAS PÚBLICAS
# =============================================================================

@main.route('/')
def home():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('home.html', config=config)

@main.route('/registro', methods=['GET', 'POST'])
def registro():
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

@main.route('/login', methods=['GET'])
def login():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('auth/login.html', config=config)

@main.route('/api/auth/login', methods=['POST'])
def api_login():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant) # Se usa el config para flash messages, pero para API no es necesario

    # En una API RESTful, esperamos JSON
    data = request.get_json()
    if not data or not 'email' in data or not 'password' in data:
        return jsonify({"error": "Faltan datos de email o contraseña."}), 400

    email = data['email'].strip()
    password = data['password']
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()

    try:
        from app import models
        user = models.User.query.filter_by(email=email, password_hash=pwd_hash).first()
    except Exception as e:
        current_app.logger.error(f"Error de base de datos durante el login para {email}: {e}")
        return jsonify({"error": "Error de conexión con la base de datos."}), 500

    if not user:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if user.status != 'active':
        return jsonify({"error": "Tu cuenta está pendiente de aprobación o fue rechazada"}), 403

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=12)) # Convertir a string
    
    # Establecer la cookie JWT directamente desde el backend y luego redirigir
    response = make_response(redirect(url_for('main.dashboard')))
    set_access_cookies(response, access_token)
    return response

@main.route('/logout')
def logout():
    response = make_response(redirect('/login'))
    unset_jwt_cookies(response)
    flash("Has cerrado sesión correctamente", "info")
    return response

# =============================================================================
# FUNCIÓN AUXILIAR: obtener usuario actual de forma segura
# =============================================================================
def get_current_user():
    """Obtiene el usuario actual de forma segura (compatible con JWT que guarda solo ID)"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(int(user_id))

# =============================================================================
# RUTAS PROTEGIDAS
# =============================================================================

@main.route('/dashboard')
@jwt_required()
def dashboard():
    user = get_current_user()
    if not user:
        flash("Sesión inválida", "error")
        return redirect('/login')
    
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('user/dashboard.html', user=user, config=config)

@main.route('/admin')
@jwt_required()
def admin_panel():
    user = get_current_user()
    if not user or user.role not in ['ADMIN', 'MASTER']:
        flash("Acceso denegado", "error")
        return redirect('/dashboard')

    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)

    pending = User.query.filter_by(status='pending').all()
    active = User.query.filter_by(status='active').count()
    rejected = User.query.filter_by(status='rejected').count()

    return render_template('admin/panel.html',
                           pending_users=pending,
                           active_count=active,
                           rejected_count=rejected,
                           user=user,
                           config=config)

@main.route('/aprobar/<int:user_id>')
@jwt_required()
def aprobar_usuario(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role not in ['ADMIN', 'MASTER']:
        return redirect('/dashboard')
    user = User.query.get_or_404(user_id)
    user.status = 'active'
    db.session.commit()
    flash(f"Usuario {user.email} aprobado", "success")
    return redirect('/admin')

@main.route('/rechazar/<int:user_id>')
@jwt_required()
def rechazar_usuario(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role not in ['ADMIN', 'MASTER']:
        return redirect('/dashboard')
    user = User.query.get_or_404(user_id)
    user.status = 'rejected'
    db.session.commit()
    flash(f"Usuario {user.email} rechazado", "info")
    return redirect('/admin')

@main.route('/master')
@jwt_required()
def master_panel():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    
    try:
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
    except Exception as e:
        current_app.logger.error(f"Error loading master panel for user {user.id if user else 'N/A'}: {e}")
        flash("Error al cargar el panel maestro", "error")
        return redirect('/dashboard')

    return render_template('master/panel.html', user=user, config=config)

# =============================================================================
# API Y RUTAS MASTER
# =============================================================================

@main.route('/api/auth/me')
@jwt_required()
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 401
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "status": user.status
    })

@main.route('/api/master/estadisticas')
@jwt_required()
def api_master_estadisticas():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        return jsonify({"error": "Acceso denegado"}), 403
    try:
        total_condominios = Condominium.query.count()
        total_usuarios = User.query.count()
        usuarios_pendientes = User.query.filter_by(status='pending').count()
        unidades_totales = Unit.query.count()

        # Para mostrar en el frontend, se espera 'condominios_activos' y 'condominios_pendientes'
        # que no están en la API actual. Podríamos calcularlos aquí o agregarlos al modelo de Condominium.
        # Por ahora, usaré valores por defecto o ceros si no tenemos esa data.
        condominios_activos = Condominium.query.filter_by(status='ACTIVO').count() # Asumiendo un campo de estado
        condominios_pendientes = Condominium.query.filter_by(status='PENDIENTE_APROBACION').count() # Asumiendo un campo de estado
        
        # Obtener condominios recientes (por ejemplo, los últimos 5)
        condominios_recientes = Condominium.query.order_by(Condominium.created_at.desc()).limit(5).all()
        condominios_recientes_data = [
            {'name': c.name, 'status': c.status, 'total_usuarios': len(c.units), 'created_at': c.created_at.isoformat()}
            for c in condominios_recientes
        ] # Asumiendo 'units' es una relación y 'status' existe

        return jsonify({
            "total_condominios": total_condominios,
            "total_usuarios": total_usuarios,
            "usuarios_pendientes": usuarios_pendientes,
            "unidades_totales": unidades_totales,
            "condominios_activos": condominios_activos,
            "condominios_pendientes": condominios_pendientes,
            "condominios_recientes": condominios_recientes_data
        })
    except Exception as e:
        current_app.logger.error(f"Error al obtener estadísticas del maestro: {e}")
        return jsonify({"error": "Error interno del servidor al obtener estadísticas"}), 500

@main.route('/master/descargar-plantilla-unidades')
@jwt_required()
def descargar_plantilla_unidades():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        return jsonify({"error": "Acceso denegado"}), 403

    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = ['property_number', 'name', 'property_type', 'main_street', 'cross_street', 
               'house_number', 'address_reference', 'latitude', 'longitude', 'building', 
               'floor', 'sector', 'area_m2', 'area_construction_m2', 'bedrooms', 'bathrooms', 
               'parking_spaces', 'front_meters', 'depth_meters', 'topography', 'land_use', 'notes']
    writer.writerow(headers)
    
    examples = [
        ['A-101', 'Apartamento 101', 'apartamento', 'Av. Principal', 'Calle 2', '101', '', '-2.123', '-79.123', 'Torre A', '10', '', '85.5', '75.0', '2', '2', '1', '', '', '', '', ''],
        ['C-25', 'Casa 25', 'casa', 'Av. Las Palmeras', 'Calle Los Pinos', '25', '', '-2.124', '-79.124', '', '', 'Manzana B', '120.0', '100.0', '3', '2', '2', '', '', '', '', '']
    ]
    for row in examples:
        writer.writerow(row)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=plantilla_unidades.csv"}
    )

@main.route('/health')
def health():
    return "OK", 200

@main.route('/unidades')
def unidades():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/unidades.html', mensaje="Gestión de Unidades", config=config)

@main.route('/pagos')
def pagos():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/pagos.html', mensaje="Sistema de Pagos", config=config)

@main.route('/reportes')
def reportes():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/reportes.html', mensaje="Reportes", config=config)

@main.route('/condominiums', methods=['GET'])
def get_condominiums():
    try:
        condominiums = Condominium.query.all()
        return jsonify([condo.to_dict() for condo in condominiums])
    except Exception as e:
        return jsonify({'error': 'Error al obtener condominios'}), 500