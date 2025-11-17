from app import db
from datetime import datetime, date  # ← AGREGADO para Date/DateTime

def get_tenant_default():
    return 'puntablanca'

# 1. USER (primero, para que las FK lo encuentren)
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    password_hash = db.Column(db.String(255))
    tenant = db.Column(db.String(50), default=get_tenant_default)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

# 2. CONFIGURACIÓN CONDOMINIO
class CondominioConfig(db.Model):
    __tablename__ = 'condominio_config'
    __table_args__ = {'extend_existing': True}

    tenant = db.Column(db.String(50), primary_key=True)
    primary_color = db.Column(db.String(7), default='#2c5aa0')
    logo_url = db.Column(db.String(255))
    nombre_comercial = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<CondominioConfig {self.tenant}>'

# 3. CONDOMINIUM (UNA SOLA CLASE, COMPLETA)
class Condominium(db.Model):
    __tablename__ = 'condominiums'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    legal_name = db.Column(db.String(200))
    ruc = db.Column(db.String(20), unique=True)
    main_street = db.Column(db.String(100), nullable=False)
    cross_street = db.Column(db.String(100), nullable=False)
    house_number = db.Column(db.String(20))
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False, default='Ecuador')
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    subdomain = db.Column(db.String(100), unique=True)
    status = db.Column(db.String(30), default='PENDIENTE_APROBACION')
    billing_day = db.Column(db.Integer, default=1)
    grace_days = db.Column(db.Integer, default=5)
    trial_start_date = db.Column(date)
    trial_end_date = db.Column(date)
    notes = db.Column(db.Text)

    # FK corregidas a 'users.id'
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    admin_user = db.relationship('User', foreign_keys=[admin_user_id], backref='admin_condominiums')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_condominiums')
    units = db.relationship('Unit', backref='condominium', lazy=True, cascade='all, delete-orphan')

    def get_full_address(self):
        parts = [self.main_street]
        if self.house_number:
            parts.append(f"#{self.house_number}")
        parts.append(f"y {self.cross_street}")
        parts.append(f"- {self.city}, {self.country}")
        return " ".join(parts)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'subdomain': self.subdomain,
            'status': self.status,
            'total_units': len(self.units),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

# 4. USER SPECIAL ROLE
class UserSpecialRole(db.Model):
    __tablename__ = 'user_special_roles'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    asignado_por = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    fecha_inicio = db.Column(date, nullable=False)
    fecha_fin = db.Column(date)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# 5. INVOICE
class Invoice(db.Model):
    __tablename__ = 'invoices'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(date, nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.now)

# 6. UNIT (última, para que todas las FK estén definidas)
class Unit(db.Model):
    __tablename__ = 'units'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    property_number = db.Column(db.String(50), nullable=False)
    name = db.Column(db.String(100))
    property_type = db.Column(db.String(50))
    main_street = db.Column(db.String(200))
    cross_street = db.Column(db.String(200))
    house_number = db.Column(db.String(20))
    address_reference = db.Column(db.Text)
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    building = db.Column(db.String(50))
    floor = db.Column(db.String(20))
    sector = db.Column(db.String(50))
    area_m2 = db.Column(db.Float)
    area_construction_m2 = db.Column(db.Float)
    bedrooms = db.Column(db.Integer)
    bathrooms = db.Column(db.Integer)
    parking_spaces = db.Column(db.Integer)
    front_meters = db.Column(db.Float)
    depth_meters = db.Column(db.Float)
    topography = db.Column(db.String(50))
    land_use = db.Column(db.String(100))
    notes = db.Column(db.Text)

    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ← CORREGIDO
    status = db.Column(db.String(20), default='disponible')
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)