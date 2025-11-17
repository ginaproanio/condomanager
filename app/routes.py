from flask import Blueprint, request, render_template, redirect, url_for, current_app, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User
import hashlib
import traceback
from datetime import datetime, timedelta

main = Blueprint('main', __name__)

@main.route('/api/test')
def test_api():
    return jsonify({
        "status": "✅ API funcionando correctamente", 
        "timestamp": datetime.utcnow().isoformat(),
        "message": "Backend Flask activo en Railway"
    })

# =============================================================================
# AUTENTICACIÓN JWT - NUEVOS ENDPOINTS
# =============================================================================

@main.route('/api/auth/register', methods=['POST'])
def api_register():
    """Registro de usuario con JWT"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email y contraseña requeridos"}), 400
        
        email = data['email']
        name = data.get('name', '')
        password = data['password']
        
        # Verificar si el usuario ya existe
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "Este email ya está registrado"}), 400
        
        # Hash de contraseña
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Obtener tenant
        from app.tenant import get_tenant
        tenant = get_tenant()
        
        # Crear usuario
        user = User(
            email=email,
            name=name,
            phone=data.get('phone', ''),      # ✅ NUEVO
            city=data.get('city', ''),        # ✅ NUEVO
            country=data.get('country', ''),  # ✅ NUEVO
            password_hash=pwd_hash,
            tenant=tenant,
            role='USER',
            status='active'
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Crear token JWT
        access_token = create_access_token(
            identity=user,
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,    # ✅ NUEVO
                "city": user.city,      # ✅ NUEVO
                "country": user.country, # ✅ NUEVO
                "role": user.role
            },
            "access_token": access_token
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error en registro: {str(e)}"}), 500

@main.route('/api/auth/login', methods=['POST'])
def api_login():
    """Login de usuario con JWT"""
    try:
        data = request.get_json()
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email y contraseña requeridos"}), 400
        
        email = data['email']
        password = data['password']
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Buscar usuario
        user = User.query.filter_by(email=email, password_hash=pwd_hash).first()
        
        if not user:
            return jsonify({"error": "Credenciales incorrectas"}), 401
        
        if user.status != 'active':
            return jsonify({"error": "Cuenta pendiente de aprobación"}), 403
        
        # Crear token JWT
        access_token = create_access_token(
            identity=user,
            expires_delta=timedelta(days=30)
        )
        
        return jsonify({
            "message": "Login exitoso",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            },
            "access_token": access_token
        })
        
    except Exception as e:
        return jsonify({"error": f"Error en login: {str(e)}"}), 500

@main.route('/api/auth/me', methods=['GET'])
@jwt_required()
def api_get_me():
    """Obtener información del usuario actual"""
    try:
        current_user = get_jwt_identity()
        
        return jsonify({
            "user": {
                "id": current_user.id,
                "name": current_user.name,
                "email": current_user.email,
                "role": current_user.role,
                "status": current_user.status
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"Error obteniendo usuario: {str(e)}"}), 500

@main.route('/api/auth/protected', methods=['GET'])
@jwt_required()
def api_protected():
    """Ruta protegida de ejemplo"""
    current_user = get_jwt_identity()
    return jsonify({
        "message": f"Acceso concedido para {current_user.email}",
        "user_role": current_user.role
    })

@main.route('/api/auth/admin-only', methods=['GET'])
@jwt_required()
def api_admin_only():
    """Ruta solo para administradores"""
    current_user = get_jwt_identity()
    
    if current_user.role not in ['ADMIN', 'MASTER']:
        return jsonify({"error": "Acceso denegado. Se requiere rol de administrador"}), 403
    
    return jsonify({
        "message": "Bienvenido administrador",
        "user": current_user.email
    })

# =============================================================================
# RUTAS EXISTENTES (TUS RUTAS ORIGINALES)
# =============================================================================

@main.route('/')
def home():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('home.html', config=config)

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    try:
        if request.method == 'POST':
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # USAR TENANT DINÁMICO
            from app.tenant import get_tenant
            tenant = get_tenant()
            
            # Obtener configuración para el template
            config = current_app.get_tenant_config(tenant)
            
            # Verificar si el usuario ya existe
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('auth/registro.html', 
                                    error="❌ Este email ya está registrado",
                                    config=config)
            
            user = User(
                email=email, 
                name=name, 
                phone=request.form['phone'],      # ✅ NUEVO
                city=request.form['city'],        # ✅ NUEVO
                country=request.form['country'],  # ✅ NUEVO
                password_hash=pwd_hash, 
                tenant=tenant,
                status='pending'
            )
            
            db.session.add(user)
            db.session.commit()
            
            return render_template('auth/registro.html', 
                                mensaje=f"✅ Registrado exitosamente. Tu email {email} está pendiente de aprobación en {tenant}.",
                                config=config)
        
        # GET request - obtener configuración
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        return render_template('auth/registro.html', config=config)
    
    except Exception as e:
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        return render_template('auth/registro.html', 
                             error=f"❌ Error en registro: {str(e)}",
                             config=config)

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios"""
    try:
        # Obtener configuración
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user = User.query.filter_by(email=email, password_hash=pwd_hash).first()
            
            if user:
                if user.status == 'pending':
                    return render_template('auth/login.html',
                                        error="⏳ Tu cuenta está pendiente de aprobación",
                                        config=config)
                elif user.status == 'rejected':
                    return render_template('auth/login.html',
                                        error="❌ Tu cuenta fue rechazada. Contacta al administrador",
                                        config=config)
                
                return render_template('auth/login.html', 
                                    mensaje=f"🎉 Bienvenido {user.name}!",
                                    config=config)
            else:
                return render_template('auth/login.html',
                                    error="❌ Credenciales incorrectas",
                                    config=config)
        
        return render_template('auth/login.html', config=config)
    
    except Exception as e:
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        return render_template('auth/login.html', 
                             error=f"❌ Error en login: {str(e)}",
                             config=config)

