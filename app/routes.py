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

    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(hours=12))
    
    # Redirigir según el rol del usuario
    if user.role == 'MASTER':
        redirect_url = url_for('main.master_panel')
    elif user.role == 'ADMIN':
        redirect_url = url_for('main.admin_panel')
    else:
        redirect_url = url_for('main.dashboard')

    response = make_response(redirect(redirect_url))
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
    
    # Si es ADMIN, redirigir a su panel de condominio específico
    if user.role == 'ADMIN' and user.condominium_id: # Suponiendo que el usuario ADMIN tiene un campo condominium_id
        return redirect(url_for('main.admin_condominio_panel', condominium_id=user.condominium_id))

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

# Nueva ruta para el panel de administración de un condominio específico
@main.route('/admin/condominio/<int:condominium_id>', methods=['GET', 'POST'])
@jwt_required()
def admin_condominio_panel(condominium_id):
    user = get_current_user()
    # Verificar que el usuario es ADMIN y está asignado a este condominio
    if not user or user.role != 'ADMIN' or user.condominium_id != condominium_id:
        flash("Acceso denegado o condominio no autorizado.", "error")
        return redirect('/dashboard')

    condominium = Condominium.query.get_or_404(condominium_id)
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)

    # Lógica para GET: mostrar el panel con las unidades y usuarios existentes
    if request.method == 'GET':
        units = Unit.query.filter_by(condominium_id=condominium.id).all()
        users_in_condo = User.query.filter_by(condominium_id=condominium.id).all()
        return render_template('admin/condominio_panel.html', user=user, config=config, condominium=condominium, units=units, users_in_condo=users_in_condo)

    # Lógica para POST: procesar carga masiva de unidades o usuarios
    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'import_units_csv':
            uploaded_file = request.files.get('csv_file')
            if not uploaded_file or uploaded_file.filename == '':
                flash("No se seleccionó ningún archivo CSV para importar unidades.", "error")
                return redirect(url_for('main.admin_condominio_panel', condominium_id=condominium_id))

            if uploaded_file and uploaded_file.filename.endswith('.csv'):
                try:
                    content = uploaded_file.read().decode('utf-8')
                    csv_reader = csv.DictReader(io.StringIO(content))
                    
                    created_count = 0
                    failed_count = 0
                    for row in csv_reader:
                        # Asegúrate de que las columnas del CSV coincidan con los campos de tu modelo Unit
                        # Ejemplo de campos: property_number, name, property_type, area_m2, bedrooms, bathrooms, etc.
                        property_number = row.get('property_number', '').strip()
                        name = row.get('name', '').strip()
                        property_type = row.get('property_type', '').strip()
                        area_m2 = row.get('area_m2', 0)
                        bedrooms = row.get('bedrooms', 0)
                        bathrooms = row.get('bathrooms', 0)
                        # ... otros campos de Unit que quieras importar ...

                        if not property_number or not name:
                            failed_count += 1
                            continue

                        try:
                            new_unit = Unit(
                                property_number=property_number,
                                name=name,
                                property_type=property_type,
                                area_m2=float(area_m2),
                                bedrooms=int(bedrooms),
                                bathrooms=int(bathrooms),
                                condominium_id=condominium.id # Asignar al condominio del ADMIN
                                # ... otros campos ...
                            )
                            db.session.add(new_unit)
                            created_count += 1
                        except Exception as e:
                            current_app.logger.error(f"Error al importar unidad '{property_number}' (fila {csv_reader.line_num}): {e}")
                            failed_count += 1

                    db.session.commit()
                    flash(f"Importación de unidades completada. {created_count} unidades creadas, {failed_count} fallidas.", "success")

                except Exception as e:
                    current_app.logger.error(f"Error al leer o procesar el archivo CSV de unidades: {e}")
                    flash(f"Error al leer o procesar el archivo CSV de unidades: {e}", "error")
            else:
                flash("El archivo seleccionado no es un archivo CSV válido para unidades.", "error")

        elif action == 'import_users_csv':
            uploaded_file = request.files.get('csv_file')
            if not uploaded_file or uploaded_file.filename == '':
                flash("No se seleccionó ningún archivo CSV para importar usuarios.", "error")
                return redirect(url_for('main.admin_condominio_panel', condominium_id=condominium_id))

            if uploaded_file and uploaded_file.filename.endswith('.csv'):
                try:
                    content = uploaded_file.read().decode('utf-8')
                    csv_reader = csv.DictReader(io.StringIO(content))

                    created_count = 0
                    failed_count = 0
                    for row in csv_reader:
                        # Columnas esperadas en el CSV para usuarios: email, name, password, phone, unit_property_number
                        email = row.get('email', '').strip()
                        name = row.get('name', '').strip()
                        password = row.get('password', '').strip()
                        phone = row.get('phone', '').strip()
                        unit_property_number = row.get('unit_property_number', '').strip()

                        if not email or not name or not unit_property_number:
                            failed_count += 1
                            continue
                        
                        # Verificar si el email ya existe
                        if User.query.filter_by(email=email).first():
                            flash(f"Error: El email {email} ya existe. Saltando.", "warning")
                            failed_count += 1
                            continue

                        # Buscar la unidad por property_number dentro del condominio del ADMIN
                        unit = Unit.query.filter_by(condominium_id=condominium.id, property_number=unit_property_number).first()
                        if not unit:
                            current_app.logger.error(f"Unidad con número de propiedad {unit_property_number} no encontrada en condominio {condominium.name}. Saltando usuario {email}.")
                            flash(f"Error: Unidad {unit_property_number} no encontrada para el usuario {email}.", "warning")
                            failed_count += 1
                            continue

                        try:
                            pwd_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
                            new_user_unit = User(
                                email=email,
                                name=name,
                                password_hash=pwd_hash,
                                phone=phone,
                                city=condominium.city, # Asumir la ciudad del condominio
                                country=condominium.country, # Asumir el país del condominio
                                tenant=condominium.tenant,
                                role='USER', # Siempre son USERs de unidad
                                status='active', # Se asumen activos al importar
                                condominium_id=condominium.id, # Asignar al condominio del ADMIN
                                unit_id=unit.id # Asignar a la unidad encontrada
                            )
                            db.session.add(new_user_unit)
                            created_count += 1
                        except Exception as e:
                            current_app.logger.error(f"Error al importar usuario {email} (fila {csv_reader.line_num}): {e}")
                            failed_count += 1

                    db.session.commit()
                    flash(f"Importación de usuarios completada. {created_count} usuarios creados, {failed_count} fallidos.", "success")

                except Exception as e:
                    current_app.logger.error(f"Error al leer o procesar el archivo CSV de usuarios: {e}")
                    flash(f"Error al leer o procesar el archivo CSV de usuarios: {e}", "error")
            else:
                flash("El archivo seleccionado no es un archivo CSV válido para usuarios.", "error")
        
        return redirect(url_for('main.admin_condominio_panel', condominium_id=condominium_id))

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
    # Redirección inteligente
    if current_user.role == 'MASTER':
        return redirect('/master/usuarios')
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
    # Redirección inteligente
    if current_user.role == 'MASTER':
        return redirect('/master/usuarios')
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

