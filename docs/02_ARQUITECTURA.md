# Arquitectura del Sistema

## 1. Visión General
Sistema multi-condominio implementado inicialmente para "Punta Blanca", diseñado para escalar a múltiples instancias.

## 2. Stack Tecnológico Actual
### 2.1 Backend
- Python con Flask Framework
- SQLAlchemy ORM
- Flask-JWT-Extended para autenticación (con cookies HTTP-Only)
- Flask-Migrate para la gestión del esquema de la DB.
- Gunicorn para servir la aplicación en producción
- Flask-Limiter para protección contra ataques de fuerza bruta.
- structlog para logging estructurado en formato JSON.
- Flask-Caching para optimización de rendimiento.
- `hashlib` para hashing de contraseñas

### 2.2 Frontend
- Bootstrap 5 (CSS y JS)
- JavaScript vanilla (para lógica de autenticación, peticiones a la API y UI dinámica)
- TinyMCE (Editor de texto enriquecido para documentos)

### 2.3 Base de Datos
- PostgreSQL (en producción)
- SQLite (en desarrollo)

## 3. Estructura del Proyecto

```
/condomanager-saas/
├── app/
│   ├── __init__.py     # Inicialización de la aplicación Flask y registro de componentes.
│   ├── auth.py         # Funciones auxiliares de autenticación (ej. obtener usuario actual).
│   ├── decorators.py   # Decoradores de seguridad y roles (@module_required, @admin_required).
│   ├── extensions.py   # Instancia de SQLAlchemy (db) para evitar dependencias circulares.
│   ├── models.py       # Definición de todos los modelos de la base de datos.
│   ├── tenant.py       # Lógica para determinar el tenant (inquilino) de la solicitud.
│   ├── routes/         # Módulo que contiene todas las rutas (endpoints) de la aplicación.
│   │   ├── __init__.py # Inicializa y registra los blueprints de rutas.
│   │   ├── public_routes.py # Rutas públicas (home, registro, login, demos).
│   │   ├── user_routes.py   # Rutas para usuarios autenticados (dashboard, pagos).
│   │   ├── admin_routes.py  # Rutas para administradores de condominio (rol ADMIN).
│   │   │   # Endpoints clave:
│   │   │   # - /admin/condominio/<id>: Panel de gestión (Unidades, Usuarios, Directiva).
│   │   │   # - /admin/usuarios/roles_especiales: Asignación de roles de directiva.
│   │   │   # - /admin/condominio/<id>/finanzas: Panel de control financiero.
│   │   ├── master_routes.py # Rutas para el super-administrador (rol MASTER).
│   │   │   # Endpoints clave:
│   │   │   # - /master: Panel global con tarjetas de gestión.
│   │   │   # - /master/modules: Catálogo global de módulos.
│   │   ├── document_routes.py # Rutas para el módulo "Firmas & Comunicados" (Freemium).
│   │   ├── payment_routes.py  # Endpoints para callbacks y proceso de pagos.
│   │   ├── petty_cash_routes.py # Rutas para el módulo de Caja Chica.
│   │   ├── api_routes.py    # Endpoints de la API REST.
│   │   └── dev_routes.py    # Rutas para desarrollo y depuración.
│   ├── static/         # Archivos estáticos (CSS, JS, imágenes).
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── uploads/    # Almacenamiento de archivos subidos (comprobantes, certificados).
│   └── templates/      # Plantillas HTML (vistas).
│       ├── admin/
│       ├── auth/
│       ├── documents/  # Plantillas del módulo de documentos.
│       ├── master/
│       ├── public/     # Plantillas públicas (demo request).
│       ├── services/   # Vistas de servicios (pagos, reportes).
│       └── user/
├── Procfile            # Configuración de despliegue en Railway.
├── requirements.txt    # Dependencias de Python.
└── docs/               # Documentación del proyecto.
```

