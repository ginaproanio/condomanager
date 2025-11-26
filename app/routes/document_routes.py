# app/routes/document_routes.py
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for,
    send_file, current_app, abort, make_response, jsonify
)
from flask_jwt_extended import jwt_required
from sqlalchemy.orm import joinedload # Optimización
from app import db
from app.models import Document, DocumentSignature, User, Condominium, ResidentSignature, UserSpecialRole
from app.decorators import login_required, module_required
from app.services.document_service import DocumentService
from app.exceptions import BusinessError
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import io
import csv
import json

document_bp = Blueprint('document', __name__, url_prefix='/documentos')

# ==================== RUTAS DEL MÓDULO ====================

@document_bp.route('/')
@login_required
def index(current_user):
    # 1. Obtener el condominio del usuario
    condominium = None
    if current_user.tenant:
        condominium = Condominium.query.filter_by(subdomain=current_user.tenant).first()
    
    # 2. Determinar si tiene acceso PREMIUM (Módulo activado)
    has_premium_access = False
    if current_user.role == 'MASTER':
        has_premium_access = True
    elif condominium and condominium.has_documents_module:
        # Si el condominio paga, verificamos roles
        if current_user.role == 'ADMIN':
            has_premium_access = True
        else:
            # Verificar roles especiales (Presidente, Secretario)
            active_role = UserSpecialRole.query.filter(
                UserSpecialRole.user_id == current_user.id,
                UserSpecialRole.condominium_id == condominium.id,
                UserSpecialRole.role.in_(['PRESIDENTE', 'SECRETARIO']),
                UserSpecialRole.is_active == True,
                UserSpecialRole.start_date <= datetime.now().date(),
                (UserSpecialRole.end_date == None) | (UserSpecialRole.end_date >= datetime.now().date())
            ).first()
            if active_role:
                has_premium_access = True

    # 3. Obtener documentos (Todos pueden verlos, la restricción es al CREAR)
    docs = []
    if condominium:
        # OPTIMIZACIÓN: Eager load de created_by para evitar N+1 al mostrar autor
        docs = Document.query.order_by(Document.created_at.desc())\
            .options(joinedload(Document.created_by))\
            .all()
    
    return render_template('documents/index.html', documents=docs, has_premium_access=has_premium_access)

@document_bp.route('/nuevo', methods=['GET', 'POST'])
@module_required('documents') 
def create(current_user):
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()

    if request.method == 'POST':
        try:
            doc = DocumentService.create_document(current_user, request.form, user_condo)
            flash("Documento creado correctamente.", "success")
            return redirect(url_for('document.view', doc_id=doc.id))
        except BusinessError as e:
            flash(e.message, "error")
            return redirect(url_for('document.index'))
        except Exception as e:
             flash(f"Error inesperado: {str(e)}", "error")
             return redirect(url_for('document.index'))

    return render_template('documents/editor.html', doc=None)

