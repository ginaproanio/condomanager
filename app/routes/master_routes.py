from flask import (
    Blueprint, render_template, redirect,
    current_app, flash, Response, jsonify, request, url_for, session
)
from flask_jwt_extended import jwt_required
from sqlalchemy import or_
from sqlalchemy.orm.attributes import flag_modified
from app.auth import get_current_user
from app.models import Condominium, User, CondominiumConfig, Unit
from app import db, models
from datetime import datetime, timedelta
import io
import csv

master_bp = Blueprint('master', __name__)

@master_bp.route('/master')
@jwt_required()
def master_panel():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    all_users = User.query.all()
    return render_template('master/panel.html', user=user, config=config, all_users=all_users)

@master_bp.route('/master/reports', methods=['GET', 'POST'])
@jwt_required()
def reports():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect('/dashboard')

    # Generación de estadísticas en tiempo real
    total_condos = Condominium.query.count()
    active_condos = Condominium.query.filter_by(status='ACTIVO').count()
    inactive_condos = total_condos - active_condos
    
    total_users = User.query.count()
    # Usuarios con roles de gestión (ADMIN o MASTER)
    management_users = User.query.filter(or_(User.role=='ADMIN', User.role=='MASTER')).count()
    
    # Módulos activos (conteo simple)
    docs_module_active = Condominium.query.filter_by(has_documents_module=True).count()
    
    # Lógica de exportación (POST)
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'export_condos':
            output = io.StringIO()
            writer = csv.writer(output)
            # Cabeceras
            writer.writerow(['ID', 'Nombre Legal', 'Nombre Comercial', 'RUC', 'Estado', 'Subdominio', 'Admin Email', 'Mód. Documentos', 'Fecha Creación'])
            
            condos = Condominium.query.order_by(Condominium.created_at.desc()).all()
            for c in condos:
                admin_email = c.admin_user.email if c.admin_user else 'Sin Asignar'
                writer.writerow([
                    c.id, 
                    c.legal_name or c.name, 
                    c.name, 
                    c.ruc, 
                    c.status, 
                    c.subdomain, 
                    admin_email, 
                    'ACTIVO' if c.has_documents_module else 'NO',
                    c.created_at.strftime('%Y-%m-%d') if c.created_at else ''
                ])
                
            output.seek(0)
            return Response(
                output.getvalue().encode('utf-8-sig'), # UTF-8 BOM para Excel en español
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename=reporte_condominios_{datetime.now().strftime('%Y%m%d')}.csv"}
            )
            
        elif action == 'export_users':
            output = io.StringIO()
            writer = csv.writer(output)
            # Cabeceras
            writer.writerow(['ID', 'Nombre', 'Email', 'Rol', 'Estado', 'Tenant/Condominio', 'Fecha Registro'])
            
            users = User.query.order_by(User.created_at.desc()).all()
            for u in users:
                writer.writerow([
                    u.id,
                    u.name,
                    u.email,
                    u.role,
                    u.status,
                    u.tenant or 'N/A',
                    u.created_at.strftime('%Y-%m-%d') if u.created_at else ''
                ])
                
            output.seek(0)
            return Response(
                output.getvalue().encode('utf-8-sig'),
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename=reporte_usuarios_global_{datetime.now().strftime('%Y%m%d')}.csv"}
            )

    return render_template('master/reports.html', 
                           user=user,
                           stats={
                               'total_condos': total_condos,
                               'active_condos': active_condos,
                               'inactive_condos': inactive_condos,
                               'total_users': total_users,
                               'management_users': management_users,
                               'docs_module_active': docs_module_active
                           })

@master_bp.route('/master/condominios', methods=['GET'])
@jwt_required()
def master_condominios():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    search_query = request.args.get('q', '')
    query = Condominium.query

    if search_query:
        search_term = f"%{search_query}%"
        query = query.filter(or_(
            Condominium.name.ilike(search_term),
            Condominium.ruc.ilike(search_term),
            Condominium.subdomain.ilike(search_term),
            Condominium.email.ilike(search_term),
            Condominium.status.ilike(search_term)
        ))

    all_condominiums = query.order_by(Condominium.created_at.desc()).all()
    return render_template('master/condominios.html', user=user, all_condominiums=all_condominiums, search_query=search_query)

