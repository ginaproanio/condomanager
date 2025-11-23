from app.extensions import db
from sqlalchemy import Boolean, Date     # ← ESTA LÍNEA ES LA CLAVE FINAL
from datetime import datetime

def get_tenant_default():
    return 'puntablanca'

# 1. USER (primero, para que las FK lo encuentren)
class User(db.Model):
    __tablename__ = 'users'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    cedula = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.Date)
    cellphone = db.Column(db.String(20))
    city = db.Column(db.String(50))
    country = db.Column(db.String(50))
    password_hash = db.Column(db.String(255))
    tenant = db.Column(db.String(50)) # El tenant debe ser asignado explícitamente por la lógica de negocio
    role = db.Column(db.String(20), default='user')
    status = db.Column(db.String(20), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.now)

    # --- SOLUCIÓN AL PROBLEMA PRINCIPAL ---
    # Añadir la columna para relacionar al usuario con una unidad.
    # Es 'nullable' porque un usuario puede no estar asignado a una unidad al registrarse.
    unit_id = db.Column(db.Integer, db.ForeignKey('units.id'), nullable=True)
    unit = db.relationship('Unit', backref='residents', lazy=True, foreign_keys=[unit_id])

    # Propiedad para obtener el nombre completo fácilmente, sin cambiar la base de datos.
    @property
    def name(self):
        return f"{self.first_name} {self.last_name}"
    
    # --- Firma Electrónica ---
    has_electronic_signature = db.Column(db.Boolean, default=False)
    signature_certificate = db.Column(db.LargeBinary) # Almacena el archivo .p12 encriptado
    signature_cert_password_hash = db.Column(db.String(255)) # Hash de la contraseña del certificado


# 2. CONFIGURACIÓN CONDOMINIO
class CondominiumConfig(db.Model):
    __tablename__ = 'condominium_configs'
    __table_args__ = {'extend_existing': True}

    tenant = db.Column(db.String(50), primary_key=True)
    primary_color = db.Column(db.String(7), default='#2c5aa0')
    logo_url = db.Column(db.String(255))
    commercial_name = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<CondominiumConfig {self.tenant}>'

# 3. CONDOMINIUM (UNA SOLA CLASE, COMPLETA)
class Condominium(db.Model):
    __tablename__ = 'condominiums'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    legal_name = db.Column(db.String(200))
    email = db.Column(db.String(255)) # Correo oficial del condominio
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
    trial_start_date = db.Column(Date)
    trial_end_date = db.Column(Date)
    notes = db.Column(db.Text)
    # --- Módulos Contratables ---
    has_documents_module = db.Column(db.Boolean, default=False, nullable=False) # Módulo "Firmas & Comunicados"
    has_billing_module = db.Column(db.Boolean, default=False, nullable=False)   # Módulo "Facturación"
    has_requests_module = db.Column(db.Boolean, default=False, nullable=False)  # Módulo "Requerimientos"

    # FK corregidas a 'users.id'
    admin_user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    legal_representative_id = db.Column(db.Integer, db.ForeignKey('users.id')) # Representante Legal
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Relaciones
    legal_representative = db.relationship('User', foreign_keys=[legal_representative_id], backref='legal_condominiums')
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
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    start_date = db.Column(Date, nullable=False)
    end_date = db.Column(Date)
    is_active = db.Column(Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.now)

# 5. INVOICE
class Invoice(db.Model):
    __tablename__ = 'invoices'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(Date, nullable=False)
    status = db.Column(db.String(20), default='PENDING')
    created_at = db.Column(db.DateTime, default=datetime.now)

# 6. UNIT (última, para que todas las FK estén definidas)
class Unit(db.Model):
    __tablename__ = 'units'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True)
    property_tax_code = db.Column(db.String(100), unique=True)
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

# --- MÓDULO DE FIRMAS & COMUNICADOS ---
import random
import string

class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(300), nullable=False)
    content = db.Column(db.Text, nullable=False)
    pdf_unsigned_path = db.Column(db.String(500))
    pdf_signed_path = db.Column(db.String(500))
    signature_type = db.Column(db.String(20), default='none')
    status = db.Column(db.String(20), default='draft')
    requires_signature = db.Column(db.Boolean, default=True)

    created_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_by = db.relationship('User', foreign_keys=[created_by_id])
    condominium_id = db.Column(db.Integer, db.ForeignKey('condominiums.id'))
    condominium = db.relationship('Condominium', backref='documents')

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    signatures = db.relationship('DocumentSignature', backref='document', lazy=True, cascade='all, delete-orphan')

    # Para recolección de firmas públicas
    collect_signatures_from_residents = db.Column(db.Boolean, default=False)
    public_signature_link = db.Column(db.String(100), unique=True)
    signature_count = db.Column(db.Integer, default=0)

    def generate_public_link(self):
        if not self.public_signature_link:
            self.public_signature_link = ''.join(random.choices(string.ascii_letters + string.digits, k=12))

class DocumentSignature(db.Model):
    __tablename__ = 'document_signatures'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    signed_by = db.relationship('User')
    signature_type = db.Column(db.String(20), nullable=False)
    signed_at = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(45))

class ResidentSignature(db.Model):
    __tablename__ = 'resident_signatures'
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    cedula = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20))
    ip_address = db.Column(db.String(45))
    signed_at = db.Column(db.DateTime, default=datetime.utcnow)
    document = db.relationship('Document', backref='resident_signatures')