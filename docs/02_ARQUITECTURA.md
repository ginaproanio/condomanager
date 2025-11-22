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
│   │   ├── admin_routes.py  # Rutas para administradores de condominio.
│   │   ├── master_routes.py # Rutas para el super-administrador (rol MASTER).
│   │   │   # Endpoints clave:
│   │   │   # - /master/condominios (GET)
│   │   │   # - /master/crear_condominio (GET, POST)
│   │   │   # - /master/condominios/editar/<id> (GET, POST)
│   │   │   # - /master/condominios/importar (POST)
│   │   │   # (Incluye endpoints como /master/condominios, /master/usuarios, /master/condominios/importar, etc.)
│   │   │   # - /master/usuarios (GET)
│   │   │   # - /master/usuarios/crear (GET, POST)
│   │   │   # - /master/usuarios/editar/<id> (GET, POST)
│   │   │   # - /master/usuarios/importar_admins (POST)
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
- **Atributos:** `id`, `cedula`, `email`, `first_name`, `last_name`, `birth_date`, `cellphone`, `city`, `country`, `password_hash`, `tenant`, `role`, `status`, `created_at`, `unit_id`.
- Roles base: `MASTER`, `ADMIN`, `USER`.
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
