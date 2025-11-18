from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import Condominium, User, Unit

api_bp = Blueprint('api', __name__, url_prefix='/api')

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