@master_bp.route('/supervise/<int:condominium_id>', methods=['GET'])
@jwt_required()
def supervise_condominium(condominium_id):
    """
    Muestra un panel de supervisión de solo lectura para un condominio específico.
    Accesible solo para el rol MASTER.
    """
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('public.login'))

    condominium = db.session.get(Condominium, condominium_id)
    if not condominium:
        flash('Condominio no encontrado.', 'danger')
        return redirect(url_for('master.master_condominios'))

    # Calcular estadísticas
    stats = {
        'total_units': Unit.query.filter_by(condominium_id=condominium.id).count(),
        'active_users': User.query.filter_by(tenant=condominium.subdomain, status='active').count(),
        'pending_users': User.query.filter_by(tenant=condominium.subdomain, status='pending').count()
    }

    return render_template('master/supervise_condominium.html', 
                           user=user, 
                           condominium=condominium, 
                           stats=stats)

@master_bp.route('/master/usuarios', methods=['GET'])
@jwt_required()
def master_usuarios():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    search_query = request.args.get('q', '')
    base_query = User.query

    if search_query:
        search_term = f"%{search_query}%"
        base_query = base_query.filter(or_(
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term),
            User.email.ilike(search_term),
            User.cedula.ilike(search_term)
        ))

    # FILTRO DE SEGURIDAD: MASTER solo ve ADMIN y MASTER
    # Esto asegura que los usuarios 'USER' (residentes) NUNCA sean accesibles por el Master
    base_query = base_query.filter(User.role.in_(['ADMIN', 'MASTER']))

    # FILTRO DE SEGURIDAD: MASTER solo ve ADMIN y MASTER
    # Esto asegura que los usuarios 'USER' (residentes) NUNCA sean accesibles por el Master
    base_query = base_query.filter(User.role.in_(['ADMIN', 'MASTER']))

    # Lógica para GET (mostrar las listas de usuarios)
    pending_users = base_query.filter_by(status='pending').order_by(User.created_at.desc()).all()
    active_users = base_query.filter_by(status='active').order_by(User.created_at.desc()).all()
    rejected_users = base_query.filter_by(status='rejected').order_by(User.created_at.desc()).all()
    all_users = base_query.order_by(User.created_at.desc()).all()
    all_condominiums = Condominium.query.order_by(Condominium.name).all() # Necesario para el modal de gestión

    return render_template(
        'master/usuarios.html',
        user=user,
        pending_users=pending_users,
        active_users=active_users,
        rejected_users=rejected_users,
        all_users=all_users,
        all_condominiums=all_condominiums, # Se pasa para el modal de gestión de usuarios
        search_query=search_query
    )

@master_bp.route('/master/usuarios/manage', methods=['POST'])
@jwt_required()
def master_manage_user():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))

    action = request.form.get('action')
    user_id = request.form.get('user_id')
    user_to_manage = User.query.get_or_404(user_id)

    if action == 'assign_and_approve':
        condominium_id = request.form.get('condominium_id')
        if not condominium_id:
            flash('Debe seleccionar un condominio para asignar y aprobar.', 'error')
            return redirect(url_for('master.master_usuarios'))
        
        condo = Condominium.query.get(condominium_id)
        user_to_manage.tenant = condo.subdomain
        # user_to_manage.condominium_id = condo.id # ELIMINADO: Este campo no existe en User
        user_to_manage.status = 'active'
        db.session.commit()
        flash(f'Usuario {user_to_manage.email} asignado a {condo.name} y aprobado.', 'success')

    elif action == 'simple_approve':
        user_to_manage.status = 'active'
        db.session.commit()
        flash(f'Usuario {user_to_manage.email} aprobado exitosamente.', 'success')

    elif action == 'activate_demo':
        # Crear un condominio de demostración para el usuario
        demo_subdomain = f"demo-{user_to_manage.id}-{datetime.utcnow().strftime('%Y%m%d')}"
        demo_condo = Condominium(
            name=f"Demo para {user_to_manage.name}",
            subdomain=demo_subdomain,
            status='DEMO',
            admin_user_id=user_to_manage.id,
            created_by=user.id,
            # Podríamos añadir una fecha de expiración
            # expiration_date=datetime.utcnow() + timedelta(days=15) 
        )
        db.session.add(demo_condo)
        db.session.flush() # Para obtener el ID del nuevo condo

        user_to_manage.tenant = demo_subdomain
        # user_to_manage.condominium_id = demo_condo.id # ELIMINADO: Este campo no existe en User
        user_to_manage.status = 'active'
        user_to_manage.role = 'ADMIN' # Un usuario de demo debe ser admin de su demo
        
        db.session.commit()
        flash(f'Demo de 15 días activada para {user_to_manage.email}. Condominio de demo: {demo_condo.name}', 'success')

    elif action == 'reject':
        user_to_manage.status = 'rejected'
        db.session.commit()
        flash(f'Usuario {user_to_manage.email} ha sido rechazado.', 'info')

    return redirect(url_for('master.master_usuarios'))

