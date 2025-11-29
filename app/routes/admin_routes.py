from flask import (
    Blueprint, render_template, redirect, url_for,
    current_app, flash, request, session, abort, Response, g
)
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
from sqlalchemy.orm import joinedload # Optimización N+1
from app import db
from app.models import User, Condominium, Unit, UserSpecialRole, Payment
from app.auth import get_current_user, is_authorized_admin_for_condo
from app.decorators import admin_tenant_required, protect_internal_tenant
from app.utils.validation import validate_file # Importar validación
from datetime import date, datetime
import io
import csv
import os # Importar os a nivel de módulo
from werkzeug.utils import secure_filename # Importar secure_filename a nivel de módulo

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/aprobar/<int:user_id>')
@jwt_required()
def approve_user(user_id): # Renombrado para consistencia
    # ... (la lógica interna de esta función debe ser revisada, pero no es la causa del bloqueo)
    pass

@admin_bp.route('/rechazar/<int:user_id>')
@jwt_required()
def reject_user(user_id): # Renombrado para consistencia
    # ... (la lógica interna de esta función debe ser revisada, pero no es la causa del bloqueo)
    pass

@admin_bp.route('/admin/panel', methods=['GET', 'POST'])
@admin_tenant_required
def admin_condominio_panel():
    """
    Panel de gestión específico para un condominio.
    Muestra las unidades y opciones de gestión.
    """
    current_user = get_current_user()
    condominium = g.condominium

    # Si la autorización pasa, se obtiene el resto de la información.
    # OPTIMIZACIÓN: Eager load de unidades para usuarios
    pending_users_in_condo = User.query.filter_by(status='pending', condominium_id=condominium.id)\
        .options(joinedload(User.unit))\
        .all()
        
    users_in_condo = User.query.filter(User.status != 'pending', User.condominium_id == condominium.id)\
        .options(joinedload(User.unit))\
        .all()
        
    # OPTIMIZACIÓN: Eager load de usuarios para unidades (si se muestran)
    units = Unit.query.filter_by(condominium_id=condominium.id).order_by(Unit.name).all()
    
    # --- AGREGAR ESTO ---
    # Obtener roles especiales activos para mostrarlos en la tabla
    # OPTIMIZACIÓN: Eager load del usuario asignado
    active_special_roles = UserSpecialRole.query.filter_by(is_active=True, condominium_id=condominium.id)\
        .options(joinedload(UserSpecialRole.user)).all()
    
    now_date = datetime.now().strftime('%Y-%m-%d')

    return render_template('admin/condominio_panel.html',
                           user=current_user,
                           condominium=condominium,
                           units=units,
                           pending_users_in_condo=pending_users_in_condo,
                           users_in_condo=users_in_condo,
                           active_special_roles=active_special_roles,
                           now_date=now_date)

@admin_bp.route('/admin/usuarios/roles_especiales', methods=['POST'])
@admin_tenant_required
def asignar_rol_especial():
    """
    Asigna un rol especial (Presidente, Secretario, etc.) a un usuario.
    """
    condominium = g.condominium
    condominium_id = condominium.id

    user_id = request.form.get('user_id')
    role = request.form.get('role')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    if not all([user_id, role, start_date_str]):
        flash("Faltan datos obligatorios.", "error")
        return redirect(url_for('admin.admin_condominio_panel'))

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        # Verificar que el rol sea válido
        ROLES_VALIDOS = ['PRESIDENTE', 'SECRETARIO', 'TESORERO', 'CONTADOR', 'VOCAL']
        if role not in ROLES_VALIDOS:
             flash("Rol inválido.", "error")
             return redirect(url_for('admin.admin_condominio_panel'))

        # Desactivar roles previos del mismo tipo para este usuario en este condominio (opcional, según regla de negocio)
        # UserSpecialRole.query.filter_by(user_id=user_id, condominium_id=condominium_id, role=role, is_active=True).update({'is_active': False})

        new_role = UserSpecialRole(
            user_id=int(user_id),
            condominium_id=condominium_id,
            role=role,
            assigned_by=get_current_user().id,
            start_date=start_date,
            end_date=end_date,
            is_active=True
        )
        
        db.session.add(new_role)
        db.session.commit()
        flash(f"Rol de {role} asignado correctamente.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al asignar rol: {str(e)}", "error")

    return redirect(url_for('admin.admin_condominio_panel'))

