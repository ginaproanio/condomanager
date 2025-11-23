import os
import hashlib
from app import create_app
from app.extensions import db
from app import models

def seed_initial_data():
    """
    Siembra datos iniciales en la base de datos si no existen.
    Esto incluye el usuario MASTER y la configuración del tenant por defecto.
    """
    app = create_app()
    with app.app_context():
        print("AUDIT: Iniciando script de siembra de datos iniciales.")

        # Crear usuario maestro si no existe
        master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
        if not models.User.query.filter_by(email=master_email).first():
            print(f"AUDIT: Creando usuario maestro para {master_email}...")
            master_password = os.environ.get('MASTER_PASSWORD', 'Master2025!')
            pwd_hash = hashlib.sha256(master_password.encode()).hexdigest()
            # --- CORRECCIÓN CRÍTICA ---
            # Usar los nuevos campos y añadir una cédula por defecto.
            master = models.User(
                cedula='0000000000', # Cédula por defecto para el usuario maestro
                email=master_email, first_name='Administrador', last_name='Maestro', 
                password_hash=pwd_hash,
                tenant=None, role='MASTER', status='active'
            )
            db.session.add(master)
            print("AUDIT: Usuario maestro añadido a la sesión.")
        else:
            print("✅ AUDIT: Usuario maestro ya existe.")

        # Crear configuración de tenant por defecto si no existe
        default_tenant = 'puntablanca'
        if not db.session.get(models.CondominiumConfig, default_tenant):
            print(f"AUDIT: Creando configuración para el tenant por defecto '{default_tenant}'...")
            config = models.CondominiumConfig(tenant=default_tenant, commercial_name='Punta Blanca')
            db.session.add(config)
            print("AUDIT: Configuración de tenant añadida a la sesión.")
        else:
            print(f"✅ AUDIT: Configuración para '{default_tenant}' ya existe.")

        # --- LÓGICA SANDBOX PARA DESARROLLO ---
        # Asegurar que existe un condominio de pruebas y el Master está asignado a él
        # para evitar errores de "NoneType" al crear documentos.
        master_user = models.User.query.filter_by(role='MASTER').first()
        if master_user:
            sandbox_subdomain = 'sandbox'
            sandbox = models.Condominium.query.filter_by(subdomain=sandbox_subdomain).first()
            
            if not sandbox:
                print("ℹ️ AUDIT: Creando Condominio Sandbox...")
                sandbox = models.Condominium(
                    name="Condominio de Pruebas (Sandbox)",
                    legal_name="Entorno de Desarrollo CondoManager",
                    email=master_user.email,
                    ruc="9999999999001",
                    main_street="Calle de los Bugs",
                    cross_street="Avenida de las Soluciones",
                    city="Matrix",
                    country="Ecuador",
                    subdomain=sandbox_subdomain,
                    status='ACTIVO',
                    admin_user_id=master_user.id,
                    created_by=master_user.id,
                    has_documents_module=True,
                    has_billing_module=True,
                    has_requests_module=True
                )
                db.session.add(sandbox)
                
                # También la config visual
                if not db.session.get(models.CondominiumConfig, sandbox_subdomain):
                    viz_config = models.CondominiumConfig(
                        tenant=sandbox_subdomain, 
                        commercial_name="Sandbox Labs", 
                        primary_color="#6f42c1"
                    )
                    db.session.add(viz_config)
            
            # Asignar Master al Sandbox si no tiene tenant o si es el por defecto
            if master_user.tenant is None or master_user.tenant == 'puntablanca':
                print(f"🔄 AUDIT: Asignando MASTER al condominio '{sandbox_subdomain}'...")
                master_user.tenant = sandbox_subdomain
                db.session.add(master_user)

        db.session.commit()
        print("✅ AUDIT: db.session.commit() ejecutado. Datos iniciales guardados en la DB.")
        print("✅✅✅ Script de siembra de datos iniciales finalizado con ÉXITO.")

if __name__ == '__main__':
    seed_initial_data()