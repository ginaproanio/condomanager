from app import db

def get_tenant_default():
    return 'puntablanca'

class User(db.Model):
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
    
class Unit(db.Model):
    __tablename__ = 'units'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # ✅ IDENTIFICACIÓN Y NUMERACIÓN (OBLIGATORIO PARA TODOS)
    code = db.Column(db.String(50), nullable=False, unique=True)  # "TORRE-A-APT-101", "TERRENO-A5"
    property_number = db.Column(db.String(20), nullable=False)    # "A-101", "C-25", "BOD-12"
    name = db.Column(db.String(100), nullable=False)              # "Apartamento 101", "Casa 25", "Bodega 12"
    property_type = db.Column(db.String(30), nullable=False)      # "apartamento", "casa", "local_comercial", "parqueadero", "bodega", "galpon", "terreno"
    
    # ✅ UBICACIÓN GEOGRÁFICA Y DIRECCIÓN (OBLIGATORIO PARA TODOS)
    latitude = db.Column(db.Float)       # -0.180653
    longitude = db.Column(db.Float)      # -78.467834
    
    # ✅ CALLES (OBLIGATORIO PARA TODOS)
    main_street = db.Column(db.String(100), nullable=False)       # "Av. Principal"
    cross_street = db.Column(db.String(100), nullable=False)      # "Calle Segunda"
    house_number = db.Column(db.String(20))                       # "S/N", "25-A", "102"
    address_reference = db.Column(db.Text)                        # "Frente al parque", "Entre calles 1 y 2"
    
    # ✅ UBICACIÓN FÍSICA EN CONDOMINIO (OPCIONAL)
    building = db.Column(db.String(50))  # "Torre A", "Edificio Principal" (null para terrenos/casas)
    floor = db.Column(db.String(20))     # "1", "PB", "Sótano 2" (null para terrenos/casas)
    sector = db.Column(db.String(50))    # "Zona Residencial", "Área Comercial", "Manzana A"
    
    # ✅ DIMENSIONES (OBLIGATORIO PARA TODOS)
    area_m2 = db.Column(db.Float, nullable=False)  # 85.5, 350.0 (metros cuadrados)
    
    # ✅ CAMPOS PARA CONSTRUCCIONES (NO TERRENOS)
    area_construction_m2 = db.Column(db.Float)  # Área construida (null para terrenos)
    bedrooms = db.Column(db.Integer)            # 2, 3 (null para terrenos/bodegas)
    bathrooms = db.Column(db.Integer)           # 2, 1 (null para terrenos/bodegas)
    parking_spaces = db.Column(db.Integer)      # 1, 2 (null para terrenos)
    
    # ✅ CAMPOS ESPECÍFICOS PARA TERRENOS
    front_meters = db.Column(db.Float)          # 15.0 (solo terrenos)
    depth_meters = db.Column(db.Float)          # 23.3 (solo terrenos)
    topography = db.Column(db.String(20))       # "plano", "inclinado", "irregular" (solo terrenos)
    land_use = db.Column(db.String(30))         # "residencial", "comercial", "industrial" (solo terrenos)
    
    # ✅ ESTADO Y ASIGNACIÓN (OBLIGATORIO PARA TODOS)
    status = db.Column(db.String(20), default='disponible')  # "disponible", "ocupado", "mantenimiento", "alquilado"
    current_owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    current_tenant_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # ✅ RELACIONES
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # ✅ METADATOS
    notes = db.Column(db.Text)  # Observaciones adicionales
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    
    # ✅ MÉTODOS DE DIRECCIÓN COMPLETA
    def get_full_address(self):
        """Genera dirección completa automáticamente"""
        parts = []
        if self.house_number:
            parts.append(f"{self.main_street} #{self.house_number}")
        else:
            parts.append(self.main_street)
        
        parts.append(f"y {self.cross_street}")
        
        if self.address_reference:
            parts.append(f"({self.address_reference})")
            
        return ", ".join(parts)
    
    def get_short_address(self):
        """Dirección resumida para listas"""
        return f"{self.main_street} y {self.cross_street}"    

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