## 4. Estrategia Multi-Condominio (Multi-Tenancy)
La implementación actual utiliza una estrategia de **multi-tenancy de esquema compartido** (`shared-schema multi-tenancy`).

- **Base de Datos Única:** Todos los datos (usuarios, condominios, unidades) residen en una única base de datos.
- **Separación Lógica:** La separación de datos entre condominios se logra mediante un campo `tenant` (o `condominium_id` para usuarios/unidades) en los modelos de la base de datos.
- **Determinación del Tenant:** La lógica en `app/tenant.py` determina el inquilino (tenant) basándose en el subdominio de la solicitud HTTP. Por defecto, si no se encuentra un subdominio válido, se utiliza 'puntablanca'.
- **Queries Globales:** Las consultas para métricas de negocio globales (ej. reportes del MASTER) **deben** excluir explícitamente los entornos de prueba filtrando por `environment NOT IN ('sandbox', 'internal')`.

### ⚠️ NOTA CRÍTICA: Configuración de Multi-Tenancy en Testing vs. Producción

**Estado Actual (Testing en Railway / Localhost):**
Debido a que el entorno de pruebas en Railway no tiene configurados los subdominios wildcard (ej: `*.railway.app`), se ha implementado una **relajación intencional** en la lógica de detección de inquilinos (`app/tenant.py`).

*   **Comportamiento:** Si el host contiene `railway.app` o `localhost`, la función `get_tenant()` devuelve `None` (Modo Global) en lugar de forzar un tenant específico o fallar.
*   **Efecto:** Permite que usuarios de *cualquier* condominio (ej: `algarrobos`) se logueen desde la URL principal sin ser bloqueados por "Acceso desde subdominio incorrecto".

**🚨 PARA PRODUCCIÓN (Dominio Real):**
Cuando se despliegue en un dominio real (ej: `condomanager.com`) con certificados SSL Wildcard:
1.  Esta excepción en `app/tenant.py` **debe ser revisada**.
2.  La lógica actual `if 'localhost' in host or 'railway.app' in host` dejará de aplicar automáticamente (lo cual es correcto), activando la validación estricta de subdominios.
3.  **Verificación:** Asegurarse de que los usuarios finales accedan EXCLUSIVAMENTE a través de su subdominio asignado (ej: `algarrobos.condomanager.com`) para garantizar la seguridad del aislamiento de datos.
4.  **Infraestructura:** Los subdominios para tenants reales son gestionados vía Cloudflare. El entorno de desarrollo/pruebas se ejecuta en `localhost` o en la URL principal de Railway sin subdominio.

## 5. Modelos Principales (definidos en `app/models.py`)

### 5.1 User
- **Atributos Clave:** `id`, `cedula`, `email`, `first_name`, `last_name`, `password_hash`, `tenant`, `role`, `status`, `unit_id`.
- Roles base: `MASTER`, `ADMIN`, `USER`.
- **Atributos para Firma Electrónica:**
    - `has_electronic_signature`: Booleano que indica si el usuario ha configurado su certificado.
    - `signature_certificate`: Campo binario que almacena el certificado `.p12` o `.pfx`.
    - `signature_cert_password_hash`: Hash de la contraseña del certificado para su uso seguro.
- **Validación:** `email_verified`, `verification_token`.
- Relaciones: Un usuario puede ser administrador de `Condominium` o creador de `Unit`.

### 5.2 Condominium
- **Atributos:** `id`, `name`, `legal_name`, `email`, `ruc`, `main_street`, `cross_street`, `house_number`, `city`, `country`, `latitude`, `longitude`, `subdomain`, `status` (ACTIVO, DEMO, INACTIVO), `billing_day`, `grace_days`, `trial_start_date`, `trial_end_date`, `notes`, `admin_user_id`, `legal_representative_id`, `created_by`, `created_at`, `updated_at`.
- **Flags de Módulos:** `has_documents_module`, `has_billing_module`.
- **Configuración WhatsApp:** `whatsapp_provider` ('GATEWAY_QR' o 'META_API'), `whatsapp_config` (JSON).
- **Configuración Pagos:** `payment_provider` ('PAYPHONE'), `payment_config` (JSON).
- Relaciones: Contiene múltiples `Unit`s y `User`s (ADMINs asignados).