# Nuevas rutas para el panel maestro
@main.route('/master/condominios', methods=['GET', 'POST'])
@jwt_required()
def master_condominios():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)

    if request.method == 'GET':
        # Obtener todos los condominios existentes
        all_condominiums = Condominium.query.all()
        return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=all_condominiums)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_single':
            name = request.form.get('name', '').strip()
            address = request.form.get('address', '').strip()
            city = request.form.get('city', '').strip()
            country = request.form.get('country', 'Ecuador').strip()
            status = request.form.get('status', 'PENDIENTE_APROBACION').upper()

            if not name:
                flash("El nombre del condominio es obligatorio", "error")
                return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())
            if not address:
                flash("La dirección del condominio es obligatoria", "error")
                return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())
            if not city:
                flash("La ciudad del condominio es obligatoria", "error")
                return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())
            if not country:
                flash("El país del condominio es obligatorio", "error")
                return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())
            if not status:
                flash("El estado del condominio es obligatorio", "error")
                return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())

            try:
                new_condominium = Condominium(
                    name=name,
                    address=address,
                    city=city,
                    country=country,
                    status=status,
                    tenant=tenant
                )
                db.session.add(new_condominium)
                db.session.commit()
                flash(f"Condominio '{name}' creado exitosamente.", "success")
            except Exception as e:
                current_app.logger.error(f"Error al crear condominio '{name}': {e}")
                flash(f"Error al crear condominio '{name}': {e}", "error")
        elif action == 'import_csv':
            uploaded_file = request.files.get('csv_file')
            if not uploaded_file or uploaded_file.filename == '':
                flash("No se seleccionó ningún archivo CSV para importar.", "error")
                return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())

            if uploaded_file and uploaded_file.filename.endswith('.csv'):
                try:
                    content = uploaded_file.read().decode('utf-8')
                    csv_reader = csv.DictReader(io.StringIO(content))
                    
                    created_count = 0
                    failed_count = 0
                    for row in csv_reader:
                        name = row.get('name', '').strip()
                        address = row.get('address', '').strip()
                        city = row.get('city', '').strip()
                        country = row.get('country', 'Ecuador').strip()
                        status = row.get('status', 'PENDIENTE_APROBACION').upper()

                        if not name:
                            failed_count += 1
                            continue
                        if not address:
                            failed_count += 1
                            continue
                        if not city:
                            failed_count += 1
                            continue
                        if not country:
                            failed_count += 1
                            continue
                        if not status:
                            failed_count += 1
                            continue

                        try:
                            new_condominium = Condominium(
                                name=name,
                                address=address,
                                city=city,
                                country=country,
                                status=status,
                                tenant=tenant
                            )
                            db.session.add(new_condominium)
                            created_count += 1
                        except Exception as e:
                            current_app.logger.error(f"Error al importar condominio '{name}' (fila {csv_reader.line_num}): {e}")
                            failed_count += 1

                    db.session.commit()
                    flash(f"Archivo CSV importado con éxito. {created_count} condominios creados, {failed_count} fallidos.", "success")
                except Exception as e:
                    current_app.logger.error(f"Error al leer o procesar el archivo CSV: {e}")
                    flash(f"Error al leer o procesar el archivo CSV: {e}", "error")
            else:
                flash("El archivo seleccionado no es un archivo CSV válido.", "error")
                return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())

        return render_template('master/condominios.html', user=user, config=config, mensaje="Página de gestión de condominios (Maestro)", all_condominiums=Condominium.query.all())