@main.route('/admin')
def admin_panel():
    """Panel de administración para aprobar usuarios"""
    try:
        # Obtener configuración
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        
        # Listar usuarios pendientes de aprobación
        pending_users = User.query.filter_by(status='pending').all()
        active_users = User.query.filter_by(status='active').all()
        rejected_users = User.query.filter_by(status='rejected').all()
        
        return render_template('admin/panel.html', 
                             pending_users=pending_users,
                             active_count=len(active_users),
                             rejected_count=len(rejected_users),
                             config=config)
    
    except Exception as e:
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        return render_template('admin/panel.html',
                             error=f"Error cargando panel: {str(e)}",
                             config=config)

@main.route('/aprobar/<int:user_id>')
def aprobar_usuario(user_id):
    """Aprobar usuario pendiente"""
    try:
        user = User.query.get(user_id)
        if user:
            user.status = 'active'
            db.session.commit()
        return redirect('/admin')
    except Exception as e:
        return redirect('/admin')

@main.route('/rechazar/<int:user_id>')
def rechazar_usuario(user_id):
    """Rechazar usuario pendiente"""
    try:
        user = User.query.get(user_id)
        if user:
            user.status = 'rejected' 
            db.session.commit()
        return redirect('/admin')
    except Exception as e:
        return redirect('/admin')

@main.route('/dashboard')
def dashboard():
    """Dashboard para usuarios aprobados"""
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('user/dashboard.html', 
                         mensaje="🏠 Panel de usuario - Próximamente",
                         config=config)

@main.route('/usuarios')
def listar_usuarios():
    """Listar todos los usuarios (solo admin)"""
    try:
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        
        users = User.query.all()
        return render_template('admin/usuarios.html',
                             users=users,
                             config=config)
    except Exception as e:
        return f"Error listando usuarios: {str(e)}"

@main.route('/health')
def health():
    """Health check para monitoreo"""
    return "OK", 200

# ✅ RUTAS DE SERVICIOS FUTUROS
@main.route('/unidades')
def unidades():
    """Gestión de unidades (próximamente)"""
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/unidades.html',
                         mensaje="🏢 Gestión de Unidades - Próximamente",
                         config=config)

@main.route('/pagos')
def pagos():
    """Sistema de pagos (próximamente)"""
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/pagos.html',
                         mensaje="💳 Sistema de Pagos - Próximamente",
                         config=config)

@main.route('/reportes')
def reportes():
    """Reportes del sistema (próximamente)"""
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/reportes.html',
                         mensaje="📊 Reportes - Próximamente",
                         config=config)
    
    # =============================================================================
# RUTAS MAESTRO
# =============================================================================

@main.route('/master')
@jwt_required()
def master_panel():
    """Panel exclusivo para usuarios MASTER"""
    try:
        current_user = get_jwt_identity()
        
        if current_user.role != 'MASTER':
            return jsonify({"error": "Acceso denegado. Se requiere rol MASTER"}), 403
        
        from app.tenant import get_tenant
        tenant = get_tenant()
        config = current_app.get_tenant_config(tenant)
        
        return render_template('master/panel.html', config=config)
        
    except Exception as e:
        return jsonify({"error": f"Error accediendo al panel maestro: {str(e)}"}), 500

@main.route('/api/master/estadisticas')
@jwt_required()
def api_master_estadisticas():
    """Estadísticas globales del sistema para MASTER"""
    try:
        current_user = get_jwt_identity()
        
        if current_user.role != 'MASTER':
            return jsonify({"error": "Acceso denegado"}), 403
        
        # Aquí irá la lógica para obtener estadísticas
        # Por ahora devolvemos datos de ejemplo
        return jsonify({
            "total_condominios": 0,
            "total_usuarios": User.query.count(),
            "condominios_activos": 0,
            "condominios_pendientes": 0,
            "condominios_recientes": []
        })
        
    except Exception as e:
        return jsonify({"error": f"Error obteniendo estadísticas: {str(e)}"}), 500
    
    
