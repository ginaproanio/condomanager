from flask_jwt_extended import get_jwt_identity
from app.models import User

def get_current_user():
    """Obtiene el usuario actual de forma segura (compatible con JWT que guarda solo ID)"""
    user_id = get_jwt_identity()
    if not user_id:
        return None
    return User.query.get(int(user_id))