@master_bp.route('/master/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
@jwt_required()
def master_usuarios_editar(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))

    user_to_edit = User.query.get_or_404(user_id)
    all_condominiums = Condominium.query.order_by(Condominium.name).all()

    if request.method == 'POST':
        # --- Lógica actualizada para guardar todos los campos ---
        user_to_edit.first_name = request.form.get('first_name')
        user_to_edit.last_name = request.form.get('last_name')
        user_to_edit.cedula = request.form.get('cedula')
        user_to_edit.email = request.form.get('email').lower()
        user_to_edit.cellphone = request.form.get('cellphone')
        
        birth_date_str = request.form.get('birth_date')
        if birth_date_str:
            user_to_edit.birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date()
        else:
            user_to_edit.birth_date = None

        user_to_edit.role = request.form.get('role')
        user_to_edit.status = request.form.get('status')
        condominium_id = request.form.get('condominium_id')
        # --- Fin de la lógica actualizada ---
        
        # user_to_edit.condominium_id = int(condominium_id) if condominium_id else None # ELIMINADO: Este campo no existe en User
        user_to_edit.tenant = Condominium.query.get(condominium_id).subdomain if condominium_id else None

        db.session.commit()
        flash(f'Usuario {user_to_edit.name} actualizado correctamente.', 'success')
        return redirect(url_for('master.master_usuarios'))

    return render_template('master/editar_usuario.html', user=current_user, user_to_edit=user_to_edit, all_condominiums=all_condominiums)

@master_bp.route('/master/usuarios/eliminar/<int:user_id>', methods=['POST'])
@jwt_required()
def master_usuarios_eliminar(user_id):
    # Placeholder para la lógica de eliminación
    flash(f"Funcionalidad para eliminar usuario {user_id} no implementada.", "info")
    return redirect(url_for('master.master_usuarios'))

@master_bp.route('/master/configuracion', methods=['GET', 'POST'])
@jwt_required()
def master_configuracion():
    """
    Panel de configuración global de la plataforma (Banco, APIs, etc.)
    Usa el condominio 'sandbox' como almacén de esta configuración global.
    """
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    # Usamos el condominio 'sandbox' o el tenant del master para guardar esta config
    # En un sistema más grande, esto iría en una tabla 'PlatformConfig'
    target_condo = None
    if user.tenant:
        target_condo = Condominium.query.filter_by(subdomain=user.tenant).first()
    if not target_condo:
        target_condo = Condominium.query.filter_by(subdomain='sandbox').first()
    
    if not target_condo:
        flash("No se encontró un entorno (Sandbox) para guardar la configuración.", "error")
        return redirect(url_for('master.master_panel'))

    # Cargar configuración existente
    # Usamos el campo 'notes' como un JSON improvisado o 'whatsapp_config' si queremos reutilizar
    # Pero lo ideal es usar payment_config para el banco y whatsapp_config para meta.
    
    current_payment_config = target_condo.payment_config or {}
    current_whatsapp_config = target_condo.whatsapp_config or {}
    
    # Unificar para la vista
    config_data = {
        # Banco (guardado en payment_config bajo la clave 'saas_bank_account')
        'bank_name': current_payment_config.get('saas_bank_account', {}).get('bank_name', ''),
        'account_type': current_payment_config.get('saas_bank_account', {}).get('account_type', ''),
        'account_number': current_payment_config.get('saas_bank_account', {}).get('account_number', ''),
        'account_holder': current_payment_config.get('saas_bank_account', {}).get('account_holder', ''),
        'account_id': current_payment_config.get('saas_bank_account', {}).get('account_id', ''),
        'account_email': current_payment_config.get('saas_bank_account', {}).get('account_email', ''),
        
        # Meta (guardado en whatsapp_config)
        'meta_phone_id': current_whatsapp_config.get('phone_id', ''),
        'meta_business_id': current_whatsapp_config.get('business_id', ''),
        'meta_access_token': current_whatsapp_config.get('access_token', '')
    }

    if request.method == 'POST':
        config_type = request.form.get('config_type')
        
        if config_type == 'bank_account':
            # Actualizar datos bancarios en payment_config
            new_bank_data = {
                'bank_name': request.form.get('bank_name'),
                'account_type': request.form.get('account_type'),
                'account_number': request.form.get('account_number'),
                'account_holder': request.form.get('account_holder'),
                'account_id': request.form.get('account_id'),
                'account_email': request.form.get('account_email')
            }
            # Preservar otros datos de payment_config si existen
            updated_payment_config = dict(current_payment_config)
            updated_payment_config['saas_bank_account'] = new_bank_data
            
            target_condo.payment_config = updated_payment_config
            flag_modified(target_condo, "payment_config")
            flash("Datos bancarios de la plataforma actualizados.", "success")

        elif config_type == 'meta_api':
            # Actualizar datos de Meta en whatsapp_config
            updated_whatsapp_config = dict(current_whatsapp_config)
            updated_whatsapp_config['phone_id'] = request.form.get('meta_phone_id')
            updated_whatsapp_config['business_id'] = request.form.get('meta_business_id')
            updated_whatsapp_config['access_token'] = request.form.get('meta_access_token')
            
            target_condo.whatsapp_config = updated_whatsapp_config
            flag_modified(target_condo, "whatsapp_config")
            flash("Credenciales de Meta actualizadas.", "success")
            
        try:
            db.session.commit()
            return redirect(url_for('master.master_configuracion'))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar: {e}", "error")

    return render_template('master/configuracion.html', user=user, config=config_data)

