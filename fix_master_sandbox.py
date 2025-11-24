from app import create_app, db
from app.models import User, Condominium, CondominiumConfig
from datetime import datetime

app = create_app()

with app.app_context():
    print("--- INICIO SCRIPT: FIX MASTER SANDBOX ---")
    
    # 1. Encontrar al Master
    master = User.query.filter_by(role='MASTER').first()
    if not master:
        print("❌ ERROR CRÍTICO: No se encontró ningún usuario con rol MASTER.")
        exit(1)
    
    print(f"✅ Usuario MASTER encontrado: {master.name} ({master.email})")
    
    # 2. Buscar o Crear Condominio Sandbox
    sandbox_subdomain = 'sandbox'
    sandbox = Condominium.query.filter_by(subdomain=sandbox_subdomain).first()
    
    if not sandbox:
        print("ℹ️ Condominio 'sandbox' no existe. Creándolo...")
        sandbox = Condominium(
            name="Condominio de Pruebas (Sandbox)",
            legal_name="Entorno de Desarrollo CondoManager",
            email=master.email,
            ruc="9999999999001",
            main_street="Calle de los Bugs",
            cross_street="Avenida de las Soluciones",
            city="Matrix",
            country="Ecuador",
            subdomain=sandbox_subdomain,
            status='ACTIVO',
            admin_user_id=master.id,
            created_by=master.id,
            has_documents_module=True, # Activar todos los módulos para pruebas
            has_billing_module=True,
            has_requests_module=True,
            payment_provider='PAYPHONE',
            payment_config={
                "token": "TOKEN_DE_PRUEBA_AQUI", # Placeholder
                "id": "ID_DE_PRUEBA_AQUI"
            }
        )
        db.session.add(sandbox)
        db.session.flush() # Para obtener el ID
        
        # Crear config visual
        config_visual = CondominiumConfig(
            tenant=sandbox_subdomain,
            commercial_name="Sandbox Labs",
            primary_color="#6f42c1" # Un color morado distintivo para saber que es pruebas
        )
        db.session.add(config_visual)
        print("✅ Condominio Sandbox creado exitosamente.")
    else:
        print(f"✅ Condominio Sandbox ya existe (ID: {sandbox.id}).")
        # Asegurar que master sea el admin
        sandbox.admin_user_id = master.id
        sandbox.has_documents_module = True # Asegurar módulos activos
        
    # 3. Asignar Master al Sandbox
    print(f"🔄 Actualizando tenant del Master de '{master.tenant}' a '{sandbox_subdomain}'...")
    master.tenant = sandbox_subdomain
    
    # Opcional: Asignarlo también a una unidad ficticia si fuera necesario para pruebas de residente
    # Pero por ahora el tenant es lo crítico para evitar el Error 500.
    
    try:
        db.session.commit()
        print("✅✅✅ ÉXITO: El usuario MASTER ahora vive en el condominio 'sandbox'.")
        print("NOTA: Ahora al crear documentos o cobrar, se usarán los datos de este condominio.")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error al guardar cambios en DB: {e}")