@admin_bp.route('/admin/usuarios/roles_especiales/revocar/<int:role_id>', methods=['POST'])
@jwt_required() # No usamos condominium_admin_required directamente porque el ID viene en el form, pero validamos adentro
def revocar_rol_especial(role_id):
    role_entry = UserSpecialRole.query.get_or_404(role_id)
    current_user = get_current_user()
    
    # Validación de seguridad manual
    condo = Condominium.query.get(role_entry.condominium_id)
    if not is_authorized_admin_for_condo(current_user, condo):
        flash("No autorizado.", "error")
        return redirect(url_for('user.dashboard'))

    role_entry.is_active = False
    role_entry.end_date = date.today()
    db.session.commit()
    
    flash("Rol revocado correctamente.", "success")
    return redirect(url_for('admin.admin_condominio_panel'))

@admin_bp.route('/admin/comunicaciones')
@admin_tenant_required
def comunicaciones():
    """
    Panel de gestión de comunicaciones (WhatsApp).
    """
    condominium = g.condominium

    # En el futuro aquí consultaremos a la API de Twilio/Gateway para ver el estado
    whatsapp_status = 'disconnected' 
    return render_template('admin/comunicaciones.html', condominium=condominium, status=whatsapp_status)

@admin_bp.route('/admin/configurar-whatsapp', methods=['POST'])
@jwt_required()
@protect_internal_tenant
def configurar_whatsapp():
    """
    Guarda la configuración del proveedor de WhatsApp (Gateway o Meta).
    """
    condo = g.condominium
    
    provider = request.form.get('whatsapp_provider')
    
    # Validar que sea un proveedor válido
    if provider not in ['GATEWAY_QR', 'META_API']:
        flash("Proveedor no válido", "error")
        return redirect(url_for('admin.comunicaciones'))
        
    condo.whatsapp_provider = provider
    
    # Actualizar configuración JSON
    # Asegurar que whatsapp_config es un diccionario
    if not condo.whatsapp_config:
        current_config = {}
    else:
        # Copiar para asegurar mutabilidad
        current_config = dict(condo.whatsapp_config)
    
    if provider == 'META_API':
        current_config['phone_id'] = request.form.get('meta_phone_id')
        current_config['business_id'] = request.form.get('meta_business_id')
        current_config['access_token'] = request.form.get('meta_access_token')
    
    # Guardar en el objeto
    condo.whatsapp_config = current_config
    
    # Flag de migración forzosa para SQLAlchmey (a veces no detecta cambios internos en JSON)
    flag_modified(condo, "whatsapp_config")
    
    try:
        db.session.commit()
        flash("Configuración de WhatsApp actualizada correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar configuración: {str(e)}", "error")
        
    return redirect(url_for('admin.comunicaciones'))

@admin_bp.route('/admin/reportes', methods=['GET', 'POST'])
@admin_tenant_required
def reportes_condominio():
    """
    Módulo de Reportes para el Administrador.
    """
    condominium = g.condominium
    condominium_id = condominium.id
    
    if request.method == 'POST':
        tipo_reporte = request.form.get('tipo_reporte')
        
        if tipo_reporte == 'residentes':
            # Generar CSV de Residentes
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Unidad', 'Nombre', 'Email', 'Teléfono', 'Rol', 'Estado'])
            
            # OPTIMIZACIÓN: Eager load de unit para el CSV
            residentes = User.query.filter_by(condominium_id=condominium_id).filter(
                User.tenant == condominium.subdomain,
                User.status == 'active'
            ).options(joinedload(User.unit))\
             .order_by(User.unit_id).all()
            
            for res in residentes:
                unidad = res.unit.property_number if res.unit else 'Sin Asignar'
                writer.writerow([unidad, res.name, res.email, res.cellphone, res.role, res.status])
                
            output.seek(0)
            return Response(
                output.getvalue().encode('utf-8-sig'), # UTF-8 con BOM
                mimetype="text/csv",
                headers={"Content-Disposition": f"attachment;filename=residentes_{condominium.name}.csv"}
            )
            
    # Estadísticas para la vista
    total_unidades = Unit.query.filter_by(condominium_id=condominium_id).count()
    total_residentes = User.query.filter_by(condominium_id=condominium_id, status='active').count()
    
    return render_template('admin/reportes.html', 
                           condominium=condominium,
                           stats={'unidades': total_unidades, 'residentes': total_residentes})

