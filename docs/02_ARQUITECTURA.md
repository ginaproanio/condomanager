# Arquitectura del Sistema

## 1. Visión General
Sistema multi-condominio implementado inicialmente para "Punta Blanca", diseñado para escalar a múltiples instancias.

## 2. Stack Tecnológico Actual
### 2.1 Backend
- Python con Flask Framework
- SQLAlchemy ORM
- Flask-JWT-Extended para autenticación (con cookies HTTP-Only)
- Flask-Migrate para la gestión y evolución del esquema de la base de datos.
- Gunicorn para servir la aplicación en producción
- `hashlib` para hashing de contraseñas

### 2.2 Frontend
- Bootstrap 5 (CSS y JS)
- JavaScript vanilla (para lógica de autenticación, peticiones a la API y UI dinámica)

### 2.3 Base de Datos
- PostgreSQL (en producción)
- SQLite (en desarrollo)

## 3. Estructura del Proyecto

```
/condomanager-saas/
├── app/
│   ├── __init__.py     # Inicialización de la aplicación Flask y registro de componentes.
│   ├── auth.py         # Funciones auxiliares de autenticación (ej. obtener usuario actual).
│   ├── extensions.py   # Instancia de SQLAlchemy (db) para evitar dependencias circulares.
│   ├── models.py       # Definición de todos los modelos de la base de datos.
│   ├── tenant.py       # Lógica para determinar el tenant (inquilino) de la solicitud.
│   ├── routes/         # Módulo que contiene todas las rutas (endpoints) de la aplicación.
│   │   ├── __init__.py # Inicializa y registra los blueprints de rutas.
│   │   ├── public_routes.py # Rutas públicas (home, registro, login).
│   │   ├── user_routes.py   # Rutas para usuarios autenticados (dashboard).
│   │   ├── admin_routes.py  # Rutas para administradores de condominio (rol ADMIN).
│   │   │   # Endpoints clave:
│   │   │   # - /admin (GET): Despachador (dispatcher) que redirige al panel correcto.
│   │   │   # - /admin/condominio/<id> (GET): Panel de gestión específico del condominio.
│   │   │   # - /aprobar/<id> (GET): Aprueba un usuario pendiente.
│   │   │   # - /rechazar/<id> (GET): Rechaza un usuario pendiente.
│   │   │   # - /admin/condominio/<id>/unidad/nueva (GET, POST): Formulario para crear unidad.
│   │   ├── master_routes.py # Rutas para el super-administrador (rol MASTER).
│   │   │   # Endpoints clave:
│   │   ├── document_routes.py # Rutas para el módulo "Firmas & Comunicados".
│   │   │   # - /master/condominios (GET, POST para importar)
│   │   │   # - /master/usuarios (GET, POST para crear/importar)
│   │   │   # - /master/supervise/<id> (GET) - Panel de supervisión de solo lectura.
│   │   │   # - /master/impersonate/admin/<id> (GET) - Acceso de emergencia (suplantación).
│   │   ├── api_routes.py    # Endpoints de la API REST.
│   │   └── dev_routes.py    # Rutas para desarrollo y depuración.
│   ├── static/         # Archivos estáticos (CSS, JS, imágenes).
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/      # Plantillas HTML (vistas).
│       ├── admin/
│       ├── auth/
│       ├── master/
│       ├── services/
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

## 5. Modelos Principales (definidos en `app/models.py`)

### 5.1 User
- **Atributos Clave:** `id`, `cedula`, `email`, `first_name`, `last_name`, `password_hash`, `tenant`, `role`, `status`, `unit_id`.
- Roles base: `MASTER`, `ADMIN`, `USER`.
- **Atributos para Firma Electrónica:**
    - `has_electronic_signature`: Booleano que indica si el usuario ha configurado su certificado.
    - `signature_certificate`: Campo binario que almacena el certificado `.p12` o `.pfx`.
    - `signature_cert_password_hash`: Hash de la contraseña del certificado para su uso seguro.
- Relaciones: Un usuario puede ser administrador de `Condominium` o creador de `Unit`.

### 5.2 Condominium
- **Atributos:** `id`, `name`, `legal_name`, `email`, `ruc`, `main_street`, `cross_street`, `house_number`, `city`, `country`, `latitude`, `longitude`, `subdomain`, `status`, `billing_day`, `grace_days`, `trial_start_date`, `trial_end_date`, `notes`, `admin_user_id`, `legal_representative_id`, `created_by`, `created_at`, `updated_at`.
- Relaciones: Contiene múltiples `Unit`s y `User`s (ADMINs asignados).

### 5.3 Unit
- **Atributos:** `id`, `property_tax_code`, `property_number`, `name`, `property_type`, `main_street`, `cross_street`, `house_number`, `address_reference`, `latitude`, `longitude`, `building`, `floor`, `sector`, `area_m2`, `area_construction_m2`, `bedrooms`, `bathrooms`, `parking_spaces`, `front_meters`, `depth_meters`, `topography`, `land_use`, `notes`, `condominium_id`, `created_by`, `status`, `created_at`, `updated_at`.
- Relaciones: Pertenece a un `Condominium`, puede tener `User`s de unidad asignados.

### 5.4 CondominioConfig (en `app/models.py`)
- **Atributos:** `tenant`, `primary_color`, `logo_url`, `commercial_name`, `created_at`.
- Propósito: Configuración de personalización para cada tenant.

### 5.5 Modelos Propuestos (No Implementados)
Para dar soporte a las reglas de negocio futuras, se proponen los siguientes modelos:

#### 5.5.1 UserSpecialRole
- **Estado:** 🚧 Implementado (Modelo de datos). Lógica de negocio pendiente.
- **Propósito:** Asignar roles temporales y específicos (Presidente, Tesorero, etc.) a usuarios dentro de un condominio.
- **Atributos Implementados:**
    - `id`: Clave primaria.
    - `user_id`: Foreign Key a `User`.
    - `condominium_id`: Foreign Key a `Condominium`.
    - `role`: String (ej. "PRESIDENT", "TREASURER").
    - `assigned_by`: Foreign Key al `User` que asigna el rol.
    - `start_date`: Fecha de inicio de vigencia del rol.
    - `end_date`: Fecha de fin de vigencia.
    - `is_active`: Booleano para indicar si el rol está activo.
    - `created_at`: Timestamp de creación.

#### 5.5.2 Módulo "Firmas & Comunicados"
- **Estado:** ✅ Implementado.
- **Propósito:** Gestionar el ciclo de vida completo de documentos oficiales.
- **Modelos Clave:**
    - **`Document`**: Entidad central. Almacena:
        - Contenido del documento (HTML desde el editor).
        - Estados: `draft`, `pending_signature`, `signed`, `sent`.
        - Rutas a los PDFs generados (`pdf_unsigned_path`, `pdf_signed_path`).
        - Configuración para recolección de firmas públicas (`collect_signatures_from_residents`, `public_signature_link`).
    - **`DocumentSignature`**: Registra cada firma realizada por un usuario del sistema (`MASTER`, `ADMIN`, etc.). Almacena:
        - El `user_id` del firmante.
        - El tipo de firma: `physical` o `electronic`.
        - Timestamp e IP de la firma.
    - **`ResidentSignature`**: Almacena las firmas recolectadas a través de un enlace público para peticiones (ej. al municipio). Registra `full_name`, `cedula`, `phone` y está desvinculado de los usuarios del sistema.
- **Control de Acceso:**
    - **Nivel Condominio (Implementación Actual):** Protegido por el flag booleano `has_documents_module` en el modelo `Condominium`.
    - **Nivel Usuario:** El decorador `@module_required('documents')` centraliza la lógica de permisos, asegurando que solo usuarios autorizados (`MASTER`, `ADMIN`, `UserSpecialRole`) de un condominio con el módulo activo puedan acceder.

#### 5.5.3 Arquitectura Escalable de Módulos (Visión a Futuro)
- **Estado:** 🏛️ **Diseño Arquitectónico.** Esta es la evolución para soportar N módulos.
- **Propósito:** Crear un sistema dinámico para añadir, activar y facturar módulos.
- **Modelos Clave:**
    - **`Module` (Catálogo de Módulos):**
        - **Propósito:** Tabla que contiene todos los módulos que la plataforma puede ofrecer.
        - **Atributos:** `id`, `code` (ej: 'documents'), `name`, `description`, `base_price`, `billing_cycle`, `status` ('ACTIVE', 'MAINTENANCE', 'ARCHIVED', 'COMING_SOON').
    - **`CondominiumModuleActivation` (Activaciones por Condominio):**
        - **Propósito:** Tabla que registra qué condominio tiene qué módulo activado, cuándo y a qué precio. Es el historial de contrataciones.
        - **Atributos:** `id`, `condominium_id` (FK), `module_id` (FK), `activation_date`, `deactivation_date`, `price_at_activation`, `status` ('active', 'inactive', 'trial').
    - **`ModuleActivationHistory` (Historial de Estados):**
        - **Propósito:** Registra cada cambio de estado de una activación de módulo, especialmente para mantenimientos específicos.
        - **Atributos:** `id`, `activation_id` (FK a `CondominiumModuleActivation`), `status` ('maintenance_start', 'maintenance_end', 'reactivated'), `timestamp`, `notes` (ej: "Reparación de datos de facturas"), `changed_by_id` (FK a `User`, para saber qué `MASTER` hizo el cambio).
- **Lógica de Negocio a Futuro:**
    1.  **Crear un Módulo Nuevo:** Como desarrollador, solo se añade una nueva fila a la tabla `Module`. No se modifica el modelo `Condominium`.
    2.  **Activar un Módulo:** El `MASTER`, desde la interfaz de edición de un condominio, selecciona un módulo del catálogo. El sistema crea un nuevo registro en `CondominiumModuleActivation`.
    3.  **Verificar Permiso:** El decorador `@module_required` se modifica para que revise dos cosas:
        a. Que el estado global del módulo en `Module` no sea `MAINTENANCE`.
        b. Que exista un registro `active` en `CondominiumModuleActivation` para ese condominio y módulo.
    4.  **Facturación:** Un proceso mensual/anual puede leer la tabla `CondominiumModuleActivation` para generar facturas. La tabla `ModuleActivationHistory` puede usarse para calcular créditos o descuentos por tiempo de inactividad.

#### 5.5.2 AuditLog
- **Propósito:** Registrar acciones clave en el sistema para trazabilidad y seguridad.
- **Atributos Sugeridos:**
    - `id`: Clave primaria.
    - `user_id`: Foreign Key al `User` que realiza la acción.
    - `tenant`: El tenant (`subdomain`) donde ocurrió la acción.
    - `action`: String describiendo la acción (ej. "USER_LOGIN", "CREATE_CONDOMINIUM").
    - `details`: Campo de texto (JSON o similar) con detalles relevantes.
    - `timestamp`: Fecha y hora de la acción.

## 6. Seguridad
- **Autenticación:** JWT con cookies HTTP-Only (gestionado por Flask-JWT-Extended).
- **Autorización:** Verificación de roles y permisos en cada ruta protegida.
- **Hashing de Contraseñas:** SHA256.
- HTTPS obligatorio en producción.

## 7. Próximas Funcionalidades y Mejoras
Esta sección documenta funcionalidades identificadas en las reglas de negocio (`07_REGLAS_NEGOCIO.md`) que no están completamente implementadas.

### 7.1 Implementación de Roles Especiales
- **Objetivo:** Implementar el modelo `UserSpecialRole` (ver 5.5.1) y la lógica de negocio para que los `ADMIN` puedan asignar y gestionar la directiva del condominio con períodos de vigencia.
- **Estado:** ❌ Faltante.

### 7.2 Completar Gestión del Administrador (`ADMIN`)
- **Objetivo:** Desarrollar las interfaces y la lógica para que un `ADMIN` pueda gestionar su condominio de forma individual (no solo por CSV).
- **Tareas Pendientes:**
    - ✅ **Creación y edición individual de `Unit`:** Implementado.
    - ✅ **Aprobación y gestión individual de `User` para su condominio:** Implementado.
    - ❌ **Asignación individual de `Unit` a `User`:** Faltante.
    - 🚧 Interfaz para gestionar la configuración del condominio (`CondominioConfig`).

### 7.3 Implementación de Auditoría
- **Objetivo:** Crear un sistema de trazabilidad de acciones críticas implementando el modelo `AuditLog` (ver 5.5.2).
- **Estado:** ❌ Faltante.

### 7.4 Componentes de Escalabilidad (Visión a Largo Plazo)
- **Celery:** Para tareas asíncronas (ej. envío de correos, procesamiento de reportes).
- **Redis:** Para caché y gestión de sesiones.
- **Nginx:** Como servidor web/proxy inverso en producción.
- **Mejoras Frontend:** Uso de DataTables y Chart.js para visualización de datos.

## 8. Consideraciones para Futuras Mejoras
- **Modularización:** La estructura actual es adecuada, pero a medida que el proyecto crezca, se puede evaluar una mayor modularización (ej. `app/api/v1/`, `app/core/`) para desacoplar componentes.
- **Refinamiento de Permisos:** Una vez implementados los roles especiales, se necesitará un sistema de permisos más granular que el basado solo en los roles base (`MASTER`, `ADMIN`, `USER`).
- **Testing:** Es crucial incrementar la cobertura de tests unitarios y de integración a medida que se añaden nuevas funcionalidades.