@document_bp.route('/<int:doc_id>/editar', methods=['GET', 'POST'])
@module_required('documents')
def edit(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()

    # Security Check
    if current_user.role != 'MASTER':
        if not user_condo or doc.condominium_id != user_condo.id:
            abort(403)

    if request.method == 'POST':
        try:
            DocumentService.update_document(doc, request.form)
            flash("Documento actualizado.", "success")
            return redirect(url_for('document.view', doc_id=doc.id))
        except BusinessError as e:
             flash(e.message, "error")

    return render_template('documents/editor.html', doc=doc)

@document_bp.route('/<int:doc_id>')
@login_required
def view(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
    
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)
        
    return render_template('documents/view.html', doc=doc)

@document_bp.route('/<int:doc_id>/descargar-sin-firmar')
@login_required
def download_unsigned(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
    
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)
        
    if not doc.pdf_unsigned_path or not os.path.exists(os.path.join('app', doc.pdf_unsigned_path)):
        DocumentService.generate_unsigned_pdf(doc)
    return send_file(os.path.join('app', doc.pdf_unsigned_path), as_attachment=True, download_name=f"{doc.title}_SIN_FIRMAR.pdf")

@document_bp.route('/<int:doc_id>/firmar', methods=['GET', 'POST'])
@module_required('documents')
def sign(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
        
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)

    if request.method == 'POST':
        action = request.form.get('action')

        # --- OPCIÓN 1: SUBIDA MANUAL (FÍSICA) ---
        if action == 'upload_physical':
            try:
                DocumentService.upload_physical_signature(
                    doc, 
                    current_user, 
                    request.files.get('signed_file'),
                    request.remote_addr
                )
                flash("¡Documento firmado físicamente y subido con éxito!", "success")
                return redirect(url_for('document.view', doc_id=doc.id))
            except BusinessError as e:
                flash(e.message, "danger")
                return redirect(request.url)
            except Exception as e:
                flash(f"Error: {str(e)}", "danger")
                return redirect(request.url)

        # --- OPCIÓN 2: FIRMA ELECTRÓNICA CON UANATACA / NEXXIT ---
        elif action == 'request_uanataca':
            try:
                DocumentService.request_electronic_signature(doc, current_user, user_condo)
                flash("Solicitud de firma enviada. Por favor verifica tu correo o espera la confirmación.", "success")
                return redirect(url_for('document.view', doc_id=doc.id))
            except BusinessError as e:
                flash(e.message, "error")
            except Exception as e:
                flash(f"Error al conectar con el servicio de firma: {str(e)}", "error")

    return render_template('documents/sign_options.html', doc=doc)

@document_bp.route('/<int:doc_id>/verificar-uanataca', methods=['POST'])
@login_required
def check_uanataca_status(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first() if current_user.tenant else None
    
    try:
        success = DocumentService.check_signature_status(doc, user_condo, request.remote_addr)
        if success:
            return jsonify({"status": "success", "message": "Documento firmado correctamente"})
        return jsonify({"status": "pending", "message": "Esperando firma..."})
    except BusinessError as e:
        return jsonify({"status": "error", "message": e.message}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@document_bp.route('/<int:doc_id>/estado-firmas')
@login_required
def view_signatures_status(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    condo = None
    if current_user.tenant:
        condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
        
    if current_user.role != 'MASTER':
        if not condo or (doc.condominium_id and doc.condominium_id != condo.id):
            abort(403)
    else:
        if doc.condominium_id:
            condo = Condominium.query.get(doc.condominium_id)
            
    signatures = ResidentSignature.query.filter_by(document_id=doc.id).order_by(ResidentSignature.signed_at.desc()).all()
    signed_cedulas = {sig.cedula for sig in signatures}
    
    pending_residents = []
    if doc.condominium_id and condo:
        all_residents = User.query.filter(
            User.status == 'active'
        ).all()
        
        for res in all_residents:
            if res.cedula and res.cedula not in signed_cedulas:
                pending_residents.append(res)
                
    return render_template('documents/signatures_status.html', 
                           doc=doc, 
                           signatures=signatures, 
                           pending_residents=pending_residents)

@document_bp.route('/<int:doc_id>/enviar', methods=['POST'])
@module_required('documents')
def send(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
        
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)
        
    if doc.status != 'signed':
        flash("El documento debe estar firmado antes de enviarse.", "warning")
        return redirect(url_for('document.view', doc_id=doc.id))

    doc.status = 'sent'
    db.session.commit()
    flash("Documento marcado como enviado.", "success")
    return redirect(url_for('document.index'))

@document_bp.route('/firmar/<public_link>', methods=['GET', 'POST'])
def public_signature(public_link):
    doc = Document.query.filter_by(public_signature_link=public_link, collect_signatures_from_residents=True).first_or_404()
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        cedula = request.form.get('cedula', '').strip()
        
        if not name or not cedula:
            flash("Nombre y Cédula son obligatorios.", "danger")
            return redirect(url_for('document.public_signature', public_link=public_link))

        exists = ResidentSignature.query.filter_by(document_id=doc.id, cedula=cedula).first()
        if exists:
            flash("Ya has firmado este documento con esta cédula.", "warning")
        else:
            sig = ResidentSignature(
                document_id=doc.id,
                full_name=name,
                cedula=cedula,
                phone=request.form.get('phone', '').strip(),
                ip_address=request.remote_addr
            )
            db.session.add(sig)
            doc.signature_count = (doc.signature_count or 0) + 1
            db.session.commit()
            flash("¡FIRMA REGISTRADA CORRECTAMENTE! Gracias por tu apoyo.", "success")
        
        return redirect(url_for('document.public_signature_thanks', public_link=public_link))

    return render_template('documents/public_signature.html', doc=doc)

@document_bp.route('/firmar/<public_link>/gracias')
def public_signature_thanks(public_link):
    doc = Document.query.filter_by(public_signature_link=public_link).first_or_404()
    return render_template('documents/public_thanks.html', doc=doc)

@document_bp.route('/<int:doc_id>/descargar-firmas')
@module_required('documents')
def download_signatures(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first() if current_user.tenant else None
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)

    signatures = ResidentSignature.query.filter_by(document_id=doc.id).order_by(ResidentSignature.signed_at.asc()).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Nombre Completo', 'Cédula', 'Teléfono', 'Fecha de Firma', 'IP'])
    for sig in signatures:
        writer.writerow([sig.full_name, sig.cedula, sig.phone, sig.signed_at.strftime('%Y-%m-%d %H:%M:%S'), sig.ip_address])
    
    output.seek(0)
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=firmas_{doc.title.replace(' ', '_')}.csv"
    response.headers["Content-type"] = "text/csv"
    return response
