from flask import Blueprint, request, redirect, url_for, flash, current_app, session
from flask_jwt_extended import jwt_required, current_user
from app.models import db, Condominium
from app.services.google_drive_service import GoogleDriveService
from app.decorators import condominium_admin_required

google_drive_bp = Blueprint('google_drive', __name__, url_prefix='/google_drive')

@google_drive_bp.route('/connect', methods=['GET'])
@jwt_required()
def connect_drive():
    """Inicia el flujo de conexión con Google Drive."""
    # Verificar que el usuario sea administrador de un condominio
    condo_id = session.get('current_condominium_id') # Asumiendo que guardamos esto en sesión o lo deducimos
    
    # Alternativa: Usar el condominio del usuario actual si es admin
    # La lógica de decorators podría necesitar ajuste, aquí lo hago manual para seguridad
    if not current_user.tenant:
        flash("No tienes un condominio asignado.", "error")
        return redirect(url_for('admin.dashboard'))
        
    condo = Condominium.query.filter_by(subdomain=current_user.tenant).first()
    if not condo:
         flash("Condominio no encontrado.", "error")
         return redirect(url_for('admin.dashboard'))

    # Guardar ID en sesión para el callback
    session['oauth_condo_id'] = condo.id
    
    service = GoogleDriveService(condominium=condo)
    auth_url, state = service.get_auth_flow()
    
    # session['oauth_state'] = state # Opcional: Validar state para CSRF
    
    return redirect(auth_url)

@google_drive_bp.route('/callback', methods=['GET'])
def callback():
    """Maneja el retorno de Google con el código de autorización."""
    code = request.args.get('code')
    error = request.args.get('error')
    
    if error:
        flash(f"Error en autorización de Google: {error}", "error")
        return redirect(url_for('admin.dashboard'))
        
    condo_id = session.get('oauth_condo_id')
    if not condo_id:
        flash("Sesión expirada o inválida.", "error")
        return redirect(url_for('public.login'))
        
    condo = Condominium.query.get(condo_id)
    if not condo:
        flash("Condominio no encontrado.", "error")
        return redirect(url_for('admin.dashboard'))
        
    try:
        service = GoogleDriveService(condominium=condo)
        result = service.connect_and_setup(code)
        
        # Actualizar Condominio
        condo.drive_refresh_token = result['refresh_token']
        condo.drive_root_folder_id = result['root_id']
        condo.drive_folders_map = result['folders_map']
        
        db.session.commit()
        
        flash("Google Drive conectado exitosamente. Estructura de carpetas creada.", "success")
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error Setup Drive: {str(e)}")
        flash(f"Ocurrió un error configurando Drive: {str(e)}", "error")
        
    return redirect(url_for('admin.dashboard'))