@main.route('/master/usuarios', methods=['GET', 'POST']) # Para gestión global de usuarios, diferente a /admin
@jwt_required()
def master_usuarios():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)

    if request.method == 'GET':
        # Obtener todos los usuarios por status
        pending_users = User.query.filter_by(status='pending').all()
        active_users = User.query.filter_by(status='active').all()
        rejected_users = User.query.filter_by(status='rejected').all()

        # Obtener todos los condominios existentes
        all_condominiums = Condominium.query.all()

        return render_template('master/usuarios.html', user=user, config=config, all_users=all_users, pending_users=pending_users, active_users=active_users, rejected_users=rejected_users, mensaje="Página de gestión de usuarios (Maestro)", all_condominiums=all_condominiums)

    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'create_user':
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '').strip() # Password is optional for new users
            phone = request.form.get('phone', '').strip()
            city = request.form.get('city', '').strip()
            country = request.form.get('country', '').strip()
            role = request.form.get('role', 'USER').upper()
            condominium_id = request.form.get('condominium_id') # For ADMINs

            # Validaciones
            if not name:
                flash("El nombre es obligatorio", "error")
                return render_template('master/usuarios.html', user=user, config=config, all_users=all_users, pending_users=pending_users, active_users=active_users, rejected_users=rejected_users, mensaje="Página de gestión de usuarios (Maestro)", all_condominiums=all_condominiums)
            if not email:
                flash("El email es obligatorio", "error")
                return render_template('master/usuarios.html', user=user, config=config, all_users=all_users, pending_users=pending_users, active_users=active_users, rejected_users=rejected_users, mensaje="Página de gestión de usuarios (Maestro)", all_condominiums=all_condominiums)
            if User.query.filter_by(email=email).first():
                flash("Este email ya está en uso por otro usuario", "error")
                return render_template('master/usuarios.html', user=user, config=config, all_users=all_users, pending_users=pending_users, active_users=active_users, rejected_users=rejected_users, mensaje="Página de gestión de usuarios (Maestro)", all_condominiums=all_condominiums)
            
            # Password hashing
            pwd_hash = hashlib.sha256(password.encode()).hexdigest() if password else None

            try:
                new_user = User(
                    name=name,
                    email=email,
                    password_hash=pwd_hash,
                    phone=phone,
                    city=city,
                    country=country,
                    role=role,
                    status='pending', # New users are pending by default
                    tenant=tenant
                )
                db.session.add(new_user)

                if role == 'ADMIN' and condominium_id:
                    # Find the condominium by ID
                    condominium = Condominium.query.get(int(condominium_id))
                    if condominium:
                        new_user.condominium = condominium # Assign condominium to the user
                    else:
                        flash(f"Condominio con ID {condominium_id} no encontrado.", "error")
                        return render_template('master/usuarios.html', user=user, config=config, all_users=all_users, pending_users=pending_users, active_users=active_users, rejected_users=rejected_users, mensaje="Página de gestión de usuarios (Maestro)", all_condominiums=all_condominiums)

                db.session.commit()
                flash(f"Usuario {email} creado exitosamente.", "success")
            except Exception as e:
                current_app.logger.error(f"Error al crear usuario {email}: {e}")
                flash(f"Error al crear usuario {email}: {e}", "error")

        return render_template('master/usuarios.html', user=user, config=config, all_users=all_users, pending_users=pending_users, active_users=active_users, rejected_users=rejected_users, mensaje="Página de gestión de usuarios (Maestro)", all_condominiums=all_condominiums)

