# app/routes/document_routes.py
from flask import (
    Blueprint, render_template, request, flash, redirect, url_for,
    send_file, current_app, abort, make_response
)
from flask_jwt_extended import jwt_required
from app import db
from app.models import Document, DocumentSignature, User, Condominium, ResidentSignature, UserSpecialRole
from app.decorators import login_required, module_required
from werkzeug.utils import secure_filename
import os
import uuid
from datetime import datetime
import io
import csv

document_bp = Blueprint('document', __name__, url_prefix='/documentos')

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads', 'documents')
os.makedirs(os.path.join(UPLOAD_FOLDER, 'unsigned'), exist_ok=True)
os.makedirs(os.path.join(UPLOAD_FOLDER, 'signed'), exist_ok=True)

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_document_code(condo, doc_type="OF"):
    """
    Genera código secuencial: {TYPE}{YYYYMMDD}{PREFIX}{SEQ}
    Ej: OF20251230PUNTA0001
    """
    prefix = condo.document_code_prefix
    if not prefix:
        # Fallback: primeros 4 chars del subdominio o nombre
        source = condo.subdomain or condo.name or "DOCS"
        prefix = source[:4].upper()
    
    date_str = datetime.now().strftime('%Y%m%d')
    
    # Buscar el último documento de este condominio que coincida con el patrón del día
    # Usamos like con el patrón base para encontrar el último secuencial
    base_pattern = f"{doc_type}{date_str}{prefix}%"
    
    last_doc = Document.query.filter_by(condominium_id=condo.id)\
        .filter(Document.document_code.like(base_pattern))\
        .order_by(Document.document_code.desc())\
        .first()
        
    if last_doc and last_doc.document_code:
        try:
            # Extraer los últimos 4 dígitos
            last_seq = int(last_doc.document_code[-4:])
            new_seq = last_seq + 1
        except:
            new_seq = 1
    else:
        new_seq = 1
        
    return f"{doc_type}{date_str}{prefix}{new_seq:04d}"

def generate_unsigned_pdf(doc):
    """Genera un PDF simple a partir del contenido del documento."""
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter
    
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width / 2.0, height - 50, doc.title)
    
    # Agregamos la referencia y fecha
    p.setFont("Helvetica", 10)
    if doc.document_code:
        p.drawRightString(width - 40, height - 30, f"Ref: {doc.document_code}")
    p.drawRightString(width - 40, height - 45, f"Fecha: {datetime.now().strftime('%Y-%m-%d')}")

    p.setFont("Helvetica", 11)
    text = p.beginText(40, height - 100)
    # Simplificado: para HTML real, se necesita una librería como WeasyPrint
    for line in doc.content.replace('<p>', '').replace('</p>', '\n').split('\n'):
        text.textLine(line)
    
    p.drawText(text)
    p.save()
    
    buffer.seek(0)
    filename = f"{uuid.uuid4().hex}.pdf"
    
    # CORRECCIÓN: Asegurar que la ruta relativa no duplique 'app'
    # UPLOAD_FOLDER es 'app/static/uploads/documents'
    path = os.path.join(UPLOAD_FOLDER, 'unsigned', filename)
    
    # Asegurar directorio
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    with open(path, 'wb') as f:
        f.write(buffer.getvalue())
    
    # Guardamos la ruta relativa para servirla después (sin 'app/' al inicio)
    doc.pdf_unsigned_path = os.path.join('static', 'uploads', 'documents', 'unsigned', filename)
    db.session.commit()
    
    return doc.pdf_unsigned_path

# ==================== LÓGICA REUTILIZABLE ====================

def create_or_edit_logic(current_user, doc_id=None):
    """
    Lógica compartida para crear o editar documentos.
    Separada de la ruta para permitir decoradores diferentes si es necesario.
    """
    # 1. Resolver el contexto del Condominio del Usuario
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()

    doc = Document.query.get_or_404(doc_id) if doc_id else None

    # 2. Verificación de Seguridad (Authorization)
    if doc:
        # Permitir si es MASTER o si el documento pertenece al condominio del usuario
        if current_user.role != 'MASTER':
            if not user_condo or doc.condominium_id != user_condo.id:
                abort(403) # Forbidden

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        doc_type = request.form.get('document_type', 'OF') # Tipo seleccionado o default 'OF'
        requires_sig = 'requires_signature' in request.form
        collect_sigs = 'collect_signatures' in request.form

        if not doc:
            # Determinación segura del Condominio ID para nuevo documento
            condo_id = user_condo.id if user_condo else None
            
            if not condo_id and current_user.role != 'MASTER':
                flash("Error de integridad: Usuario sin condominio asignado.", "error")
                return redirect(url_for('document.index'))

            # Generar código oficial
            new_code = None
            if user_condo:
                new_code = generate_document_code(user_condo, doc_type=doc_type)

            doc = Document(
                title=title,
                content=content,
                created_by_id=current_user.id,
                condominium_id=condo_id,
                document_code=new_code,
                document_type=doc_type
            )
            db.session.add(doc)
            
            if new_code:
                flash(f"Documento creado correctamente. Código: {new_code}", "success")
            else:
                flash("Documento creado correctamente.", "success")
        else:
            doc.title = title
            doc.content = content
            # No permitimos cambiar el tipo de documento una vez creado para mantener la integridad del secuencial
            # doc.document_type = doc_type 
            flash("Documento actualizado.", "success")

        doc.requires_signature = requires_sig
        doc.collect_signatures_from_residents = collect_sigs
        if collect_sigs and not doc.public_signature_link:
            doc.generate_public_link()

        db.session.commit()
        generate_unsigned_pdf(doc)
        return redirect(url_for('document.view', doc_id=doc.id))

    return render_template('documents/editor.html', doc=doc)

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
        docs = Document.query.filter_by(condominium_id=condominium.id).order_by(Document.created_at.desc()).all()
    
    return render_template('documents/index.html', documents=docs, has_premium_access=has_premium_access)

