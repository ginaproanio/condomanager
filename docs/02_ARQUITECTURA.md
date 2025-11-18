# Arquitectura del Sistema

## 1. Visión General
Sistema multi-condominio implementado inicialmente para "Punta Blanca", diseñado para escalar a múltiples instancias.

## 2. Stack Tecnológico Actual
### 2.1 Backend
- Python con Flask Framework
- SQLAlchemy ORM
- Flask-JWT-Extended para autenticación (con cookies HTTP-Only)
- Gunicorn para servir la aplicación en producción
- `hashlib` para hashing de contraseñas

### 2.2 Frontend
- Bootstrap 5 (CSS y JS)
- JavaScript vanilla (para lógica de autenticación y UI dinámica)

### 2.3 Base de Datos
- PostgreSQL (en producción)
- SQLite (en desarrollo)

## 3. Estructura del Proyecto Actual

```
/condomanager-saas/
├── app/
│   ├── __init__.py     # Inicialización de la aplicación Flask, JWT, CORS
│   ├── extensions.py   # Instancia de SQLAlchemy (db) para evitar dependencias circulares
│   ├── models.py       # Definición de todos los modelos de base de datos (User, Condominium, Unit, etc.)
│   ├── routes.py       # Definición CENTRALIZADA de TODAS las rutas (públicas, protegidas, API, maestro, admin)
│   ├── tenant.py       # Lógica para determinar el tenant de la solicitud
│   ├── static/         # Archivos estáticos (CSS, JS, imágenes)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   └── templates/      # Plantillas HTML
│       ├── admin/      # Templates para el panel de administradores (admin/panel.html, admin/condominio_panel.html)
│       ├── auth/       # Templates de autenticación (login.html, registro.html)
│       ├── master/     # Templates para el panel maestro (master/panel.html, master/condominios.html, master/usuarios.html, master/configuracion.html, master/editar_usuario.html)
│       ├── services/   # Templates para servicios (unidades.html, pagos.html, reportes.html)
│       ├── user/       # Templates para usuarios regulares (dashboard.html)
│       └── base.html   # Plantilla base compartida
├── config.py           # Configuración principal de Flask y JWT (cargando de variables de entorno)
├── initialize_db.py    # Script para inicializar la base de datos (crear tablas, usuario maestro)
├── Procfile            # Configuración de despliegue en Railway (ejecuta initialize_db.py y gunicorn)
├── requirements.txt    # Dependencias de Python
└── docs/               # Documentación del proyecto (este archivo y otros borradores)
```

## 4. Estrategia Multi-Condominio (Multi-Tenancy)
La implementación actual utiliza una estrategia de **multi-tenancy de esquema compartido** (`shared-schema multi-tenancy`).

- **Base de Datos Única:** Todos los datos (usuarios, condominios, unidades) residen en una única base de datos.
- **Separación Lógica:** La separación de datos entre condominios se logra mediante un campo `tenant` (o `condominium_id` para usuarios/unidades) en los modelos de la base de datos.
- **Determinación del Tenant:** La lógica en `app/tenant.py` determina el inquilino (tenant) basándose en el subdominio de la solicitud HTTP. Por defecto, si no se encuentra un subdominio válido, se utiliza 'puntablanca'.

## 5. Modelos Principales (definidos en `app/models.py`)

### 5.1 User
- Atributos clave: `id`, `email`, `name`, `password_hash`, `tenant`, `role`, `status`, `condominium_id` (para ADMINs).
- Roles base: `MASTER`, `ADMIN`, `USER`.
- Relaciones: Puede estar asignado a una `Unit` (`unit_id`).

### 5.2 Condominium
- Atributos clave: `id`, `name`, `address`, `city`, `country`, `status`, `tenant`.
- Relaciones: Contiene múltiples `Unit`s y `User`s (ADMINs asignados).

### 5.3 Unit
- Atributos clave: `id`, `property_number`, `name`, `property_type`, `area_m2`, `bedrooms`, `bathrooms`, `condominium_id`.
- Relaciones: Pertenece a un `Condominium`, puede tener `User`s de unidad asignados.

### 5.4 CondominioConfig (en `app/models.py`)
- Atributos clave: `tenant`, `primary_color`, `nombre_comercial`.
- Propósito: Configuración específica de cada inquilino/condominio.

## 6. Seguridad
- **Autenticación:** JWT con cookies HTTP-Only (gestionado por Flask-JWT-Extended).
- **Autorización:** Verificación de roles y permisos en cada ruta protegida.
- **Hashing de Contraseñas:** SHA256.
- HTTPS obligatorio en producción.

## 7. Próximas Funcionalidades (Visión del Borrador Original y Necesidades Actuales)
Esta sección documenta funcionalidades y componentes que están en borradores (`docs/08_ROLES_Y_PERMISOS.md`, etc.) o que son necesidades identificadas, pero que no están completamente implementadas en la arquitectura actual.

### 7.1 Roles Especiales y su Gestión
- **Roles:** PRESIDENTE, SECRETARIO, TESORERO, CONTADOR, VOCAL.
- **Gestión:** Asignación y revocación por el ADMINISTRADOR de un condominio, con período de vigencia.
- **Estructura DB:** Requiere una tabla `user_special_roles`.

### 7.2 Gestión Detallada de Condominios por ADMIN
- Un ADMIN debe poder:
    - Ver y editar datos completos del condominio al que está asignado.
    - Registrar la directiva (usando roles especiales).
    - Crear y gestionar unidades individualmente.
    - Importar unidades masivamente por CSV.
    - Crear y gestionar usuarios de unidades individualmente.
    - Importar usuarios de unidades masivamente por CSV (relacionados con unidades).
    - Generar y gestionar pagos.
    - Hacer cobranzas.
    - Generar reportes específicos del condominio.

### 7.3 Componentes de Escalabilidad/Rendimiento (del borrador original)
- Celery para tareas asíncronas.
- Redis para caché y sesiones.
- Nginx como servidor web.
- DataTables y Chart.js para frontend.
- Estrategias avanzadas de caché, monitoreo y balanceo de carga.

## 8. Consideraciones para Futuras Mejoras
- **Modularización:** La arquitectura borrador original (con `app/api/v1/auth/`, `app/core/`, etc.) representa un objetivo a largo plazo para una mayor escalabilidad y separación de responsabilidades, que podría ser abordada cuando las necesidades del proyecto lo requieran o superen la capacidad de la estructura actual.