@main.route('/master/configuracion')
@jwt_required()
def master_configuracion():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('master/configuracion.html', user=user, config=config, mensaje="Página de configuración global (Maestro)")

# Rutas de acción para usuarios del Master Panel
@main.route('/master/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
@jwt_required()
def master_usuarios_editar(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    
    user_to_edit = User.query.get_or_404(user_id)
    
    if request.method == 'GET':
        return render_template('master/editar_usuario.html', user=user_to_edit, config=current_app.get_tenant_config(current_user.tenant))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', '').strip()
        country = request.form.get('country', '').strip()
        role = request.form.get('role', 'USER').upper()
        status = request.form.get('status', 'active').upper()

        # Validaciones
        if not name:
            flash("El nombre es obligatorio", "error")
            return render_template('master/editar_usuario.html', user=user_to_edit, config=current_app.get_tenant_config(current_user.tenant))
        if not email:
            flash("El email es obligatorio", "error")
            return render_template('master/editar_usuario.html', user=user_to_edit, config=current_app.get_tenant_config(current_user.tenant))
        if User.query.filter_by(email=email).first() and email != user_to_edit.email:
            flash("Este email ya está en uso por otro usuario", "error")
            return render_template('master/editar_usuario.html', user=user_to_edit, config=current_app.get_tenant_config(current_user.tenant))
        
        # No permitir que un MASTER cambie su propio rol o el rol de otro MASTER
        if current_user.role == 'MASTER' and user_to_edit.role == 'MASTER':
            if role != 'MASTER':
                flash("No puedes cambiar el rol de un usuario MASTER a otro rol.", "error")
                return render_template('master/editar_usuario.html', user=user_to_edit, config=current_app.get_tenant_config(current_user.tenant))

        user_to_edit.name = name
        user_to_edit.email = email
        user_to_edit.phone = phone
        user_to_edit.city = city
        user_to_edit.country = country
        user_to_edit.role = role
        user_to_edit.status = status

        db.session.commit()
        flash(f"Usuario {user_to_edit.email} actualizado exitosamente.", "success")
        return redirect(url_for('main.master_usuarios'))

@main.route('/master/usuarios/eliminar/<int:user_id>')
@jwt_required()
def master_usuarios_eliminar(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    
    user_to_delete = User.query.get_or_404(user_id)
    if user_to_delete.role == 'MASTER': # No permitir eliminar al propio MASTER o a otros MASTERs
        flash("No puedes eliminar a un usuario MASTER.", "error")
        return redirect(url_for('main.master_usuarios'))

    db.session.delete(user_to_delete)
    db.session.commit()
    flash(f"Usuario {user_to_delete.email} eliminado exitosamente.", "success")
    return redirect(url_for('main.master_usuarios'))

@main.route('/master/usuarios/reaprobar/<int:user_id>')
@jwt_required()
def master_usuarios_reaprobar(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    
    user_to_reapprove = User.query.get_or_404(user_id)
    user_to_reapprove.status = 'active'
    db.session.commit()
    flash(f"Usuario {user_to_reapprove.email} reaprobado y activo.", "success")
    return redirect(url_for('main.master_usuarios'))

@main.route('/condominiums', methods=['GET'])
def get_condominiums():
    try:
        condominiums = Condominium.query.all()
        return jsonify([condo.to_dict() for condo in condominiums])
    except Exception as e:
        return jsonify({'error': 'Error al obtener condominios'}), 500