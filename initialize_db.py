def initialize_database():
    # Paso 1: Importar solo lo absolutamente necesario para crear la app
    print("AUDIT: Iniciando script initialize_db.py")
    from app import create_app
    
    app = create_app()
    print("AUDIT: Instancia de Flask creada.")
    
    # Paso 2: Trabajar dentro del contexto de la aplicación
    with app.app_context():
        print("AUDIT: Entrando en el contexto de la aplicación.")
        # Importar extensiones y modelos DESPUÉS de tener un contexto
        from app.extensions import db
        from app import models
        import os
        import hashlib
        import sys
        
        try:
            print("AUDIT: Intentando crear tablas...")
            db.create_all()
            print("✅ Tablas creadas exitosamente.")
            
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
                db.session.commit()
                print(f"✅ USUARIO MAESTRO CREADO: {master_email}")
            else:
                print("✅ Usuario maestro ya existe.")
                
            # Crear configuración de tenant por defecto
            default_tenant = 'puntablanca'
            if not models.CondominiumConfig.query.get(default_tenant):
                print(f"AUDIT: Creando configuración para el tenant por defecto '{default_tenant}'...")
                config = models.CondominiumConfig(tenant=default_tenant, commercial_name='Punta Blanca')
                db.session.add(config)
                db.session.commit()
                print(f"✅ Configuración de tenant por defecto creada para '{default_tenant}'.")
            else:
                print(f"✅ Configuración para '{default_tenant}' ya existe.")
                
            print("AUDIT: Script de inicialización finalizado con éxito.")
            
        except Exception as e:
            print(f"❌ ERROR CRÍTICO DURANTE LA INICIALIZACIÓN DE LA DB: {e}")
            sys.exit(1) # Detiene el despliegue si hay un error

if __name__ == '__main__':
    initialize_database()