@main.route('/master/descargar-plantilla-unidades')
@jwt_required()
def descargar_plantilla_unidades():
    """Descargar plantilla CSV para carga masiva de unidades"""
    try:
        current_user = get_jwt_identity()
        if current_user.role != 'MASTER':
            return jsonify({"error": "Acceso denegado"}), 403
        
        # Crear CSV en memoria
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Encabezados según el modelo
        headers = [
            'property_number',    # Ej: "A-101", "C-25", "BOD-12" (OBLIGATORIO)
            'name',              # "Apartamento 101", "Casa 25" (OBLIGATORIO)
            'property_type',     # "apartamento", "casa", "local_comercial", "parqueadero", "bodega", "galpon", "terreno" (OBLIGATORIO)
            'main_street',       # "Av. Principal" (OBLIGATORIO)
            'cross_street',      # "Calle Segunda" (OBLIGATORIO)
            'house_number',      # "S/N", "25-A", "102"
            'address_reference', # "Frente al parque", "Entre calles"
            'latitude',          # "-0.180653" (OBLIGATORIO)
            'longitude',         # "-78.467834" (OBLIGATORIO)
            'building',          # "Torre A", "Edificio Principal"
            'floor',             # "1", "PB", "Sótano 2" 
            'sector',            # "Zona Residencial", "Área Comercial"
            'area_m2',           # "85.5", "350.0" (OBLIGATORIO)
            'area_construction_m2', # "75.0", "180.0" (para construcciones)
            'bedrooms',          # "2", "3" (para apartamentos/casas)
            'bathrooms',         # "2", "1" (para apartamentos/casas)
            'parking_spaces',    # "1", "2" (para apartamentos/casas)
            'front_meters',      # "15.0" (solo terrenos)
            'depth_meters',      # "23.3" (solo terrenos)
            'topography',        # "plano", "inclinado" (solo terrenos)
            'land_use',          # "residencial", "comercial" (solo terrenos)
            'notes'              # Observaciones adicionales
        ]
        
        writer.writerow(headers)
        
        # Ejemplos de datos
        examples = [
            ['A-101', 'Apartamento 101', 'apartamento', 'Av. Principal', 'Calle Segunda', '101', 'Frente al ascensor', 
             '-0.180653', '-78.467834', 'Torre A', '1', 'Zona Residencial', '85.5', '75.0', '2', '2', '1', '', '', '', '', ''],
            ['C-25', 'Casa 25', 'casa', 'Av. Las Palmeras', 'Calle Los Pinos', '25-A', 'Frente al parque',
             '-0.180700', '-78.467900', '', '', 'Manzana B', '120.0', '95.0', '3', '2', '2', '', '', '', '', ''],
            ['T-A5', 'Terreno A5', 'terreno', 'Av. Principal', 'Calle Segunda', 'S/N', 'Esquina noroeste',
             '-0.180750', '-78.467950', '', '', 'Loteamiento Norte', '350.0', '', '', '', '', '15.0', '23.3', 'plano', 'residencial', '']
        ]
        
        for example in examples:
            writer.writerow(example)
        
        # Devolver archivo
        from flask import Response
        output.seek(0)
        
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=plantilla_unidades.csv"}
        )
        
    except Exception as e:
        return jsonify({"error": f"Error generando plantilla: {str(e)}"}), 500
    