@master_bp.route('/master/usuarios/reaprobar/<int:user_id>', methods=['POST'])
@jwt_required()
def master_usuarios_reaprobar(user_id):
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))

    user_to_reapprove = User.query.get_or_404(user_id)
    if user_to_reapprove:
        user_to_reapprove.status = 'pending' # Lo devolvemos a pendiente para que el MASTER decida qué hacer
        db.session.commit()
        flash(f"El usuario {user_to_reapprove.email} ha sido movido a 'Pendientes' para su reevaluación.", "success")
    else:
        flash("Usuario no encontrado.", "error")

    return redirect(url_for('master.master_usuarios'))

@master_bp.route('/master/usuarios/importar_admins', methods=['POST'])
@jwt_required()
def master_importar_admins_csv():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('master.master_usuarios'))

    if 'csv_file' not in request.files:
        flash('No se encontró el archivo en la solicitud.', 'error')
        return redirect(url_for('master.master_usuarios'))

    file = request.files['csv_file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('master.master_usuarios'))

    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            created_count = 0
            errors = []
            import hashlib

            for row in csv_reader:
                if User.query.filter_by(email=row['email']).first() or User.query.filter_by(cedula=row['cedula']).first():
                    errors.append(f"Usuario con email {row['email']} o cédula {row['cedula']} ya existe.")
                    continue

                password = row.get('password')
                pwd_hash = hashlib.sha256(password.encode()).hexdigest() if password else None

                new_admin = User(
                    first_name=row['first_name'],
                    last_name=row['last_name'],
                    cedula=row['cedula'],
                    email=row['email'],
                    cellphone=row.get('cellphone'),
                    city=row.get('city'),
                    country=row.get('country', 'Ecuador'),
                    password_hash=pwd_hash,
                    role='ADMIN',
                    status='active'
                )
                db.session.add(new_admin)
                created_count += 1
            db.session.commit()
            flash(f'{created_count} administradores creados exitosamente. Errores: {len(errors)}', 'success')
            if errors:
                flash(f"Detalles de errores: {'; '.join(errors)}", 'warning')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar el archivo CSV: {e}', 'error')
        return redirect(url_for('master.master_usuarios'))

    flash('Formato de archivo inválido. Por favor, sube un archivo .csv', 'error')
    return redirect(url_for('master.master_usuarios'))

@master_bp.route('/master/usuarios/crear', methods=['GET', 'POST'])
@jwt_required()
def master_usuarios_crear():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    all_condominiums = Condominium.query.order_by(Condominium.name).all()

    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        cedula = request.form.get('cedula', '').strip()

        if User.query.filter_by(email=email).first():
            flash(f"El email '{email}' ya está registrado.", "error")
            return render_template('master/crear_usuario.html', user=user, all_condominiums=all_condominiums, request_form=request.form)
        if User.query.filter_by(cedula=cedula).first():
            flash(f"La cédula '{cedula}' ya está registrada.", "error")
            return render_template('master/crear_usuario.html', user=user, all_condominiums=all_condominiums, request_form=request.form)

        import hashlib
        password = request.form.get('password')
        pwd_hash = hashlib.sha256(password.encode()).hexdigest() if password else None

        birth_date_str = request.form.get('birth_date')
        birth_date = datetime.strptime(birth_date_str, '%Y-%m-%d').date() if birth_date_str else None

        new_user = User(
            first_name=request.form.get('first_name'),
            last_name=request.form.get('last_name'),
            cedula=cedula,
            email=email,
            password_hash=pwd_hash,
            cellphone=request.form.get('cellphone'),
            birth_date=birth_date,
            city=request.form.get('city'),
            country=request.form.get('country', 'Ecuador'),
            role=request.form.get('role'),
            status='active' # Creado por MASTER, se activa directamente
        )

        condominium_id = request.form.get('condominium_id')
        if condominium_id:
            condo = Condominium.query.get(condominium_id)
            # new_user.condominium_id = condo.id # ELIMINADO: Este campo no existe en User
            new_user.tenant = condo.subdomain

        db.session.add(new_user)
        db.session.commit()
        flash(f'Usuario {new_user.name} creado exitosamente.', 'success')
        return redirect(url_for('master.master_usuarios'))

    return render_template('master/crear_usuario.html', user=user, all_condominiums=all_condominiums, request_form={})

@master_bp.route('/master/crear_condominio', methods=['GET', 'POST'])
@jwt_required()
def crear_condominio():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    if request.method == 'POST':
        try:
            # Asegurarse de que el admin_user_id es un entero
            admin_id = request.form.get('admin_user_id')
            if not admin_id:
                # CORRECCIÓN: En lugar de redirigir, volvemos a renderizar la plantilla con un error.
                flash('Debe seleccionar un administrador.', 'error')
                administradores = User.query.filter(User.role.in_(['ADMIN', 'MASTER'])).all()
                return render_template('master/crear_condominio.html', user=user, administradores=administradores, legal_representatives=administradores, request_form=request.form)

            new_condo = Condominium(
                name=request.form.get('name'),
                legal_name=request.form.get('legal_name'),
                email=request.form.get('email'),
                ruc=request.form.get('ruc'),
                main_street=request.form.get('main_street'),
                cross_street=request.form.get('cross_street'),
                house_number=request.form.get('house_number'),
                city=request.form.get('city'),
                country=request.form.get('country'),
                latitude=float(request.form.get('latitude')) if request.form.get('latitude') else None,
                longitude=float(request.form.get('longitude')) if request.form.get('longitude') else None,
                subdomain=request.form.get('subdomain'),
                status='ACTIVO', # Corregido: El MASTER crea condominios activos directamente.
                admin_user_id=int(admin_id),
                created_by=user.id
            )
            db.session.add(new_condo)
            db.session.commit()
            # Si se asignó un representante legal, actualizarlo después de crear el condominio
            legal_representative_id = request.form.get('legal_representative_id')
            if legal_representative_id:
                new_condo.legal_representative_id = int(legal_representative_id)
                db.session.commit()

            flash('Condominio creado exitosamente.', 'success')
            return redirect('/master/condominios')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear el condominio: {e}")
            flash(f'Error al crear el condominio: {e}', 'error')
            administradores = User.query.filter(User.role.in_(['ADMIN', 'MASTER'])).order_by(User.first_name).all()
            return render_template('master/crear_condominio.html', user=user, administradores=administradores, legal_representatives=administradores, request_form=request.form)

    # GET request
    administradores = User.query.filter(User.role.in_(['ADMIN', 'MASTER'])).order_by(User.first_name).all()
    legal_representatives = User.query.order_by(User.first_name).all()
    return render_template('master/crear_condominio.html', user=user, administradores=administradores, legal_representatives=legal_representatives)

@master_bp.route('/master/modules', methods=['GET', 'POST'])
@jwt_required()
def manage_module_catalog():
    """
    Panel para que el MASTER gestione el catálogo global de módulos.
    Aquí se crean, editan y se pone en mantenimiento los módulos.
    """
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))

    if request.method == 'POST':
        # Lógica para crear o editar un módulo del catálogo
        module_id = request.form.get('module_id')
        
        try:
            if module_id: # Editar
                module = models.Module.query.get(module_id)
                flash('Módulo actualizado correctamente.', 'success')
            else: # Crear
                module = models.Module()
                db.session.add(module)
                flash('Módulo creado correctamente.', 'success')

            module.code = request.form.get('code')
            module.name = request.form.get('name')
            module.description = request.form.get('description')
            module.base_price = float(request.form.get('base_price', 0))
            module.billing_cycle = request.form.get('billing_cycle')
            
            new_status = request.form.get('status')
            module.status = new_status
            module.pricing_type = request.form.get('pricing_type')

            # Lógica de Mantenimiento
            if new_status == 'MAINTENANCE':
                module.maintenance_mode = True
                if not module.maintenance_start:
                    module.maintenance_start = datetime.utcnow()
                
                end_date_str = request.form.get('maintenance_end')
                if end_date_str:
                     # Convertir a datetime sin zona horaria (naive) pero consistente con la DB
                     try:
                         module.maintenance_end = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M')
                     except ValueError:
                         # Intento de fallback si el navegador envía segundos
                         try:
                             module.maintenance_end = datetime.strptime(end_date_str, '%Y-%m-%dT%H:%M:%S')
                         except:
                             flash('Formato de fecha de fin de mantenimiento inválido.', 'warning')
                             return redirect(url_for('master.manage_module_catalog'))
                
                module.maintenance_message = request.form.get('maintenance_message')
            else:
                module.maintenance_mode = False
                module.maintenance_start = None
                module.maintenance_end = None
                module.maintenance_message = None

            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el módulo: {e}', 'danger')
        
        return redirect(url_for('master.manage_module_catalog'))

    all_modules = db.session.query(models.Module).order_by(models.Module.name).all()
    return render_template('master/module_catalog.html', user=user, all_modules=all_modules)

