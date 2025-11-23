from flask import (
    Blueprint, render_template, redirect,
    current_app, flash, request, url_for
)
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import db, User
import hashlib

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
        from app.models import Unit
        user_unit = Unit.query.get(user.unit_id)
    elif user.email: # Fallback: buscar unidad por email del creador (temporal)
         from app.models import Unit
         # Lógica simple para demo: primera unidad del condominio
         pass

    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    
    return render_template('user/dashboard.html', user=user, config=config, user_unit=user_unit)

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
    return render_template('services/pagos.html', mensaje="Sistema de Pagos", config=config, user=user)

@user_bp.route('/reportes')
@jwt_required()
def reportes():
    user = get_current_user()
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/reportes.html', mensaje="Reportes", config=config, user=user)