@admin_bp.route('/admin/configuracion-pagos', methods=['GET', 'POST'])
@jwt_required()
@protect_internal_tenant
def configuracion_pagos():
    """
    Configuración de la Pasarela de Pagos (PayPhone) para el Condominio.
    """
    condo = g.condominium
    condominium_id = condo.id
    
    if request.method == 'POST':
        token = request.form.get('payphone_token')
        identifier = request.form.get('payphone_id')
        
        # Guardar en JSON
        config = condo.payment_config or {}
        # Asegurarnos de que sea un dict mutable
        config = dict(config)
        
        config['token'] = token.strip() if token else ''
        config['id'] = identifier.strip() if identifier else ''
        
        condo.payment_config = config
        condo.payment_provider = 'PAYPHONE'
        
        # Flag para SQLAlchemy
        flag_modified(condo, "payment_config")
        
        try:
            db.session.commit()
            flash("Credenciales de PayPhone guardadas correctamente.", "success")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al guardar: {str(e)}", "error")
            
        return redirect(url_for('admin.configuracion_pagos'))
        
    # Obtener historial de pagos recibidos para este condominio
    # OPTIMIZACIÓN: Eager load de user y unit
    transactions = Payment.query.filter_by(condominium_id=condominium_id).order_by(Payment.created_at.desc())\
        .options(joinedload(Payment.user), joinedload(Payment.unit))\
        .all()
        
    return render_template('admin/config_pagos.html', condominium=condo, transactions=transactions)

@admin_bp.route('/admin/finanzas', methods=['GET'])
@admin_tenant_required
def finanzas():
    """
    Panel Principal de Finanzas: Muestra transacciones y pagos pendientes de aprobación.
    """
    condo = g.condominium
    condominium_id = condo.id
    
    # Pagos pendientes de revisión (Transferencias)
    # OPTIMIZACIÓN: Eager load de user y unit
    pending_payments = Payment.query.filter_by(condominium_id=condominium_id).filter_by(
        status='PENDING_REVIEW'
    ).options(joinedload(Payment.user), joinedload(Payment.unit))\
     .order_by(Payment.created_at.asc()).all()
    
    # Historial de pagos procesados (Últimos 50)
    # OPTIMIZACIÓN: Eager load de user y unit
    history_payments = Payment.query.filter_by(condominium_id=condominium_id).filter(
        Payment.status != 'PENDING_REVIEW'
    ).options(joinedload(Payment.user), joinedload(Payment.unit))\
     .order_by(Payment.created_at.desc()).limit(50).all()
    
    return render_template('admin/finanzas.html', 
                           condominium=condo, 
                           pending_payments=pending_payments,
                           history_payments=history_payments)

