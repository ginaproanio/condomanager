from flask import (
    Blueprint, render_template, redirect, url_for,
    current_app, flash, request, session, abort, Response
)
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from sqlalchemy.orm.attributes import flag_modified
from app import db
from app.models import User, Condominium, Unit, UserSpecialRole
from app.auth import get_current_user
from app.decorators import condominium_admin_required
from datetime import date, datetime
import io
import csv

admin_bp = Blueprint('admin', __name__)

def is_authorized_admin_for_condo(user, condominium):
    """
    Función de seguridad centralizada para verificar si un usuario es un administrador autorizado
    para un condominio específico.
    """
    if not user or not condominium:
        return False
    # --- LÓGICA DE AUTORIZACIÓN ÚNICA Y DEFINITIVA ---
    # La única fuente de verdad es la asignación explícita en la tabla de condominios.
    return user.role == 'ADMIN' and condominium.admin_user_id == user.id

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

@admin_bp.route('/admin/condominio/<int:condominium_id>', methods=['GET', 'POST'])
@jwt_required()
def admin_condominio_panel(condominium_id):
    """
    Panel de gestión específico para un condominio.
    Muestra las unidades y opciones de gestión.
    """
    current_user = get_current_user()
    condominium = Condominium.query.get_or_404(condominium_id)

    # --- GUARDIÁN ÚNICO Y ESTRICTO ---
    if not is_authorized_admin_for_condo(current_user, condominium):
        flash("No tienes acceso a este panel de administración de condominio o no estás asignado a este condominio. Por favor, inicia sesión como un Administrador autorizado.", "error")
        return redirect(url_for('public.login'))

    # Si la autorización pasa, se obtiene el resto de la información.
    pending_users_in_condo = User.query.filter_by(tenant=condominium.subdomain, status='pending').all()
    users_in_condo = User.query.filter(User.tenant == condominium.subdomain, User.status != 'pending').all()
    units = Unit.query.filter_by(condominium_id=condominium_id).order_by(Unit.name).all()
    
    # --- AGREGAR ESTO ---
    # Obtener roles especiales activos para mostrarlos en la tabla
    active_special_roles = UserSpecialRole.query.filter_by(
        condominium_id=condominium.id, 
        is_active=True
    ).all()
    # --------------------

    return render_template('admin/condominio_panel.html',
                           user=current_user,
                           condominium=condominium,
                           units=units,
                           pending_users_in_condo=pending_users_in_condo,
                           users_in_condo=users_in_condo,
                           active_special_roles=active_special_roles) # <-- PASAR LA VARIABLE AQUÍ

@admin_bp.route('/admin/usuarios/roles_especiales', methods=['POST'])
@condominium_admin_required
def asignar_rol_especial(condominium_id):
    """
    Asigna un rol especial (Presidente, Secretario, etc.) a un usuario.
    """
    user_id = request.form.get('user_id')
    role = request.form.get('role')
    start_date_str = request.form.get('start_date')
    end_date_str = request.form.get('end_date')

    if not all([user_id, role, start_date_str]):
        flash("Faltan datos obligatorios.", "error")
        return redirect(url_for('admin.admin_condominio_panel', condominium_id=condominium_id))

    try:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        # Verificar que el rol sea válido
        ROLES_VALIDOS = ['PRESIDENTE', 'SECRETARIO', 'TESORERO', 'CONTADOR', 'VOCAL']
        if role not in ROLES_VALIDOS:
             flash("Rol inválido.", "error")
             return redirect(url_for('admin.admin_condominio_panel', condominium_id=condominium_id))

        # Desactivar roles previos del mismo tipo para este usuario en este condominio (opcional, según regla de negocio)
        # UserSpecialRole.query.filter_by(user_id=user_id, condominium_id=condominium_id, role=role, is_active=True).update({'is_active': False})

        new_role = UserSpecialRole(
            user_id=user_id,
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

    return redirect(url_for('admin.admin_condominio_panel', condominium_id=condominium_id))

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
    return redirect(url_for('admin.admin_condominio_panel', condominium_id=role_entry.condominium_id))

@admin_bp.route('/admin/condominio/<int:condominium_id>/comunicaciones')
@condominium_admin_required
def comunicaciones(condominium_id):
    """
    Panel de gestión de comunicaciones (WhatsApp).
    """
    condominium = Condominium.query.get_or_404(condominium_id)
    # En el futuro aquí consultaremos a la API de Twilio/Gateway para ver el estado
    whatsapp_status = 'disconnected' 
    return render_template('admin/comunicaciones.html', condominium=condominium, status=whatsapp_status)

@admin_bp.route('/admin/condominio/<int:condominium_id>/configurar-whatsapp', methods=['POST'])
@condominium_admin_required
def configurar_whatsapp(condominium_id):
    """
    Guarda la configuración del proveedor de WhatsApp (Gateway o Meta).
    """
    condo = Condominium.query.get_or_404(condominium_id)
    
    provider = request.form.get('whatsapp_provider')
    
    # Validar que sea un proveedor válido
    if provider not in ['GATEWAY_QR', 'META_API']:
        flash("Proveedor no válido", "error")
        return redirect(url_for('admin.comunicaciones', condominium_id=condominium_id))
        
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
        
    return redirect(url_for('admin.comunicaciones', condominium_id=condominium_id))

@admin_bp.route('/admin/condominio/<int:condominium_id>/reportes', methods=['GET', 'POST'])
@condominium_admin_required
def reportes_condominio(condominium_id):
    """
    Módulo de Reportes para el Administrador.
    """
    condominium = Condominium.query.get_or_404(condominium_id)
    
    if request.method == 'POST':
        tipo_reporte = request.form.get('tipo_reporte')
        
        if tipo_reporte == 'residentes':
            # Generar CSV de Residentes
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(['Unidad', 'Nombre', 'Email', 'Teléfono', 'Rol', 'Estado'])
            
            residentes = User.query.filter(
                User.tenant == condominium.subdomain,
                User.status == 'active'
            ).order_by(User.unit_id).all()
            
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
    total_unidades = Unit.query.filter_by(condominium_id=condominium.id).count()
    total_residentes = User.query.filter_by(tenant=condominium.subdomain, status='active').count()
    
    return render_template('admin/reportes.html', 
                           condominium=condominium,
                           stats={'unidades': total_unidades, 'residentes': total_residentes})

@admin_bp.route('/admin/condominio/<int:condominium_id>/configuracion-pagos', methods=['GET', 'POST'])
@condominium_admin_required
def configuracion_pagos(condominium_id):
    """
    Configuración de la Pasarela de Pagos (PayPhone) para el Condominio.
    """
    condo = Condominium.query.get_or_404(condominium_id)
    
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
            
        return redirect(url_for('admin.configuracion_pagos', condominium_id=condo.id))
        
    return render_template('admin/config_pagos.html', condominium=condo)
