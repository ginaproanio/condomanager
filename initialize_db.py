def initialize_database():
    print("AUDIT: Iniciando script initialize_db.py")
    
    try:
        # Importar la fábrica de la aplicación
        from app import create_app
        app = create_app()
        print("AUDIT: Instancia de Flask creada exitosamente.")

        # Trabajar dentro del contexto de la aplicación para acceder a la DB
        with app.app_context():
            print("AUDIT: Entrando en el contexto de la aplicación.")
            from app.extensions import db
            from app import models
            import os
            import hashlib

            # print("AUDIT: **MODO DEPURACIÓN DESACTIVADO** Las tablas ya no se eliminarán en cada despliegue.")
            # db.drop_all()
            # print("✅ AUDIT: Todas las tablas eliminadas.")

            print("AUDIT: Creando todas las tablas desde cero (db.create_all())...")
            db.create_all()
            print("✅ AUDIT: db.create_all() ejecutado.")

            # Crear usuario maestro
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

            # Crear configuración de tenant por defecto
            default_tenant = 'puntablanca' # Asegúrate de que este sea el tenant que esperas
            if not db.session.get(models.CondominiumConfig, default_tenant): # Usar db.session.get()
                print(f"AUDIT: Creando configuración para el tenant por defecto '{default_tenant}'...")
                config = models.CondominiumConfig(tenant=default_tenant, commercial_name='Punta Blanca')
                db.session.add(config)
                print("AUDIT: Configuración de tenant añadida a la sesión.")
            else:
                print(f"✅ AUDIT: Configuración para '{default_tenant}' ya existe.")

            db.session.commit()
            print("✅ AUDIT: db.session.commit() ejecutado. Cambios guardados en la DB.")
            print("✅✅✅ Script de inicialización finalizado con ÉXITO.")

    except Exception as e:
        import traceback
        print(f"❌ ERROR CRÍTICO EN initialize_db.py: {e}")
        print("--- TRACEBACK COMPLETO ---")
        traceback.print_exc()
        print("--------------------------")
        import sys
        sys.exit(1) # Detiene el despliegue si hay un error

if __name__ == '__main__':
    initialize_database()
