from flask import (
    Blueprint, render_template, redirect,
    current_app, flash, request, url_for
)
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import db, User, Document, Condominium, Unit, DocumentSignature, Payment # Importar DocumentSignature
import hashlib
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename

# Librerías para validación criptográfica
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend

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

    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    
    # --- Lógica de Notificaciones de Documentos ---
    new_docs_count = 0
    condo_id = None
    
    if user_unit and user_unit.condominium_id:
        condo_id = user_unit.condominium_id
    elif user.tenant:
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
        
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)

    if request.method == 'POST':
        # --- ACTUALIZACIÓN DE REDES SOCIALES ---
        if 'update_social' in request.form:
            user.twitter_profile = request.form.get('twitter_profile', '').strip()
            user.facebook_profile = request.form.get('facebook_profile', '').strip()
            user.instagram_profile = request.form.get('instagram_profile', '').strip()
            user.linkedin_profile = request.form.get('linkedin_profile', '').strip()
            user.tiktok_profile = request.form.get('tiktok_profile', '').strip()
            
            try:
                db.session.commit()
                flash("Perfiles sociales actualizados correctamente.", "success")
            except Exception as e:
                db.session.rollback()
                flash(f"Error al actualizar perfil social: {str(e)}", "danger")
            
            return redirect(url_for('user.perfil'))

        # Lógica para subir certificado .p12/.pfx
        if 'certificate' in request.files:
            file = request.files['certificate']
            password = request.form.get('cert_password')
            
            # Validar que se haya seleccionado un archivo
            if file.filename == '':
                flash("No se seleccionó ningún archivo", "warning")
            elif file and file.filename.lower().endswith(('.p12', '.pfx')):
                if not password:
                    flash("Debes ingresar la contraseña del certificado para poder validarlo.", "warning")
                else:
                    try:
                        # Leer el contenido binario
                        file_data = file.read()
                        
                        # --- VALIDACIÓN CRIPTOGRÁFICA REAL ---
                        try:
                            # Intentamos abrir el contenedor PKCS12 con la clave proporcionada
                            # Si la clave es incorrecta o el archivo no es válido, lanzará excepción
                            pkcs12.load_key_and_certificates(
                                file_data,
                                password.encode(),
                                backend=default_backend()
                            )
                        except ValueError:
                            flash("Error de Validación: La contraseña ingresada es INCORRECTA para este certificado.", "danger")
                            return redirect(url_for('user.perfil'))
                        except Exception as e:
                            flash(f"Error de Validación: El archivo del certificado está dañado o no es válido. Detalle: {str(e)}", "danger")
                            return redirect(url_for('user.perfil'))

                        # Si pasamos aquí, el certificado y la clave son VÁLIDOS
                        
                        # Guardar en base de datos
                        user.signature_certificate = file_data
                        # Guardamos hash solo para verificar propiedad futura, la firma real requerirá input manual
                        user.signature_cert_password_hash = hashlib.sha256(password.encode()).hexdigest()
                        user.has_electronic_signature = True
                        
                        db.session.commit()
                        flash("✅ Firma electrónica validada y configurada exitosamente.", "success")
                    except Exception as e:
                        db.session.rollback()
                        flash(f"Error interno al guardar: {str(e)}", "danger")
            else:
                flash("Formato de archivo no válido. Solo se permiten archivos .p12 o .pfx", "danger")
                
        return redirect(url_for('user.perfil'))

    return render_template('user/profile.html', user=user, config=config)

@user_bp.route('/unidades')
@jwt_required()
def unidades():
    user = get_current_user()
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/unidades.html', mensaje="Gestión de Unidades", config=config, user=user)

@user_bp.route('/pagos')
@jwt_required()
def pagos():
    user = get_current_user()
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    
    # Obtener el condominio para verificar config de pagos
    condominium = None
    if user.unit and user.unit.condominium_id:
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
def reportar_pago():
    user = get_current_user()
    
    # Validar que pertenezca a un condominio
    condo = None
    if user.unit and user.unit.condominium_id:
        condo = Condominium.query.get(user.unit.condominium_id)
    elif user.tenant:
        condo = Condominium.query.filter_by(subdomain=user.tenant).first()
    
    if not condo:
        flash("No tienes un condominio asignado para reportar pagos.", "error")
        return redirect(url_for('user.pagos'))

    # Validar archivo
    if 'proof_file' not in request.files:
        flash('No se subió ningún archivo.', 'error')
        return redirect(url_for('user.pagos'))
    
    file = request.files['proof_file']
    if file.filename == '':
        flash('No seleccionaste ningún archivo.', 'error')
        return redirect(url_for('user.pagos'))
        
    if file:
        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user.id}_{file.filename}")
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'payments')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Crear registro de pago
        # El monto puede venir con comas, las reemplazamos por puntos
        amount_str = request.form.get('amount', '0').replace(',', '.')
        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0
            
        new_payment = Payment(
            amount=amount,
            amount_with_tax=amount, # Asumimos exento de IVA por ahora para transferencias de alícuotas
            currency='USD',
            description=request.form.get('description'),
            status='PENDING_REVIEW',
            payment_method='TRANSFER',
            proof_of_payment=filename,
            user_id=user.id,
            condominium_id=condo.id,
            unit_id=user.unit_id if user.unit_id else None,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(new_payment)
            db.session.commit()
            flash('Comprobante subido correctamente. Tu pago está en revisión por la administración.', 'success')
            # Mantener al usuario en la misma página para ver su estado o hacer otro pago
            return redirect(url_for('user.pagos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el reporte: {str(e)}', 'error')
            return redirect(url_for('user.pagos'))
            
    # Fallback redirect if request method is not POST (should be handled by @route methods)
    return redirect(url_for('user.pagos'))

@user_bp.route('/reportes')
@jwt_required()
def reportes():
    user = get_current_user()
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    
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
