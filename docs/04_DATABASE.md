# Documentación Base de Datos
Versión: v1.0.0-beta

## 1. Esquema General
```sql
CREATE DATABASE condominio CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

## 2. Tablas de Configuración

### 2.1 Tipos de Unidad
```sql
CREATE TABLE unit_types (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    condominium_id BIGINT NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (condominium_id) REFERENCES condominiums(id),
    INDEX idx_code (code),
    INDEX idx_condominium (condominium_id)
);

-- Datos iniciales para Punta Blanca
INSERT INTO unit_types (code, name, condominium_id) VALUES
('LOTE', 'Lote', 1),
('BODEGA', 'Bodega', 1),
('CASA', 'Casa', 1),
('DEPARTAMENTO', 'Departamento', 1);
```

### 2.2 Estados de Unidad
```sql
CREATE TABLE unit_states (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,
    name VARCHAR(50) NOT NULL,
    description TEXT,
    condominium_id BIGINT NOT NULL,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (condominium_id) REFERENCES condominiums(id),
    INDEX idx_code (code),
    INDEX idx_condominium (condominium_id)
);

-- Datos iniciales para Punta Blanca
INSERT INTO unit_states (code, name, condominium_id) VALUES
('EN_ARRIENDO', 'En Arriendo', 1),
('EN_VENTA', 'En Venta', 1),
('SIN_USO', 'Sin Uso', 1),
('CONSTRUYENDO', 'Construyendo', 1);
```

### 2.3 Unidades
```sql
CREATE TABLE units (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    codigo_predial_nuevo VARCHAR(20) UNIQUE NOT NULL,
    codigo_predial_anterior VARCHAR(20) NOT NULL,
    lote VARCHAR(4) NOT NULL,
    manzana VARCHAR(4) NOT NULL,
    nomenclatura VARCHAR(5) NOT NULL,
    numero_casa VARCHAR(4) NOT NULL,
    calle_principal VARCHAR(80) NOT NULL,
    calle_secundaria VARCHAR(80) NOT NULL,
    area_terreno FLOAT NOT NULL,
    area_construccion FLOAT NOT NULL,
    avaluo_comercial FLOAT NOT NULL,
    avaluo_municipal FLOAT NOT NULL,
    latitud DECIMAL(10,8) NOT NULL,
    longitud DECIMAL(11,8) NOT NULL,
    
    -- Referencias a las tablas de tipos
    type_id BIGINT NOT NULL,
    state_id BIGINT NOT NULL,
    condominium_id BIGINT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (type_id) REFERENCES unit_types(id),
    FOREIGN KEY (state_id) REFERENCES unit_states(id),
    FOREIGN KEY (condominium_id) REFERENCES condominiums(id),
    
    INDEX idx_lote (lote),
    INDEX idx_manzana (manzana),
    INDEX idx_type (type_id),
    INDEX idx_state (state_id),
    INDEX idx_condominium (condominium_id)
);
```

## 3. Consideraciones
- Cada condominio puede definir sus propios tipos y estados de unidades
- Los tipos y estados base se crean al inicializar un nuevo condominio
- Se mantiene un histórico de cambios de estado mediante triggers

## 4. Tablas Principales

### 4.1 Roles y Permisos
```sql
-- Roles y Permisos
CREATE TABLE roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(20) UNIQUE NOT NULL,  -- SUPER_ADMIN, ADMIN, UNIT_USER
    name VARCHAR(50) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE permissions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE role_permissions (
    role_id BIGINT NOT NULL,
    permission_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

-- Usuarios
CREATE TABLE users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    telefono VARCHAR(20),
    role_id BIGINT NOT NULL,
    status ENUM('pending', 'active', 'rejected', 'inactive') DEFAULT 'pending',
    ultimo_acceso TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Relación Administrador-Condominio
CREATE TABLE condominium_administrators (
    user_id BIGINT NOT NULL,
    condominium_id BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, condominium_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (condominium_id) REFERENCES condominiums(id)
);

-- Relación Usuario-Unidad con histórico
CREATE TABLE unit_assignments (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    unit_id BIGINT NOT NULL,
    user_id BIGINT NOT NULL,
    status ENUM('active', 'inactive') DEFAULT 'active',
    start_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_date TIMESTAMP NULL,
    created_by BIGINT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (unit_id) REFERENCES units(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
);
```

[resto del contenido igual...]

## 8. Consideraciones Importantes

### 8.1 Estados Permitidos
- Estados para unidades:
  - 'En Arriendo'
  - 'En Venta'
  - 'Sin Uso'
  - 'Construyendo'
- Estados para usuarios:
  - 'ACTIVO'
  - 'INACTIVO'
- Roles de usuario:
  - 'ADMIN'
  - 'USUARIO'

### 8.2 Validaciones de Campos
- `codigo_predial_nuevo`: Debe ser único en el sistema
- `latitud`: Rango válido entre -90 y 90
- `longitud`: Rango válido entre -180 y 180
- `area_terreno`, `area_construccion`: Valores positivos mayores a 0
- `avaluo_comercial`, `avaluo_municipal`: Valores positivos mayores a 0

### 8.3 Manejo de Coordenadas
- `latitud`: DECIMAL(10,8) para precisión de hasta 1.11 metros
- `longitud`: DECIMAL(11,8) para precisión de hasta 1.11 metros

### 8.4 Notas de Cambios
- La tabla `usuarios` fue renombrada a `users` para mantener consistencia con la convención de nombres en inglés usada en el resto del proyecto
