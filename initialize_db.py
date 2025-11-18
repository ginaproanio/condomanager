from app import create_app
from app.extensions import db
from app import models

def initialize_database():
    app = create_app()
    with app.app_context():
        try:
            print("Creando tablas...")
            db.create_all() # Esto crea todas las tablas definidas en app/models.py
            print("Tablas creadas exitosamente")

            # Ahora, vamos a crear el usuario maestro si no existe.
            import os
            import hashlib

            master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
            if not models.User.query.filter_by(email=master_email).first():
                master_password = os.environ.get('MASTER_PASSWORD', 'Master2025!')
                pwd_hash = hashlib.sha256(master_password.encode()).hexdigest()

                master = models.User(
                    email=master_email,
                    name='Administrador Maestro',
                    password_hash=pwd_hash,
                    tenant=None,  # El MASTER no pertenece a ningún tenant.
                    role='MASTER',
                    status='active'
                )
                db.session.add(master)
                db.session.commit()
                print(f"✅ USUARIO MAESTRO CREADO: {master_email}")
            else:
                print("✅ Usuario maestro ya existe, no se realizaron cambios.")

            # Crear configuración inicial para el tenant 'puntablanca' si no existe.
            # Esto es crucial para que la primera carga de la app no falle.
            default_tenant_name = 'puntablanca'
            if not models.CondominiumConfig.query.get(default_tenant_name):
                default_config = models.CondominiumConfig(
                    tenant=default_tenant_name,
                    primary_color='#2c5aa0',
                    commercial_name='Punta Blanca'
                )
                db.session.add(default_config)
                db.session.commit()
                print(f"✅ Configuración de tenant por defecto creada para: {default_tenant_name}")

        except Exception as e:
            print(f"❌ ERROR CRÍTICO EN INICIALIZACIÓN DE DB: {e}")
            # Forzar que el proceso falle si hay un error para que el despliegue se detenga.
            import sys
            sys.exit(1)

if __name__ == '__main__':
    initialize_database()