### 5.3 Unit
- **Atributos:** `id`, `property_tax_code`, `property_number`, `name`, `property_type`, `main_street`, `cross_street`, `house_number`, `address_reference`, `latitude`, `longitude`, `building`, `floor`, `sector`, `area_m2`, `area_construction_m2`, `bedrooms`, `bathrooms`, `parking_spaces`, `front_meters`, `depth_meters`, `topography`, `land_use`, `notes`, `condominium_id`, `created_by`, `status`, `created_at`, `updated_at`.
- Relaciones: Pertenece a un `Condominium`, puede tener `User`s de unidad asignados.

### 5.4 CondominioConfig (en `app/models.py`)
- **Atributos:** `tenant`, `primary_color`, `logo_url`, `commercial_name`, `created_at`.
- Propósito: Configuración de personalización para cada tenant.

### 5.5 Modelos de Negocio

#### 5.5.1 UserSpecialRole
- **Estado:** ✅ Implementado y en uso.
- **Propósito:** Asignar roles de directiva (Presidente, Tesorero, etc.) a usuarios dentro de un condominio.
- **Atributos:** `id`, `user_id`, `condominium_id`, `role`, `assigned_by`, `start_date`, `end_date`, `is_active`.
- **Gestión:** Se gestiona desde el Panel de Administrador (`admin_routes.py`), pestaña "Directiva".

#### 5.5.2 Módulo "Firmas & Comunicados"
- **Estado:** ✅ Implementado (Fase 1 y 4). Estrategia Freemium activa.
- **Propósito:** Gestionar el ciclo de vida completo de documentos oficiales.
- **Modelos Clave:**
    - **`Document`**: Entidad central. Almacena:
        - Contenido del documento (HTML desde el editor).
        - Estados: `draft`, `pending_signature`, `signed`, `sent`.
        - Rutas a los PDFs generados (`pdf_unsigned_path`, `pdf_signed_path`).
        - Configuración para recolección de firmas públicas (`collect_signatures_from_residents`, `public_signature_link`).
    - **`DocumentSignature`**: Registra firmas de usuarios del sistema (`MASTER`, `ADMIN`, Directiva).
    - **`ResidentSignature`**: Registra firmas públicas externas.
- **Control de Acceso:**
    - **Nivel Básico:** Accesible para todos (repositorio).
    - **Nivel Premium (Crear/Firmar):** Protegido por el decorador `@module_required`. Requiere que el condominio tenga el módulo contratado Y que el usuario sea ADMIN o Directiva.

#### 5.5.3 Arquitectura Escalable de Módulos
- **Estado:** ✅ Implementado (Catálogo Global).
- **Propósito:** Crear un sistema dinámico para añadir, activar y facturar módulos.
- **Modelos Clave:**
    - **`Module` (Catálogo de Módulos):**
        - **Propósito:** Tabla que contiene todos los módulos que la plataforma puede ofrecer.
        - **Atributos:** `id`, `code` (ej: 'documents'), `name`, `description`, `base_price`, `billing_cycle`, `status` ('ACTIVE', 'MAINTENANCE', 'ARCHIVED', 'COMING_SOON'), `pricing_type` ('per_module', 'per_user'), `maintenance_mode` (bool), `maintenance_end` (datetime), `maintenance_message` (string).
        - **Gestión:** El MASTER gestiona este catálogo desde `/master/modules`.
    - **`CondominiumModule` (Personalización por Condominio):**
        - **Propósito:** Tabla intermedia que permite personalizar las condiciones comerciales de un módulo para un condominio específico.
        - **Atributos:** `id`, `condominium_id`, `module_id`, `status` ('ACTIVE', 'INACTIVE', 'TRIAL'), `price_override` (float), `pricing_type` ('per_module', 'per_user'), `activated_at`, `trial_ends_at`.
        - **Lógica:** Permite "overrides" de precio y tipo de cobro sobre el catálogo global.