@main.route('/api/master/cargar-unidades-csv', methods=['POST'])
@jwt_required()
def cargar_unidades_csv():
    """Cargar unidades masivamente desde CSV"""
    try:
        current_user = get_jwt_identity()
        if current_user.role != 'MASTER':
            return jsonify({"error": "Acceso denegado"}), 403
        
        if 'csv_file' not in request.files:
            return jsonify({"error": "No se envió archivo CSV"}), 400
        
        csv_file = request.files['csv_file']
        if csv_file.filename == '':
            return jsonify({"error": "Nombre de archivo vacío"}), 400
        
        if not csv_file.filename.endswith('.csv'):
            return jsonify({"error": "El archivo debe ser CSV"}), 400
        
        # Leer y procesar CSV
        import csv
        import io
        
        stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
        csv_reader = csv.DictReader(stream)
        
        unidades_procesadas = []
        errores = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # row_num incluye encabezado
            try:
                # Validar campos obligatorios
                campos_obligatorios = ['property_number', 'name', 'property_type', 'main_street', 'cross_street', 'latitude', 'longitude', 'area_m2']
                for campo in campos_obligatorios:
                    if not row.get(campo):
                        errores.append(f"Fila {row_num}: Campo '{campo}' es obligatorio")
                        continue
                
                # Verificar si ya existe
                if Unit.query.filter_by(property_number=row['property_number']).first():
                    errores.append(f"Fila {row_num}: Número de propiedad '{row['property_number']}' ya existe")
                    continue
                
                # Crear unidad
                unidad = Unit(
                    property_number=row['property_number'],
                    name=row['name'],
                    property_type=row['property_type'],
                    main_street=row['main_street'],
                    cross_street=row['cross_street'],
                    house_number=row.get('house_number', ''),
                    address_reference=row.get('address_reference', ''),
                    latitude=float(row['latitude']),
                    longitude=float(row['longitude']),
                    building=row.get('building'),
                    floor=row.get('floor'),
                    sector=row.get('sector'),
                    area_m2=float(row['area_m2']),
                    area_construction_m2=float(row['area_construction_m2']) if row.get('area_construction_m2') else None,
                    bedrooms=int(row['bedrooms']) if row.get('bedrooms') else None,
                    bathrooms=int(row['bathrooms']) if row.get('bathrooms') else None,
                    parking_spaces=int(row['parking_spaces']) if row.get('parking_spaces') else None,
                    front_meters=float(row['front_meters']) if row.get('front_meters') else None,
                    depth_meters=float(row['depth_meters']) if row.get('depth_meters') else None,
                    topography=row.get('topography'),
                    land_use=row.get('land_use'),
                    notes=row.get('notes', ''),
                    condominium_id=1,  # Por defecto, luego se puede configurar
                    created_by=current_user.id,
                    status='disponible'
                )
                
                db.session.add(unidad)
                unidades_procesadas.append(row['property_number'])
                
            except ValueError as e:
                errores.append(f"Fila {row_num}: Error en formato de número - {str(e)}")
            except Exception as e:
                errores.append(f"Fila {row_num}: Error procesando - {str(e)}")
        
        if errores:
            db.session.rollback()
            return jsonify({
                "error": "Errores en el archivo CSV",
                "detalles": errores,
                "unidades_procesadas": 0
            }), 400
        
        # Si no hay errores, guardar todo
        db.session.commit()
        
        return jsonify({
            "message": f"✅ {len(unidades_procesadas)} unidades cargadas exitosamente",
            "unidades_procesadas": unidades_procesadas
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error procesando archivo: {str(e)}"}), 500
    
@main.route('/api/master/crear-unidad', methods=['POST'])
@jwt_required()
def crear_unidad_individual():
    """Crear unidad individualmente"""
    try:
        current_user = get_jwt_identity()
        if current_user.role != 'MASTER':
            return jsonify({"error": "Acceso denegado"}), 403
        
        data = request.get_json()
        
        # Validar campos obligatorios
        campos_obligatorios = ['property_number', 'name', 'property_type', 'main_street', 'cross_street', 'latitude', 'longitude', 'area_m2']
        for campo in campos_obligatorios:
            if not data.get(campo):
                return jsonify({"error": f"Campo '{campo}' es obligatorio"}), 400
        
        # Verificar si ya existe
        if Unit.query.filter_by(property_number=data['property_number']).first():
            return jsonify({"error": f"El número de propiedad '{data['property_number']}' ya existe"}), 400
        
        # Crear unidad
        unidad = Unit(
            property_number=data['property_number'],
            name=data['name'],
            property_type=data['property_type'],
            main_street=data['main_street'],
            cross_street=data['cross_street'],
            house_number=data.get('house_number', ''),
            address_reference=data.get('address_reference', ''),
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            building=data.get('building'),
            floor=data.get('floor'),
            sector=data.get('sector'),
            area_m2=float(data['area_m2']),
            area_construction_m2=float(data['area_construction_m2']) if data.get('area_construction_m2') else None,
            bedrooms=int(data['bedrooms']) if data.get('bedrooms') else None,
            bathrooms=int(data['bathrooms']) if data.get('bathrooms') else None,
            parking_spaces=int(data['parking_spaces']) if data.get('parking_spaces') else None,
            front_meters=float(data['front_meters']) if data.get('front_meters') else None,
            depth_meters=float(data['depth_meters']) if data.get('depth_meters') else None,
            topography=data.get('topography'),
            land_use=data.get('land_use'),
            notes=data.get('notes', ''),
            condominium_id=1,  # Por defecto
            created_by=current_user.id,
            status='disponible'
        )
        
        db.session.add(unidad)
        db.session.commit()
        
        return jsonify({
            "message": "✅ Unidad creada exitosamente",
            "unidad": {
                "id": unidad.id,
                "property_number": unidad.property_number,
                "name": unidad.name,
                "full_address": unidad.get_full_address()
            }
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Error creando unidad: {str(e)}"}), 500