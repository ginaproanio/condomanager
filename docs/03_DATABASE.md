# Documentación de la Base de Datos
Versión: 4.0.0 (Final y Unificada: Noviembre 2025)

## 1. Visión General
La base de datos utiliza una estrategia de **esquema compartido (shared-schema)**. Todos los datos de todos los condominios residen en las mismas tablas, y la separación lógica se logra mediante columnas de identificación como `tenant` o `condominium_id`.

A continuación se describen las tablas **esenciales** para entender la arquitectura, basadas en los modelos de SQLAlchemy definidos en `app/models.py`.

## 2. Tablas Principales
 
### 2.1 Tabla `users`
Almacena la información de todos los usuarios del sistema, sin importar el condominio al que pertenezcan.
```sql
-- Basado en el modelo User en app/models.py
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    cedula VARCHAR(20) UNIQUE,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    birth_date DATE,
    password_hash VARCHAR(255) NOT NULL,
    condominium_id INTEGER, -- FK a la tabla 'condominiums'. Clave para el aislamiento de datos.
    role VARCHAR(20) NOT NULL, -- 'MASTER', 'ADMIN', 'USER'
    status VARCHAR(20) NOT NULL, -- 'pending', 'active', 'rejected'
    created_at TIMESTAMP WITHOUT TIME ZONE,
    unit_id INTEGER -- FK a la tabla 'units'
);
> **Nota:** Para el rol `MASTER`, el campo `condominium_id` puede ser nulo.

### 2.2 Tabla `condominiums`
Almacena la información de cada tenant (condominio). Es la tabla central de la arquitectura multi-tenant.
```sql
-- Basado en el modelo Condominium en app/models.py
CREATE TABLE condominiums (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL, -- Este es el 'tenant_slug' usado en las URLs
    status VARCHAR(20), -- 'ACTIVO', 'DEMO', 'INACTIVO'
    environment VARCHAR(20), -- 'production', 'demo', 'internal', 'sandbox'
    admin_user_id INTEGER, -- FK a la tabla 'users'
    -- Flags de módulos para control de acceso a features
    has_documents_module BOOLEAN,
    has_billing_module BOOLEAN
);
```

### 2.3 Tabla `units`
Representa las propiedades individuales (departamentos, casas, lotes) dentro de cada condominio.
```sql
-- Basado en el modelo Unit en app/models.py
CREATE TABLE units (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    property_number VARCHAR(50),
    condominium_id INTEGER NOT NULL, -- FK a la tabla 'condominiums'
    -- Otros campos descriptivos de la unidad...
);
```