@master_bp.route('/master/condominios/importar', methods=['POST'])
@jwt_required()
def master_importar_condos_csv():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('master.master_condominios'))

    if 'csv_file' not in request.files:
        flash('No se encontró el archivo en la solicitud.', 'error')
        return redirect(url_for('master.master_condominios'))

    file = request.files['csv_file']
    if file.filename == '':
        flash('No se seleccionó ningún archivo.', 'error')
        return redirect(url_for('master.master_condominios'))

    if file and file.filename.endswith('.csv'):
        try:
            stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
            csv_reader = csv.DictReader(stream)
            created_count = 0
            errors = []

            for row in csv_reader:
                if Condominium.query.filter_by(subdomain=row['subdomain']).first() or Condominium.query.filter_by(ruc=row['ruc']).first():
                    errors.append(f"Condominio con subdominio {row['subdomain']} o RUC {row['ruc']} ya existe.")
                    continue

                admin = User.query.filter_by(email=row['admin_email']).first()
                if not admin:
                    errors.append(f"El administrador con email {row['admin_email']} no fue encontrado.")
                    continue

                new_condo = Condominium(
                    name=row['name'], legal_name=row.get('legal_name'), email=row.get('email'), ruc=row['ruc'],
                    main_street=row['main_street'], cross_street=row['cross_street'], city=row['city'], country=row.get('country', 'Ecuador'),
                    subdomain=row['subdomain'], status='ACTIVO', admin_user_id=admin.id, created_by=user.id
                )
                db.session.add(new_condo)
                created_count += 1
            db.session.commit()
            flash(f'{created_count} condominios creados exitosamente. Errores: {len(errors)}', 'success')
            if errors:
                flash(f"Detalles de errores: {'; '.join(errors)}", 'warning')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al procesar el archivo CSV: {e}', 'error')
        return redirect(url_for('master.master_condominios'))

    flash('Formato de archivo inválido. Por favor, sube un archivo .csv', 'error')
    return redirect(url_for('master.master_condominios'))

