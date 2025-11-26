from flask import (
    Blueprint, render_template, redirect,
    current_app, flash, request, url_for, g
)
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import db, User, Document, Condominium, Unit, DocumentSignature, Payment # Importar DocumentSignature
from app.extensions import limiter
from app.services.user_service import UserService
from app.services.payment_service import PaymentService
from app.exceptions import BusinessError
import os
from datetime import datetime, timedelta

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@jwt_required()
def dashboard():
    user = get_current_user()
    if not user:
        flash("Sesión inválida", "error")
        return redirect('/login')
    
    # Inyectar unidad del usuario
    user_unit = None
    if user.unit_id:
        user_unit = Unit.query.get(user.unit_id)
    elif user.email: # Fallback: buscar unidad por email del creador (temporal)
         # Lógica simple para demo: primera unidad del condominio
         pass

    tenant_subdomain = g.condominium.subdomain if g.condominium else None
    config = current_app.get_tenant_config(tenant_subdomain)
    
    # --- Lógica de Notificaciones de Documentos ---
    new_docs_count = 0
    condo_id = None
    
    if g.condominium:
        condo_id = g.condominium.id
    elif user_unit and user_unit.condominium_id:
        condo_id = user_unit.condominium_id
    elif user.tenant:
        # Fallback legacy (si el middleware falló o no aplicó)
        condo = Condominium.query.filter_by(subdomain=user.tenant).first()
        if condo:
            condo_id = condo.id
            
    if condo_id:
        # Contar documentos firmados/enviados en los últimos 7 días
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        new_docs_count = Document.query.filter(
            Document.condominium_id == condo_id,
            Document.created_at >= seven_days_ago,
            Document.status.in_(['signed', 'sent']) # Solo contar documentos públicos oficiales
        ).count()

    return render_template('user/dashboard.html', 
                           user=user, 
                           config=config, 
                           user_unit=user_unit,
                           new_docs_count=new_docs_count)

@user_bp.route('/perfil', methods=['GET', 'POST'])
@jwt_required()
def perfil():
    user = get_current_user()
    if not user:
        return redirect('/login')
        
    tenant_subdomain = g.condominium.subdomain if g.condominium else None
    config = current_app.get_tenant_config(tenant_subdomain)

    if request.method == 'POST':
        # --- ACTUALIZACIÓN DE REDES SOCIALES ---
        if 'update_social' in request.form:
            try:
                UserService.update_social_profiles(user.id, request.form)
                flash("Perfiles sociales actualizados correctamente.", "success")
            except BusinessError as e:
                 flash(e.message, "danger")
            except Exception as e:
                flash(f"Error al actualizar perfil social: {str(e)}", "danger")
            
            return redirect(url_for('user.perfil'))

        # Lógica para subir certificado .p12/.pfx
        if 'certificate' in request.files:
            try:
                UserService.upload_certificate(
                    user.id, 
                    request.files['certificate'], 
                    request.form.get('cert_password')
                )
                flash("✅ Firma electrónica validada y configurada exitosamente.", "success")
            except BusinessError as e:
                flash(e.message, "danger")
            except Exception as e:
                flash(f"Error interno: {str(e)}", "danger")
                
        return redirect(url_for('user.perfil'))

    return render_template('user/profile.html', user=user, config=config)

@user_bp.route('/unidades')
@jwt_required()
def unidades():
    user = get_current_user()
    tenant_subdomain = g.condominium.subdomain if g.condominium else None
    config = current_app.get_tenant_config(tenant_subdomain)
    return render_template('services/unidades.html', mensaje="Gestión de Unidades", config=config, user=user)

@user_bp.route('/pagos')
@jwt_required()
def pagos():
    user = get_current_user()
    tenant_subdomain = g.condominium.subdomain if g.condominium else None
    config = current_app.get_tenant_config(tenant_subdomain)
    
    # Obtener el condominio para verificar config de pagos
    condominium = None
    if g.condominium:
        condominium = g.condominium
    elif user.unit and user.unit.condominium_id:
        condominium = Condominium.query.get(user.unit.condominium_id)
    elif user.tenant:
        condominium = Condominium.query.filter_by(subdomain=user.tenant).first()
        
    return render_template('services/pagos.html', 
                           mensaje="Sistema de Pagos", 
                           config=config, 
                           condominium=condominium,
                           user=user)

@user_bp.route('/pagos/reportar', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")  # Proteger pasarela de pagos
def reportar_pago():
    user = get_current_user()
    
    # Validar que pertenezca a un condominio
    condo_id = None
    if g.condominium:
        condo_id = g.condominium.id
    elif user.unit and user.unit.condominium_id:
        condo_id = user.unit.condominium_id
    elif user.tenant:
        condo = Condominium.query.filter_by(subdomain=user.tenant).first()
        if condo:
            condo_id = condo.id
    
    try:
        PaymentService.report_manual_payment(
            user.id, 
            condo_id, 
            request.form, 
            request.files.get('proof_file')
        )
        flash('Comprobante subido correctamente. Tu pago está en revisión por la administración.', 'success')
    except BusinessError as e:
        flash(e.message, 'error')
    except Exception as e:
        flash(f'Error al guardar el reporte: {str(e)}', 'error')
            
    return redirect(url_for('user.pagos'))

@user_bp.route('/reportes')
@jwt_required()
def reportes():
    user = get_current_user()
    tenant_subdomain = g.condominium.subdomain if g.condominium else None
    config = current_app.get_tenant_config(tenant_subdomain)
    
    # --- HISTORIAL DE FIRMAS Y ACTIVIDAD ---
    # Buscar documentos firmados por el usuario
    signed_docs = DocumentSignature.query.filter_by(user_id=user.id).order_by(DocumentSignature.signed_at.desc()).all()
    
    # Buscar pagos del usuario
    payments = Payment.query.filter_by(user_id=user.id).order_by(Payment.created_at.desc()).all()
    
    return render_template('services/reportes.html', 
                           mensaje="Mi Historial", 
                           config=config, 
                           user=user,
                           signed_docs=signed_docs,
                           payments=payments)