@document_bp.route('/nuevo', methods=['GET', 'POST'])
@module_required('documents') # ESTO SIGUE PROTEGIDO (Solo Premium)
def create(current_user): # Renombrado para claridad
    return create_or_edit_logic(current_user)

@document_bp.route('/<int:doc_id>/editar', methods=['GET', 'POST'])
@module_required('documents') # ESTO SIGUE PROTEGIDO (Solo Premium)
def edit(current_user, doc_id):
    return create_or_edit_logic(current_user, doc_id)

@document_bp.route('/<int:doc_id>')
# @module_required('documents') # <-- COMENTADO: Ahora todos pueden ver (Freemium)
@login_required
def view(current_user, doc_id):
    # Asegurar que pertenece al condominio del usuario
    doc = Document.query.get_or_404(doc_id)
    
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
    
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)
        
    return render_template('documents/view.html', doc=doc)

@document_bp.route('/<int:doc_id>/descargar-sin-firmar')
# @module_required('documents') # <-- COMENTADO: Descarga permitida para todos
@login_required
def download_unsigned(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
    
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)
        
    if not doc.pdf_unsigned_path or not os.path.exists(os.path.join('app', doc.pdf_unsigned_path)):
        generate_unsigned_pdf(doc)
    return send_file(os.path.join('app', doc.pdf_unsigned_path), as_attachment=True, download_name=f"{doc.title}_SIN_FIRMAR.pdf")

@document_bp.route('/<int:doc_id>/firmar', methods=['GET', 'POST'])
@module_required('documents') # PROTEGIDO: Firmar requiere módulo premium
def sign(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    # Validación manual de tenant (seguridad extra)
    user_condo = None
    if current_user.tenant:
        user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
        
    if not user_condo or doc.condominium_id != user_condo.id:
        abort(403)

    if request.method == 'POST' and request.form.get('action') == 'upload_physical':
        file = request.files.get('signed_file')
        if not file or file.filename == '':
            flash("No se seleccionó ningún archivo.", "danger")
            return redirect(request.url)
        
        if allowed_file(file.filename):
            filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
            path = os.path.join(UPLOAD_FOLDER, 'signed', filename)
            file.save(path)

            doc.pdf_signed_path = os.path.join('static', 'uploads', 'documents', 'signed', filename)
            doc.signature_type = 'physical'
            doc.status = 'signed'
            
            sig = DocumentSignature(document_id=doc.id, user_id=current_user.id, signature_type='physical', ip_address=request.remote_addr)
            db.session.add(sig)
            db.session.commit()
            flash("¡Documento firmado físicamente y subido con éxito!", "success")
            return redirect(url_for('document.view', doc_id=doc.id))
        else:
            flash("Solo se permiten archivos PDF.", "danger")

    return render_template('documents/sign_options.html', doc=doc)

@document_bp.route('/<int:doc_id>/estado-firmas')
@login_required
def view_signatures_status(current_user, doc_id):
    doc = Document.query.get_or_404(doc_id)
    
    # Seguridad: Verificar condominio
    condo = None
    if current_user.tenant:
        condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
        
    # Permitir si es el dueño del condominio o si es MASTER
    if current_user.role != 'MASTER':
        if not condo or (doc.condominium_id and doc.condominium_id != condo.id):
            abort(403)
    else:
        # Si es master, obtenemos el condominio del documento para buscar residentes
        if doc.condominium_id:
            condo = Condominium.query.get(doc.condominium_id)
            
    # Firmas registradas (Públicas - ResidentSignature)
    signatures = ResidentSignature.query.filter_by(document_id=doc.id).order_by(ResidentSignature.signed_at.desc()).all()
    signed_cedulas = {sig.cedula for sig in signatures}
    
    # Residentes registrados en el sistema que NO han firmado
    pending_residents = []
    if doc.condominium_id and condo:
        # Buscamos usuarios activos del condominio
        all_residents = User.query.filter(
            User.tenant == condo.subdomain, 
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

    # Lógica de envío (Email/WhatsApp) a implementar aquí
    doc.status = 'sent'
    db.session.commit()
    flash("Documento marcado como enviado.", "success")
    return redirect(url_for('document.index'))

# ==================== RUTAS PÚBLICAS PARA RECOLECCIÓN DE FIRMAS ====================

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
    
    user_condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
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