@master_bp.route('/master/condominios/editar/<int:condo_id>', methods=['GET', 'POST'])
@jwt_required()
def editar_condominio(condo_id):
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))

    condo_to_edit = Condominium.query.get_or_404(condo_id)
    administradores = User.query.filter(User.role.in_(['ADMIN', 'MASTER'])).all()

    if request.method == 'POST':
        try:
            # Actualización robusta de campos
            if request.form.get('name'): condo_to_edit.name = request.form.get('name')
            if request.form.get('legal_name') is not None: condo_to_edit.legal_name = request.form.get('legal_name')
            if request.form.get('email') is not None: condo_to_edit.email = request.form.get('email')
            if request.form.get('ruc') is not None: condo_to_edit.ruc = request.form.get('ruc')
            if request.form.get('main_street'): condo_to_edit.main_street = request.form.get('main_street')
            if request.form.get('cross_street'): condo_to_edit.cross_street = request.form.get('cross_street')
            if request.form.get('house_number') is not None: condo_to_edit.house_number = request.form.get('house_number')
            if request.form.get('city'): condo_to_edit.city = request.form.get('city')
            
            country_input = request.form.get('country')
            if country_input:
                condo_to_edit.country = country_input
            elif not condo_to_edit.country:
                condo_to_edit.country = 'Ecuador'

            if request.form.get('latitude'): 
                condo_to_edit.latitude = float(request.form.get('latitude'))
            
            if request.form.get('longitude'):
                condo_to_edit.longitude = float(request.form.get('longitude'))

            subdomain_input = request.form.get('subdomain')
            if subdomain_input:
                condo_to_edit.subdomain = subdomain_input
            
            if request.form.get('status'):
                condo_to_edit.status = request.form.get('status')
                
            admin_id_input = request.form.get('admin_user_id')
            if admin_id_input:
                condo_to_edit.admin_user_id = int(admin_id_input)

            # Contacto de Facturación (Opcional)
            billing_contact_input = request.form.get('billing_contact_id')
            if billing_contact_input:
                condo_to_edit.billing_contact_id = int(billing_contact_input)
            else:
                condo_to_edit.billing_contact_id = None

            # --- LÓGICA PARA ACTUALIZAR MÓDULOS ---
            # Los interruptores legacy han sido eliminados para evitar discrepancias.
            # Ahora la configuración se hace exclusivamente vía 'configure_condo_modules'.
            
            db.session.commit()
            flash('Condominio actualizado exitosamente.', 'success')
            return redirect(url_for('master.master_condominios'))
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al editar el condominio: {e}")
            flash(f'Error al editar el condominio: {e}', 'error')

    return render_template('master/editar_condominio.html', user=user, condo=condo_to_edit, administradores=administradores)


