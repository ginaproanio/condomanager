from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def get_tenant_default():
    """Función segura para default, sin depender de request"""
    return 'puntablanca'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    tenant = db.Column(db.String(50), default=get_tenant_default)  # ✅ FUNCIÓN SEGURA
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')