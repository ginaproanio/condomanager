from app import db

def get_tenant_default():
    return 'puntablanca'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(100))
    phone = db.Column(db.String(20))  # ✅ NUEVO - CELULAR
    city = db.Column(db.String(50))   # ✅ NUEVO - CIUDAD  
    country = db.Column(db.String(50)) # ✅ NUEVO - PAÍS
    password_hash = db.Column(db.String(255))
    tenant = db.Column(db.String(50), default=get_tenant_default)
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=db.func.now())

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
    __table_args__ = {'extend_existing': True}  # ← AGREGAR ESTA LÍNEA
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
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Corregir referencia a 'user.id'
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # PRESIDENTE, SECRETARIO, TESORERO, CONTADOR, VOCAL
    asignado_por = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Corregir referencia a 'user.id'
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
    
class Unit(db.Model):
    __tablename__ = 'units'                    # ← Obligatorio para evitar conflictos
    __table_args__ = {'extend_existing': True} # ← Evita errores si ya existe

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
    area_construction_m2 = db.Column(db.Float, nullable=True)
    bedrooms = db.Column(db.Integer, nullable=True)
    bathrooms = db.Column(db.Integer, nullable=True)
    parking_spaces = db.Column(db.Integer, nullable=True)
    front_meters = db.Column(db.Float, nullable=True)
    depth_meters = db.Column(db.Float, nullable=True)
    topography = db.Column(db.String(50))
    land_use = db.Column(db.String(100))
    notes = db.Column(db.Text)
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)  # ← referencia a tabla 'users'
    status = db.Column(db.String(20), default='disponible')
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Condominium(db.Model):
    __tablename__ = 'condominiums'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    
    # ✅ INFORMACIÓN BÁSICA
    name = db.Column(db.String(200), nullable=False)                    # "Condominio Las Palmas"
    legal_name = db.Column(db.String(200))                             # "CONDOMINIO LAS PALMAS S.A."
    ruc = db.Column(db.String(20), unique=True)                        # "1791234567001"
    
    # ✅ UBICACIÓN GEOGRÁFICA
    main_street = db.Column(db.String(100), nullable=False)            # "Av. Principal"
    cross_street = db.Column(db.String(100), nullable=False)           # "Calle Segunda" 
    house_number = db.Column(db.String(20))                            # "S/N", "25-A"
    city = db.Column(db.String(50), nullable=False)                    # "Quito"
    country = db.Column(db.String(50), nullable=False)                 # "Ecuador"
    latitude = db.Column(db.Float)                                     # -0.180653
    longitude = db.Column(db.Float)                                    # -78.467834
    
    # ✅ CONFIGURACIÓN DEL SISTEMA
    subdomain = db.Column(db.String(100), unique=True)                 # "laspalmas", "puntablanca"
    status = db.Column(db.String(20), default='PENDIENTE_APROBACION')  # PENDIENTE_APROBACION, ACTIVO, BLOQUEADO, INACTIVO
    billing_day = db.Column(db.Integer, default=1)                     # Día del mes para facturación (1-28)
    grace_days = db.Column(db.Integer, default=5)                      # Días de gracia para pagos
    
    # ✅ PERIODO DE PRUEBA
    trial_start_date = db.Column(db.Date)
    trial_end_date = db.Column(db.Date)
    
    # ✅ ADMINISTRADOR ASIGNADO
    admin_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))   # Administrador principal
    
    # ✅ METADATOS
    notes = db.Column(db.Text)                                         # Observaciones
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))      # MAESTRO que lo creó
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # ✅ RELACIONES
    admin_user = db.relationship('User', foreign_keys=[admin_user_id], backref='admin_condominiums')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_condominiums')
    units = db.relationship('Unit', backref='condominium', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'legal_name': self.legal_name,
            'ruc': self.ruc,
            'main_street': self.main_street,
            'cross_street': self.cross_street,
            'city': self.city,
            'country': self.country,
            'subdomain': self.subdomain,
            'status': self.status,
            'admin_user': {
                'id': self.admin_user.id,
                'name': self.admin_user.name,
                'email': self.admin_user.email
            } if self.admin_user else None,
            'total_units': len(self.units),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def get_full_address(self):
        """Genera dirección completa"""
        parts = []
        if self.house_number:
            parts.append(f"{self.main_street} #{self.house_number}")
        else:
            parts.append(self.main_street)
        
        parts.append(f"y {self.cross_street}")
        parts.append(f"- {self.city}, {self.country}")
        
        return " ".join(parts)