@master_bp.route('/master/descargar-plantilla-unidades')
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

@master_bp.route('/master/condominios/inactivar/<int:condo_id>', methods=['POST'])
@jwt_required()
def inactivar_condominio(condo_id):
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('master.master_condominios'))

    condo_to_inactivate = Condominium.query.get_or_404(condo_id)
    condo_to_inactivate.status = 'INACTIVO'
    db.session.commit()
    flash(f'El condominio "{condo_to_inactivate.name}" ha sido inactivado.', 'success')
    return redirect(url_for('master.master_condominios'))

from app.services.whatsapp import WhatsAppService

@master_bp.route('/master/comunicaciones', methods=['GET'])
@jwt_required()
def master_comunicaciones():
    """
    Panel de comunicaciones globales para el MASTER.
    """
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))

    # Obtener el condominio "Sandbox" o donde resida el Master
    # Lógica: Buscar por tenant del usuario, si no, buscar por subdomain 'sandbox'
    condominium = None
    if user.tenant:
        condominium = Condominium.query.filter_by(subdomain=user.tenant).first()
    
    if not condominium:
        # Fallback: Buscar sandbox
        condominium = Condominium.query.filter_by(subdomain='sandbox').first()
    
    if not condominium:
        flash("No se encontró un condominio base (Sandbox) para la configuración del Master.", "warning")

    # Obtener lista de destinatarios potenciales (Administradores)
    admins_count = User.query.filter_by(role='ADMIN', status='active').count()
    
    # Estado real/simulado usando el servicio
    whatsapp_status = 'disconnected'
    if condominium:
        ws = WhatsAppService(condominium)
        whatsapp_status = ws.get_status()

    return render_template('master/comunicaciones.html', 
                           user=user, 
                           condominium=condominium, 
                           admins_count=admins_count,
                           status=whatsapp_status)

@master_bp.route('/master/comunicaciones/qr', methods=['GET'])
@jwt_required()
def master_get_qr():
    """
    Retorna el QR para la conexión de WhatsApp.
    """
    user = get_current_user()
    if not user or user.role != 'MASTER':
        return jsonify({"error": "Acceso denegado"}), 403

    condominium = None
    if user.tenant:
        condominium = Condominium.query.filter_by(subdomain=user.tenant).first()
    if not condominium:
        condominium = Condominium.query.filter_by(subdomain='sandbox').first()
        
    if not condominium:
         return jsonify({"error": "Condominio no encontrado"}), 404
         
    ws = WhatsAppService(condominium)
    qr_data = ws.get_qr()
    
    if not qr_data:
        return jsonify({"error": "No se pudo obtener el QR"}), 500
        
    return jsonify({"qr": qr_data, "status": "SCAN_QR"})

