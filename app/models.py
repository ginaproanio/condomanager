# app/models.py - DEJAR SOLO ESTO:
from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

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
    
    # =============================================================================
# NUEVOS MODELOS PARA EL SISTEMA DE ROLES Y CONDOMINIOS
# =============================================================================

class Condominium(db.Model):
    __tablename__ = 'condominiums'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    subdomain = db.Column(db.String(100), unique=True)
    ruc = db.Column(db.String(20))
    address = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    status = db.Column(db.String(30), default='PENDIENTE_APROBACION')  # DEMO, PENDIENTE_APROBACION, ACTIVO, BLOQUEADO
    billing_day = db.Column(db.Integer, default=1)
    grace_days = db.Column(db.Integer, default=5)
    trial_start_date = db.Column(db.Date)
    trial_end_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.now())
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class UserSpecialRole(db.Model):
    __tablename__ = 'user_special_roles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # PRESIDENTE, SECRETARIO, TESORERO, CONTADOR, VOCAL
    asignado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_fin = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=db.func.now())

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, PAID, OVERDUE
    created_at = db.Column(db.DateTime, default=db.func.now())