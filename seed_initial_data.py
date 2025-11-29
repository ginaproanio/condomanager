import os
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
from app import create_app
from app.extensions import db
from app import models

def seed_initial_data():
    """
    Siembra datos iniciales en la base de datos para un entorno de desarrollo completo.
    Incluye: Master, Sandbox, Condominio de Prueba (Algarrobos), Unidades, Residentes, Pagos y Documentos.
    """
    app = create_app()
    with app.app_context():
        print("AUDIT: Iniciando script de siembra de datos masiva...")

        # ==========================================
        # 0. CATÁLOGO DE MÓDULOS (GLOBAL)
        # ==========================================
        print("📦 Verificando Catálogo de Módulos...")
        modules_data = [
            {
                "code": "documents",
                "name": "Firmas & Comunicados",
                "description": "Gestión de documentos, firmas electrónicas y comunicados oficiales.",
                "base_price": 0.00,
                "billing_cycle": "monthly",
                "status": "ACTIVE"
            },
            {
                "code": "collections",
                "name": "Gestión de Recaudación (Cobranza)",
                "description": "Pasarela de pagos (PayPhone) y conciliación de transferencias.",
                "base_price": 25.00,
                "billing_cycle": "monthly",
                "status": "ACTIVE"
            },
            {
                "code": "accounting",
                "name": "Contabilidad Condominial",
                "description": "Asientos contables, balances y reportes financieros formales.",
                "base_price": 30.00,
                "billing_cycle": "monthly",
                "status": "COMING_SOON"
            },
            {
                "code": "petty_cash",
                "name": "Caja Chica",
                "description": "Gestión de gastos menores y reposición de fondos.",
                "base_price": 5.00,
                "billing_cycle": "monthly",
                "status": "COMING_SOON"
            },
            {
                "code": "requests",
                "name": "Gestión de Requerimientos",
                "description": "Sistema de tickets para mantenimiento, quejas y sugerencias.",
                "base_price": 15.00,
                "billing_cycle": "monthly",
                "status": "COMING_SOON"
            },
            {
                "code": "communications",
                "name": "Comunicaciones Masivas",
                "description": "Envíos masivos por WhatsApp (Gateway/API) y notificaciones.",
                "base_price": 10.00,
                "billing_cycle": "monthly",
                "status": "ACTIVE"
            },
            {
                "code": "access_control",
                "name": "Control de Accesos y Visitas",
                "description": "Pre-registro de visitas y control de garita (IoT Ready).",
                "base_price": 20.00,
                "billing_cycle": "monthly",
                "status": "COMING_SOON"
            },
            {
                "code": "marketplace",
                "name": "Marketplace Inmobiliario",
                "description": "Publicación de propiedades en venta/arriendo por propietarios.",
                "base_price": 10.00,
                "billing_cycle": "monthly",
                "status": "COMING_SOON"
            },
            {
                "code": "procurement",
                "name": "Club de Compras (B2B)",
                "description": "Compra centralizada de suministros con descuentos mayoristas.",
                "base_price": 0.00,
                "billing_cycle": "monthly",
                "status": "COMING_SOON"
            },
            {
                "code": "ad_server",
                "name": "Red Publicitaria Local",
                "description": "Monetización mediante anuncios locales en el dashboard.",
                "base_price": 0.00,
                "billing_cycle": "monthly",
                "status": "COMING_SOON"
            }
        ]

        for mod_data in modules_data:
            existing_mod = models.Module.query.filter_by(code=mod_data["code"]).first()
            if not existing_mod:
                print(f"   ➕ Creando módulo: {mod_data['name']}")
                new_mod = models.Module(
                    code=mod_data["code"],
                    name=mod_data["name"],
                    description=mod_data["description"],
                    base_price=mod_data["base_price"],
                    billing_cycle=mod_data["billing_cycle"],
                    status=mod_data["status"]
                )
                db.session.add(new_mod)
            else:
                # Opcional: Actualizar datos si ya existe para mantener consistencia
                existing_mod.name = mod_data["name"]
                existing_mod.description = mod_data["description"]
                existing_mod.status = mod_data["status"]
                db.session.add(existing_mod)
        
        db.session.commit() # Guardar módulos antes de seguir

        # ==========================================
        # 1. USUARIO MAESTRO (SUPERADMIN)
        # ==========================================
        master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
        master_password = os.environ.get('MASTER_PASSWORD', 'Master2025!')
        master = models.User.query.filter_by(email=master_email).first()
        
        if not master:
            print(f"🌱 Creando usuario MASTER: {master_email}...")
            master = models.User(
                # --- DATOS ENRIQUECIDOS ---
                first_name='Gina',
                last_name='Proaño',
                email=master_email, 
                password_hash=generate_password_hash(master_password),
                role='MASTER', 
                status='active',
                cedula='1700000000',
                cellphone='0999999999',
                city='Quito',
                country='Ecuador',
                birth_date=datetime.strptime('1990-01-01', '%Y-%m-%d').date(),
                tenant='sandbox', # Asignado directamente al sandbox
                email_verified=True
            )
            db.session.add(master)
            db.session.flush() # Para tener ID
        else:
            # FIX DEFINITIVO: Forzar la actualización del hash si el master ya existe.
            print(f"✅ Master ya existe. Forzando actualización de contraseña a formato seguro para {master_email}...")
            master.password_hash = generate_password_hash(master_password)
            master.status = 'active' # Asegurar que esté activo
            master.role = 'MASTER'   # Asegurar que sea MASTER
            db.session.add(master)

        # ==========================================
        # 2. CONDOMINIO SANDBOX (Entorno del Master)
        # ==========================================
        sandbox_subdomain = 'sandbox'
        sandbox = models.Condominium.query.filter_by(subdomain=sandbox_subdomain).first()
        
        if not sandbox:
            print(f"🌱 Creando Condominio Sandbox ({sandbox_subdomain})...")
            sandbox = models.Condominium(
                name="Condominio de Pruebas (Sandbox)",
                legal_name="Entorno de Desarrollo CondoManager",
                email="dev@condomanager.com",
                ruc="9999999999001",
                main_street="Calle de los Bugs",
                cross_street="Avenida de las Soluciones",
                city="Matrix",
                country="Ecuador",
                subdomain=sandbox_subdomain,
                status='ACTIVO',
                environment='internal', # ARQUITECTURA CORRECTA: Tenant interno
                is_demo=False,
                is_internal=True, # Backward compatibility por ahora
                admin_user_id=master.id,
                created_by=master.id,
                has_documents_module=True,
                has_billing_module=True,
                has_requests_module=True,
                payment_provider='PAYPHONE',
                whatsapp_provider='GATEWAY_QR'
            )
            db.session.add(sandbox)
            
            # Configuración Visual Sandbox
            if not db.session.get(models.CondominiumConfig, sandbox_subdomain):
                viz_config = models.CondominiumConfig(
                    tenant=sandbox_subdomain, 
                    commercial_name="Sandbox Labs", 
                    primary_color="#6f42c1" # Morado Developer
                )
                db.session.add(viz_config)
            
            # Configuración de Pagos Global (SaaS) para el Master
            sandbox.payment_config = {
                "payphone_global": {
                    "app_id": "APP_SAAS_TEST",
                    "token": "TOK_SAAS_TEST"
                }
            }
            db.session.add(sandbox)
        
        # Asegurar que el Master apunta al Sandbox
        if master.tenant != sandbox_subdomain:
            master.tenant = sandbox_subdomain
            db.session.add(master)
            
        # ==========================================
        # 2.5 CONDOMINIO PUNTA BLANCA (Cliente Real/Ejemplo)
        # ==========================================
        puntablanca_subdomain = 'puntablanca'
        pb_config = db.session.get(models.CondominiumConfig, puntablanca_subdomain)
        if pb_config:
            # Si existe la config, aseguramos que apunte al logo si existe
            logo_path = 'app/static/uploads/logos/puntablanca.png'
            if os.path.exists(logo_path):
                 print(f"ℹ️ Encontrado logo para {puntablanca_subdomain}, actualizando URL...")
                 pb_config.logo_url = 'uploads/logos/puntablanca.png'
                 db.session.add(pb_config)
        else:
             # Si no existe la config pero existe el condominio (caso legacy), la creamos
             pb_condo = models.Condominium.query.filter_by(subdomain=puntablanca_subdomain).first()
             if pb_condo:
                 print(f"🌱 Creando Config Visual para {puntablanca_subdomain}...")
                 logo_url = None
                 if os.path.exists('app/static/uploads/logos/puntablanca.png'):
                     logo_url = 'uploads/logos/puntablanca.png'
                     
                 pb_config = models.CondominiumConfig(
                    tenant=puntablanca_subdomain, 
                    commercial_name="Punta Blanca Ocean Club", 
                    primary_color="#007bff",
                    logo_url=logo_url
                )
                 db.session.add(pb_config)

        # ==========================================
        # 3. CONDOMINIO DE PRUEBA REAL (Algarrobos)
        # ==========================================
        demo_subdomain = 'algarrobos'
        admin_email = "admin@algarrobos.com" # Definir aquí para usarlo abajo
        algarrobos = models.Condominium.query.filter_by(subdomain=demo_subdomain).first()
        
        if not algarrobos:
            print(f"🌱 Creando Condominio Realista ({demo_subdomain})...")
            algarrobos = models.Condominium(
                name="Conjunto Residencial Los Algarrobos",
                legal_name="Comité Pro-Mejoras Algarrobos",
                email=admin_email,
                ruc="1790000000001",
                main_street="Av. Interoceánica Km 14",
                house_number="Lote 2",
                cross_street="Calle Los Ceibos",
                city="Cumbayá",
                country="Ecuador",
                subdomain=demo_subdomain,
                document_code_prefix="ALGA", # NUEVO: Prefijo para documentos
                status='ACTIVO',
                environment='demo', # DEMO PÚBLICA (Datos fake)
                is_demo=True,
                created_by=master.id,
                has_documents_module=True, # PREMIUM ACTIVADO
                has_billing_module=True,
                payment_config={"token": "TOK_TEST_123", "id": "ID_TEST_123"}, # Mock PayPhone
                whatsapp_provider='META_API'
            )
            db.session.add(algarrobos)
        
        # --- LÓGICA DE ACTUALIZACIÓN FORZOSA PARA ADMIN (CORREGIDA) ---
        admin_email = "admin@algarrobos.com"
        admin_user = models.User.query.filter_by(email=admin_email).first()
        if not admin_user:
            print(f"   🌱 Creando usuario ADMIN para {demo_subdomain}...")
            admin_user = models.User(
                first_name='Michelle', last_name='Tobar', email=admin_email, role='ADMIN',
                cedula='1700000001', cellphone='0991234567', city='Cumbayá', country='Ecuador',
                birth_date=datetime.strptime('1992-05-10', '%Y-%m-%d').date()
            )
            db.session.add(admin_user)
        
        print(f"   ✅ Asegurando datos y contraseña segura para ADMIN {admin_email}...")
        admin_user.password_hash = generate_password_hash('Admin123!')
        admin_user.status = 'active'
        admin_user.tenant = demo_subdomain
        admin_user.email_verified = True
        
        # ASOCIACIÓN CRÍTICA: Asegurar que el admin y el condominio estén vinculados
        if algarrobos.admin_user_id != admin_user.id:
            algarrobos.admin_user_id = admin_user.id
        if admin_user.condominium_id != algarrobos.id:
            admin_user.condominium_id = algarrobos.id

        db.session.add_all([admin_user, algarrobos])
        
        db.session.flush() # Hacemos flush para que algarrobos.id esté disponible

        # El resto de la siembra de datos (unidades, residentes, etc.) solo debe
        # ejecutarse si el condominio es nuevo, para no duplicar datos.
        if not algarrobos.id:
            # Config Visual Algarrobos
            if not db.session.get(models.CondominiumConfig, demo_subdomain):
                viz_config = models.CondominiumConfig(
                    tenant=demo_subdomain, 
                    commercial_name="Los Algarrobos", 
                    primary_color="#28a745" # Verde Naturaleza
                )
                db.session.add(viz_config)

            # ------------------------------------------
            # 3.0 CONFIGURACIÓN DE MÓDULOS (Nueva Lógica)
            # ------------------------------------------
            # Simular que Algarrobos tiene contratado el módulo de Comunicaciones Masivas
            # usando la nueva tabla CondominiumModule
            print("   ... Configurando Módulos Personalizados...")
            comms_module = models.Module.query.filter_by(code='communications').first()
            if comms_module:
                condo_module_config = models.CondominiumModule(
                    condominium_id=algarrobos.id,
                    module_id=comms_module.id,
                    status='ACTIVE',
                    price_override=12.50, # Precio personalizado (base era 10.00)
                    pricing_type='per_module'
                )
                db.session.add(condo_module_config)

            # ------------------------------------------
            # 3.1 UNIDADES Y RESIDENTES
            # ------------------------------------------
            print("   ... Generando Unidades y Residentes...")
            
            # Lista de datos fake para residentes
            residents_data = [
                ("Juan", "Perez", "101", "Casa"),
                ("Maria", "Lopez", "102", "Casa"),
                ("Carlos", "Andrade", "201", "Departamento"), # Tesorero
                ("Ana", "Torres", "202", "Departamento"), # Presidente
                ("Luis", "Gomez", "A1", "Local Comercial")
            ]

            users_objects = []

            # --- LÓGICA DE ACTUALIZACIÓN FORZOSA PARA RESIDENTES ---
            for idx, (nombre, apellido, _, _) in enumerate(residents_data):
                email = f"{nombre.lower()}.{apellido.lower()}@example.com"
                residente = models.User.query.filter_by(email=email).first()
                if not residente:
                    print(f"      🌱 Creando residente: {email}...")
                    residente = models.User(role='USER', tenant=demo_subdomain)
                    db.session.add(residente)
                
                # Forzar siempre los datos correctos
                print(f"      ✅ Asegurando datos y contraseña para residente {email}...")
                residente.password_hash=generate_password_hash('Vecino123!')
                residente.status='active'
                residente.email_verified=True
                residente.cedula=f'17000000{idx+2}'
                residente.email=email
                residente.first_name=nombre
                residente.last_name=apellido
                residente.cellphone=f'099000000{idx}'
                db.session.add(residente)
                users_objects.append(residente)

            # Asignar unidades (esto puede hacerse en un bucle separado o integrado)
            for idx, (residente, (_, _, num, tipo)) in enumerate(zip(users_objects, residents_data)):
                if not residente.unit:
                    unit = models.Unit.query.filter_by(property_number=num, condominium_id=algarrobos.id).first()
                    if not unit:
                        unit = models.Unit(
                            property_number=num, name=f"{tipo} {num}", property_type=tipo,
                            condominium_id=algarrobos.id, created_by=admin_user.id,
                            area_m2=120.0, bedrooms=3, bathrooms=2
                        )
                        db.session.add(unit)
                        db.session.flush()
                    residente.unit_id = unit.id
                    db.session.add(residente)

            # ------------------------------------------
            # 3.1.5 USUARIOS PENDIENTES Y RECHAZADOS (Para pruebas del Master)
            # ------------------------------------------
            print("   ... Generando Usuarios Pendientes/Rechazados...")
            
            pending_user = models.User.query.filter_by(email='pendiente@example.com').first()
            if not pending_user:
                pending_user = models.User(
                    cedula=f'17000000{idx+2}',
                    email='pendiente@example.com',
                    first_name='Pedro',
                    last_name='Pendiente',
                    password_hash=generate_password_hash('123456'),
                    role='USER',
                    status='pending',
                    tenant=demo_subdomain,
                    cellphone='0999999999'
                )
                db.session.add(pending_user)
            
            rejected_user = models.User.query.filter_by(email='rechazado@example.com').first()
            if not rejected_user:
                rejected_user = models.User(
                    cedula='1744444444',
                    email='rechazado@example.com',
                    first_name='Roberto',
                    last_name='Rechazado',
                    password_hash=generate_password_hash('123456'),
                    role='USER',
                    status='rejected',
                    tenant=demo_subdomain,
                    cellphone='0988888888'
                )
                db.session.add(rejected_user)

            # ------------------------------------------
            # 3.2 DIRECTIVA (Roles Especiales)
            # ------------------------------------------
            print("   ... Asignando Directiva...")
            # Carlos (Tesorero)
            tesorero_role = models.UserSpecialRole(
                user_id=users_objects[2].id,
                condominium_id=algarrobos.id,
                role='TESORERO',
                assigned_by=admin_user.id,
                start_date=datetime.utcnow().date(),
                is_active=True
            )
            # Ana (Presidente)
            presidente_role = models.UserSpecialRole(
                user_id=users_objects[3].id,
                condominium_id=algarrobos.id,
                role='PRESIDENTE',
                assigned_by=admin_user.id,
                start_date=datetime.utcnow().date(),
                is_active=True
            )
            db.session.add_all([tesorero_role, presidente_role])

            # ------------------------------------------
            # 3.3 DOCUMENTOS
            # ------------------------------------------
            print("   ... Creando Documentos de Prueba...")
            doc1 = models.Document(
                title="Acta de Asamblea General 2024",
                content="<p>Se aprueba el presupuesto...</p>",
                created_by_id=admin_user.id,
                condominium_id=algarrobos.id,
                status='signed',
                created_at=datetime.utcnow() - timedelta(days=5)
            )
            
            doc2 = models.Document(
                title="Comunicado: Mantenimiento Piscina",
                content="<p>La piscina estará cerrada por mantenimiento...</p>",
                created_by_id=admin_user.id,
                condominium_id=algarrobos.id,
                status='sent',
                created_at=datetime.utcnow()
            )
            db.session.add_all([doc1, doc2])

            # ------------------------------------------
            # 3.4 PAGOS (Historial Financiero)
            # ------------------------------------------
            print("   ... Registrando Pagos...")
            # Pago Aprobado (Tarjeta)
            pago1 = models.Payment(
                amount=85.00,
                amount_with_tax=85.00,
                description="Alícuota Enero - Casa 101",
                status='APPROVED',
                payment_method='PAYPHONE',
                payphone_transaction_id='mock_tx_1',
                user_id=users_objects[0].id,
                unit_id=users_objects[0].unit_id,
                condominium_id=algarrobos.id,
                created_at=datetime.utcnow() - timedelta(days=10)
            )
            
            # Pago Pendiente (Transferencia)
            pago2 = models.Payment(
                amount=85.00,
                amount_with_tax=85.00,
                description="Transferencia Febrero - Casa 102",
                status='PENDING_REVIEW',
                payment_method='TRANSFER',
                proof_of_payment='comprobante_mock.pdf', # Archivo simulado
                user_id=users_objects[1].id,
                unit_id=users_objects[1].unit_id,
                condominium_id=algarrobos.id,
                created_at=datetime.utcnow() - timedelta(hours=2)
            )
            db.session.add_all([pago1, pago2])
        else:
            print(f"✅ Condominio '{demo_subdomain}' ya existe.")