@master_bp.route('/master/configurar-whatsapp', methods=['POST'])
@jwt_required()
def configurar_whatsapp():
    """
    Guarda la configuración del proveedor de WhatsApp para el MASTER.
    """
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))

    # Determinar condominio del Master
    condo = None
    if user.tenant:
        condo = Condominium.query.filter_by(subdomain=user.tenant).first()
    if not condo:
        condo = Condominium.query.filter_by(subdomain='sandbox').first()
    
    if not condo:
        flash("Error crítico: No tienes un condominio asignado para guardar la configuración.", "error")
        return redirect(url_for('master.master_comunicaciones'))
    
    provider = request.form.get('whatsapp_provider')
    
    if provider not in ['GATEWAY_QR', 'META_API']:
        flash("Proveedor no válido", "error")
        return redirect(url_for('master.master_comunicaciones'))
        
    condo.whatsapp_provider = provider
    
    # Actualizar configuración JSON
    if not condo.whatsapp_config:
        current_config = {}
    else:
        current_config = dict(condo.whatsapp_config)
    
    if provider == 'META_API':
        current_config['phone_id'] = request.form.get('meta_phone_id')
        current_config['business_id'] = request.form.get('meta_business_id')
        current_config['access_token'] = request.form.get('meta_access_token')
    
    condo.whatsapp_config = current_config
    flag_modified(condo, "whatsapp_config")
    
    try:
        db.session.commit()
        flash("Configuración de comunicaciones actualizada correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar configuración: {str(e)}", "error")
        
    return redirect(url_for('master.master_comunicaciones'))

@master_bp.route('/master/condominios/configurar-modulos/<int:condo_id>', methods=['GET'])
@jwt_required()
def configure_condo_modules(condo_id):
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))
    
    condo = Condominium.query.get_or_404(condo_id)
    
    # 1. Obtener TODOS los módulos globales
    all_modules = models.Module.query.order_by(models.Module.name).all()
    
    # 2. Filtrar SOLO los módulos que el condominio tiene "contratados" (legacy flags)
    # Esto asegura que solo se personalicen los módulos que realmente usan.
    active_modules = []
    for mod in all_modules:
        is_active_in_condo = False
        
        # Mapeo entre código de módulo y flag en Condominium
        if mod.code == 'documents' and condo.has_documents_module:
            is_active_in_condo = True
        elif mod.code == 'billing' and condo.has_billing_module:
            is_active_in_condo = True
        elif mod.code == 'requests' and condo.has_requests_module:
            is_active_in_condo = True
        # Para módulos nuevos que no tienen flag legacy, asumimos que si existen en la tabla CondominiumModule están activos
        # O si no tienen flag legacy, los mostramos siempre para permitir su activación futura via esta pantalla
        elif mod.code not in ['documents', 'billing', 'requests']:
             # Lógica futura: Permitir activar módulos nuevos desde aquí
             is_active_in_condo = True 
             
        if is_active_in_condo:
            active_modules.append(mod)

    # Get existing configurations
    configs = models.CondominiumModule.query.filter_by(condominium_id=condo.id).all()
    module_configs = {c.module_id: c for c in configs}
    
    return render_template('master/configure_condo_modules.html', 
                           user=user, condo=condo, 
                           all_modules=active_modules, # Pasamos solo los filtrados
                           module_configs=module_configs)

@master_bp.route('/master/condominios/guardar-config-modulo/<int:condo_id>', methods=['POST'])
@jwt_required()
def save_condo_module_config(condo_id):
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado.", "error")
        return redirect(url_for('public.login'))
    
    condo = Condominium.query.get_or_404(condo_id)
    module_id = request.form.get('module_id')
    
    config = models.CondominiumModule.query.filter_by(condominium_id=condo.id, module_id=module_id).first()
    if not config:
        config = models.CondominiumModule(condominium_id=condo.id, module_id=module_id)
        db.session.add(config)
    
    config.status = request.form.get('status')
    
    price_override = request.form.get('price_override')
    if price_override and price_override.strip():
        config.price_override = float(price_override)
    else:
        config.price_override = None
        
    config.pricing_type = request.form.get('pricing_type')
    
    db.session.commit()
    flash(f'Configuración del módulo actualizada para {condo.name}.', 'success')
    return redirect(url_for('master.configure_condo_modules', condo_id=condo.id))