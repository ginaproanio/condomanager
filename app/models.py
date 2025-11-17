# app/models.py - DEJAR SOLO ESTO:
from app import db  # ✅ Importar la instancia única de __init__.py

def get_tenant_default():
    return 'puntablanca'

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    password_hash = db.Column(db.String(255))
    tenant = db.Column(db.String(50), default=get_tenant_default)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')
    
# Modelo para configuración de condominios (AGREGAR al final del archivo)
class CondominioConfig(db.Model):
    tenant = db.Column(db.String(50), primary_key=True)  # 'puntablanca', 'nuevocondo'
    primary_color = db.Column(db.String(7), default='#2c5aa0')
    logo_url = db.Column(db.String(255))
    nombre_comercial = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def __repr__(self):
        return f'<CondominioConfig {self.tenant}>'