- **Lógica de Seguridad Global:** El decorador `@module_required` verifica primero el estado en `Module` (si está en mantenimiento) y luego la configuración específica en `CondominiumModule` (o los flags legacy `has_billing_module`).

#### 5.5.4 Módulo Comunicaciones (Híbrido)
- **Estado:** ✅ UI y Backend de Configuración listos.
- **Estrategia:** Multi-Driver (Gateway QR / Meta API).
- **Modelos:** Uso de campos JSON en `Condominium` para flexibilidad de credenciales.

#### 5.5.5 Módulo de Recaudación (Cobranza) - `collections`
- **Estado:** ✅ Implementado (Base de Pagos).
- **Propósito:** Recibir y conciliar dinero (PayPhone, Transferencias).
- **Detalle:** Ver `docs/11_MODULOS_FINANCIEROS.md`.

#### 5.5.6 Módulo de Caja Chica - `petty_cash`
- **Estado:** ✅ Implementado (Registro de Movimientos).
- **Propósito:** Gestión de gastos menores e ingresos operativos.
- **Modelo `PettyCashTransaction`**:
    - Atributos: `description`, `amount` (positivo/negativo), `transaction_date`, `category`, `receipt_url`, `created_by`.

#### 5.5.7 AuditLog (Propuesto)
- **Propósito:** Registrar acciones clave en el sistema para trazabilidad y seguridad.
- **Estado:** ❌ Faltante.

## 6. Seguridad
- **Autenticación:** JWT con cookies HTTP-Only (gestionado por Flask-JWT-Extended).
- **Autorización:** Verificación de roles y permisos en cada ruta protegida. Decoradores personalizados (`@master_required`, `@module_required`, `@condominium_admin_required`).
- **Hashing de Contraseñas:** SHA256.
- **Protección CSRF:** Implícita por diseño en cookies SameSite.
- **HTTPS:** Obligatorio en producción.

## 7. Próximas Funcionalidades y Mejoras
Esta sección documenta funcionalidades identificadas en las reglas de negocio (`07_REGLAS_NEGOCIO.md`) que no están completamente implementadas.

### 7.1 Implementación de Firma Electrónica Real
- **Objetivo:** Integrar librerías criptográficas (`endesive`) para firmar digitalmente los PDFs con certificados .p12 subidos por el usuario.
- **Estado:** 🚧 Parcial (Base de datos y carga de certificados listos).

### 7.2 Envíos Inteligentes
- **Objetivo:** Módulo de notificaciones masivas por WhatsApp/Email.
- **Estado:** 🚧 Parcial (Configuración lista, falta motor de envío).

### 7.3 Nuevos Módulos (IoT, Comercial y Financiero)
1.  **Control de Accesos (IoT)**: Ver `docs/10_MODULOS_FUTUROS.md`.
2.  **Marketplace Inmobiliario**: Ver `docs/10_MODULOS_FUTUROS.md`.
3.  **Ecosistema Financiero (Contabilidad, Procurement, AdServer)**: Ver `docs/11_MODULOS_FINANCIEROS.md`.

## 8. Consideraciones para Futuras Mejoras
- **Modularización:** La estructura actual es adecuada, pero a medida que el proyecto crezca, se puede evaluar una mayor modularización (ej. `app/api/v1/`, `app/core/`) para desacoplar componentes.
- **Refinamiento de Permisos:** Una vez implementados los roles especiales, se necesitará un sistema de permisos más granular que el basado solo en los roles base (`MASTER`, `ADMIN`, `USER`).
- **Testing:** Es crucial incrementar la cobertura de tests unitarios y de integración a medida que se añaden nuevas funcionalidades.
