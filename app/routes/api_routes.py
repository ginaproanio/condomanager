from flask import Blueprint, jsonify, request, make_response, url_for # Importar url_for
from flask_jwt_extended import jwt_required, create_access_token, set_access_cookies, current_user
from app.auth import get_current_user
from app.models import Condominium, User, Unit
from app import db
import hashlib
from datetime import timedelta

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/auth/login', methods=['POST'])
def api_login():
    """
    Endpoint de la API para el login de usuarios.
    Recibe un JSON con email y password, y si son válidos,
    devuelve un token JWT en una cookie HTTP-Only.
    """
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Email y contraseña requeridos"}), 400

    email = data['email'].strip()
    password = data['password']
    pwd_hash = hashlib.sha256(password.encode()).hexdigest()

    user = User.query.filter_by(email=email, password_hash=pwd_hash).first()

    if not user:
        return jsonify({"error": "Credenciales incorrectas"}), 401

    if user.status != 'active':
        return jsonify({"error": f"Tu cuenta está en estado '{user.status}'"}), 403

    # Crear token y establecerlo en una cookie
    access_token = create_access_token(identity=user.id, expires_delta=timedelta(hours=12)) # 12 horas
    
    # Determinar URL de redirección basada en el rol del usuario
    redirect_url = url_for('user.dashboard') # Por defecto
    if user.role == 'MASTER':
        redirect_url = url_for('master.master_panel')
    elif user.role == 'ADMIN':
        redirect_url = url_for('admin.admin_panel')

    response = jsonify({"status": "success", "message": "Login exitoso", "user_role": user.role, "redirect_url": redirect_url})
    set_access_cookies(response, access_token)
    return response

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
