from app import create_app
from app.extensions import db
from app import models
import os
import hashlib

def initialize_database():
    app = create_app()
    with app.app_context():
        try:
            print("Creando tablas...")
            db.create_all()
            print("Tablas creadas exitosamente")

            master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
            if not models.User.query.filter_by(email=master_email).first():
                master_password = os.environ.get('MASTER_PASSWORD', 'Master2025!')
                pwd_hash = hashlib.sha256(master_password.encode()).hexdigest()

                master = models.User(
                    email=master_email,
                    name='Administrador Maestro',
                    phone='+593999999999',
                    city='Guayaquil',
                    country='Ecuador',
                    password_hash=pwd_hash,
                    tenant='master',
                    role='MASTER',
                    status='active'
                )
                db.session.add(master)
                db.session.commit()
                print(f"USUARIO MAESTRO CREADO: {master_email}")
            else:
                print("Usuario maestro ya existe")

            # Crear configuración inicial de 'condomanager' si no existe
            config_tenant_name = 'puntablanca' # Tenant principal para el arranque
            if not models.CondominiumConfig.query.get(config_tenant_name):
                config = models.CondominiumConfig(
                    tenant=config_tenant_name,
                    primary_color='#2c5aa0',
                    commercial_name=config_tenant_name.replace('_', ' ').title()
                )
                db.session.add(config)
                db.session.commit()
                print(f"Configuración de tenant por defecto creada para: {config_tenant_name}")
            else:
                print(f"Configuración para '{config_tenant_name}' ya existe")

        except Exception as e:
            print(f"Error en inicialización de la base de datos: {e}")
        finally:
            db.session.remove() # Asegurarse de cerrar la sesión después de la inicialización

if __name__ == '__main__':
    initialize_database()