@admin_bp.route('/admin/pagos/aprobar/<int:payment_id>', methods=['POST'])
@jwt_required()
def aprobar_pago(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    current_user = get_current_user()
    
    # Validar permisos
    condo = Condominium.query.get(payment.condominium_id)
    if not is_authorized_admin_for_condo(current_user, condo):
        flash("No autorizado para aprobar este pago.", "error")
        return redirect(url_for('user.dashboard'))
        
    payment.status = 'APPROVED'
    payment.reviewed_by = current_user.id
    payment.review_date = datetime.utcnow()
    payment.review_notes = request.form.get('notes', 'Aprobado manualmente')
    
    db.session.commit()
    flash(f"Pago de ${payment.amount} aprobado exitosamente.", "success")
    return redirect(url_for('admin.finanzas'))

@admin_bp.route('/admin/pagos/rechazar/<int:payment_id>', methods=['POST'])
@jwt_required()
def rechazar_pago(payment_id):
    payment = Payment.query.get_or_404(payment_id)
    current_user = get_current_user()
    
    condo = Condominium.query.get(payment.condominium_id)
    if not is_authorized_admin_for_condo(current_user, condo):
        flash("No autorizado.", "error")
        return redirect(url_for('user.dashboard'))
        
    payment.status = 'REJECTED'
    payment.reviewed_by = current_user.id
    payment.review_date = datetime.utcnow()
    payment.review_notes = request.form.get('notes', 'Rechazado por administración')
    
    db.session.commit()
    flash("Pago rechazado.", "warning")
    return redirect(url_for('admin.finanzas'))

@admin_bp.route('/admin/comprobante/<filename>')
@jwt_required()
def ver_comprobante(filename):
    from flask import send_from_directory, abort
    
    # 1. Buscar el pago asociado a este archivo para validar permisos
    # En la DB se guarda como '/static/uploads/payments/filename' o similar, buscamos coincidencia parcial o exacta
    # Asumimos que payment.proof_of_payment guarda 'uploads/payments/filename' o similar
    
    # Buscamos el pago que tenga este filename exacto en su proof_of_payment
    # Se asume que proof_of_payment almacena la ruta relativa (ej: 'uploads/payments/archivo.png')
    # o el nombre del archivo. Ajustar según cómo se guarde en la DB.
    # Para mayor seguridad, usamos endswith o buscamos exactitud si se guarda solo el nombre.
    payment = Payment.query.filter(Payment.proof_of_payment.isnot(None), Payment.proof_of_payment.endswith(filename)).first()
    
    if not payment:
        abort(404)

    current_user = get_current_user()
    if not current_user:
        abort(401) # Unauthorized si el usuario no existe o el token es inválido aunque haya pasado jwt_required

    
    # 2. Verificar Autorización
    # A) Es el dueño del pago (Usuario que lo subió)
    is_owner = (payment.user_id and current_user.id == payment.user_id)
    
    # B) Es administrador del condominio al que pertenece el pago
    condo = Condominium.query.get(payment.condominium_id)
    is_admin = is_authorized_admin_for_condo(current_user, condo)
    
    # C) Es MASTER
    is_master = (current_user.role == 'MASTER')

    if not (is_owner or is_admin or is_master):
        abort(403)

    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'payments')
    return send_from_directory(upload_folder, filename)

@admin_bp.route('/admin/personalizar', methods=['POST'])
@jwt_required()
@admin_tenant_required
def personalizar_condominio():
    """
    Permite subir el logo y personalizar colores del condominio.
    """
    condo = g.condominium
    
    # 1. Obtener o crear config
    from app.models import CondominiumConfig
    config = CondominiumConfig.query.get(condo.subdomain)
    if not config:
        config = CondominiumConfig(tenant=condo.subdomain, commercial_name=condo.name)
        db.session.add(config)
        
    # 2. Procesar Color
    primary_color = request.form.get('primary_color')
    if primary_color:
        config.primary_color = primary_color
        
    # 3. Procesar Logo
    if 'logo_file' in request.files:
        file = request.files['logo_file']
        if file.filename != '':
            # VALIDACIÓN BACKEND: Tipo de archivo
            try:
                validate_file(file, allowed_extensions=['png', 'jpg', 'jpeg', 'gif', 'webp'], 
                              allowed_mimetypes=['image/png', 'image/jpeg', 'image/gif', 'image/webp'])
            except Exception as e:
                flash(f"Archivo inválido: {e.description if hasattr(e, 'description') else str(e)}", "error")
                return redirect(url_for('admin.admin_condominio_panel'))

            # Validar extensión
            ext = os.path.splitext(file.filename)[1].lower()
            
            filename = secure_filename(f"logo_{condo.id}_{int(datetime.utcnow().timestamp())}{ext}")
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'logos')
            
            # Crear directorio si no existe
            os.makedirs(upload_folder, exist_ok=True)
            
            # Guardar archivo
            file.save(os.path.join(upload_folder, filename))
            
            # Actualizar config
            config.logo_url = f"uploads/logos/{filename}"

    try:
        db.session.commit()
        flash("Personalización actualizada correctamente.", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al guardar: {str(e)}", "error")
        
    return redirect(url_for('admin.admin_condominio_panel'))
