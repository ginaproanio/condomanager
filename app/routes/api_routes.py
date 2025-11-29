from flask import Blueprint, jsonify, request, make_response, url_for, current_app, g
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies, current_user
from app.auth import get_current_user
from app.models import Condominium, User, Unit
from app import db, models
from app.extensions import limiter
from werkzeug.security import check_password_hash # ✅ Importar la función correcta
from datetime import timedelta
import traceback

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")  # Prevenir brute force
def api_login():
    """
    Endpoint de la API para el login de usuarios.
    Recibe un JSON con email y password, y si son válidos,
    devuelve un token JWT en una cookie HTTP-Only.
    """
    try:
        data = request.get_json()
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email y contraseña requeridos"}), 400

        email = data['email'].strip()
        password = data['password']

        # --- SOLUCIÓN DE INGENIERÍA: AUTENTICACIÓN POR TENANT ---
        # 1. Obtener el tenant del subdominio actual.
        tenant = g.condominium.subdomain if g.condominium else None
        current_app.logger.info(f"Login attempt for {email} on tenant: {tenant}")

        # 2. Buscar usuario por email y tenant (si aplica)
        user_query = User.query.filter_by(email=email)
        
        if tenant: # Si hay un subdominio, filtramos por tenant para todos excepto el MASTER
            user_query = user_query.filter( (User.tenant == tenant) | (User.role == 'MASTER') )
        
        user = user_query.first()

        if not user or not check_password_hash(user.password_hash, password): # ✅ Usar el hashing seguro
            # Si no se encuentra, es porque las credenciales son incorrectas O porque intenta loguearse en el subdominio equivocado.
            current_app.logger.warning(f"Login failed for {email}. Tenant: {tenant}")
            return jsonify({"error": "Credenciales incorrectas o acceso desde un subdominio no autorizado."}), 401

        if user.status != 'active':
            return jsonify({"error": f"Tu cuenta está en estado '{user.status}'"}), 403

        # Crear token y establecerlo en una cookie
        access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=12)) # 12 horas
        
        # --- SOLUCIÓN DE INGENIERÍA DEFINITIVA Y ROBUSTA ---
        # La API de login es responsable de determinar la URL final y correcta.
        redirect_url = url_for('user.dashboard') # Por defecto
        
        if user.role == 'MASTER':
            redirect_url = url_for('master.master_panel')
        elif user.role == 'ADMIN':
            # Si es ADMIN, buscar el condominio donde está explícitamente asignado.
            # Esta consulta es permitida aquí porque es para ENRUTAMIENTO, no para acceso a datos.
            admin_condo = Condominium.query.filter_by(admin_user_id=user.id).first()
            if admin_condo and admin_condo.subdomain:
                # ✅ SOLUCIÓN DEFINITIVA: Construir URL absoluta con subdominio.
                # 1. Obtener el host base (ej: condomanager.vip)
                server_name = current_app.config.get('SERVER_NAME')
                if not server_name:
                    # Fallback para desarrollo o si SERVER_NAME no está configurado
                    host_parts = request.host.split('.')
                    server_name = '.'.join(host_parts[-2:]) if len(host_parts) > 1 else request.host

                # 2. Construir la URL que activa el middleware de tenant.
                scheme = 'https' if not current_app.debug else 'http'
                admin_panel_path = url_for('admin.admin_condominio_panel') # Obtiene la ruta, ej: /admin/panel
                redirect_url = f"{scheme}://{admin_condo.subdomain}.{server_name}{admin_panel_path}"
            else:
                # Si es un ADMIN no asignado, la API devuelve un estado de 'warning'.
                # El frontend será responsable de mostrar este mensaje al usuario.
                # El frontend será responsable de mostrar este mensaje al usuario.
                response = jsonify({
                    "status": "warning", 
                    "message": "Rol de Administrador detectado, pero no estás asignado a ningún condominio.", 
                    "user_role": user.role, 
                    "redirect_url": redirect_url
                })
                set_access_cookies(response, access_token)
                return response
        
        response = jsonify({
            "status": "success", 
            "message": "Login exitoso", 
            "user_role": user.role, 
            "redirect_url": redirect_url
        })
        set_access_cookies(response, access_token)
        return response

    except Exception as e:
        current_app.logger.error(f"LOGIN INTERNAL ERROR: {str(e)}")
        traceback.print_exc()
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500

@api_bp.route('/auth/me')
@jwt_required()
def api_me():
    user = get_current_user()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 401
    return jsonify({
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "status": user.status
    })

@api_bp.route('/master/estadisticas')
@jwt_required()
def api_master_estadisticas():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        return jsonify({"error": "Acceso denegado"}), 403
    return jsonify({
        "total_condominios": Condominium.query.count(),
        "total_usuarios": User.query.count(),
        "usuarios_pendientes": User.query.filter_by(status='pending').count(),
        "unidades_totales": Unit.query.count(),
    })

@api_bp.route('/condominiums', methods=['GET'])
def get_condominiums():
    try:
        condominiums = Condominium.query.all()
        return jsonify([condo.to_dict() for condo in condominiums])
    except Exception as e:
        return jsonify({'error': 'Error al obtener condominios'}), 500
