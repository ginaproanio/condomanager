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
            master = models.User(
                email=master_email, name='Administrador Maestro', password_hash=pwd_hash,
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

        db.session.commit()
        print("✅ AUDIT: db.session.commit() ejecutado. Datos iniciales guardados en la DB.")
        print("✅✅✅ Script de siembra de datos iniciales finalizado con ÉXITO.")

if __name__ == '__main__':
    seed_initial_data()