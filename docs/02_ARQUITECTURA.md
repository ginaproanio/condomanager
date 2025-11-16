# Arquitectura del Sistema

## 1. Visión General
Sistema multi-condominio implementado inicialmente para "Punta Blanca", diseñado para escalar a múltiples instancias.

## 2. Stack Tecnológico
### 2.1 Backend
- Python con Flask Framework
- SQLAlchemy ORM
- JWT para autenticación
- Celery para tareas asíncronas

### 2.2 Frontend
- Bootstrap 5
- JavaScript vanilla
- DataTables y Chart.js

### 2.3 Infraestructura
- MariaDB: Base de datos principal
- Redis: Caché y sesiones
- Nginx: Servidor web
- Supervisor: Gestión de procesos

## 1.5 Estructura del Proyecto

/condominios/              # Directorio raíz del proyecto
├── app/                    # Código principal de la aplicación
│   ├── api/               # Endpoints de la API
│   │   └── v1/           # Versión 1 de la API
│   ├── core/             # Núcleo de la aplicación
│   │   ├── config.py     # Configuraciones core
│   │   └── exceptions.py # Manejo de excepciones
│   ├── forms/            # Formularios
│   ├── models/           # Modelos de datos
│   ├── routes/           # Rutas de la aplicación
│   ├── schemas/          # Esquemas de validación
│   ├── services/         # Lógica de negocio
│   ├── templates/        # Plantillas HTML
│   │   ├── admin/       # Templates para administradores
│   │   ├── auth/        # Templates de autenticación
│   │   ├── unit_user/   # Templates para usuarios de unidades
│   │   └── shared/      # Templates compartidos
│   └── utils/            # Utilidades generales
├── config/               # Configuraciones del proyecto
│   ├── database.py      # Configuración de base de datos
│   └── settings.py      # Configuraciones generales
├── docs/                # Documentación
├── migrations/          # Migraciones de base de datos (Flask-Migrate)
│   ├── versions/       # Archivos de migración numerados
│   ├── script.py.mako  # Template para nuevas migraciones
│   ├── alembic.ini     # Configuración de Alembic
│   └── env.py          # Entorno de migraciones
├── scripts/            # Scripts de utilidad
├── tests/              # Pruebas unitarias y de integración
├── .env.example        # Ejemplo de variables de entorno
├── .gitignore         # Configuración de Git
└── pyproject.toml     # Configuración del proyecto

La carpeta migrations/ es generada automáticamente por Flask-Migrate y contiene
el historial de cambios de la estructura de la base de datos. Cada archivo en
versions/ representa una modificación al esquema, permitiendo actualizar o revertir
la base de datos de manera controlada. Esta carpeta debe estar bajo control de
versiones.

## 2. Estructura Multi-Condominio
### 2.1 Estado Actual
- Producción: Punta Blanca (puntablancaecuador.com)
- Desarrollo: Condominio de prueba (testcondominio.com)

### 2.2 Estructura de Datos
Cada condominio mantiene:
- Base de datos independiente
- Archivos separados
- Configuraciones propias

## 3. Modelos Principales

### 3.1 Tablas de Configuración
- `unit_types`: Tipos de unidad configurables por condominio
  - id (BIGINT, PK)
  - name (VARCHAR(50))
  - code (VARCHAR(20))
  - condominium_id (BIGINT, FK)
  - active (BOOLEAN)

- `unit_states`: Estados posibles de unidades
  - id (BIGINT, PK)
  - name (VARCHAR(50))
  - code (VARCHAR(20))
  - condominium_id (BIGINT, FK)
  - active (BOOLEAN)

### 3.2 Unidad (Unit)
- Configuración dinámica por condominio:
  - Tipos de unidad: Definidos en tabla `unit_types`
  - Estados: Definidos en tabla `unit_states`

- Atributos obligatorios:
  - código_predial_nuevo (VARCHAR(20), único)
  - código_predial_anterior (VARCHAR(20))
  - lote (VARCHAR(4))
  - manzana (VARCHAR(4))
  - nomenclatura (VARCHAR(5))
  - numero_casa (VARCHAR(4))
  - calle_principal (VARCHAR(80))
  - calle_secundaria (VARCHAR(80))
  - area_terreno (FLOAT)
  - area_construccion (FLOAT)
  - avaluo_comercial (FLOAT)
  - avaluo_municipal (FLOAT)
  - latitud (DECIMAL(10,8))
  - longitud (DECIMAL(11,8))
  - type_id (FK a unit_types)
  - state_id (FK a unit_states)
  - condominium_id (FK a condominiums)

### 3.3 Usuario (User)
- Roles: Administrador, Usuario de Unidad
- Atributos: nombre, contacto, credenciales
- Relaciones: Unidades, Notificaciones

### 3.4 Pago
- Tipos: PayPhone, Transferencia
- Estados: Pendiente, Completado, Rechazado
- Relaciones: Unidad, Usuario

## 4. Seguridad
- Autenticación JWT
- HTTPS obligatorio
- Rate limiting
- Validación de entrada
- Sanitización de datos

## 5. Optimizaciones y Límites

### 5.1 Búsqueda en Tiempo Real
- Implementación de debouncing (500ms)
- Límite mínimo: 3 caracteres
- Límite de resultados: 20 por consulta
- Caché Redis: TTL 5 minutos

### 5.2 Consideraciones de Rendimiento
- Monitoreo activo de consultas
- Índices optimizados para campos de búsqueda
- Balanceo de carga para consultas concurrentes
- Sistema de caché en múltiples niveles

## 6. Escalabilidad
### 6.1 Fase 1 (MVP)
- Hostinger compartido
- Caché básico
- Optimización de consultas

### 6.2 Futuro
- VPS dedicado
- Balanceo de carga
- CDN para estáticos

## 7. Monitoreo
- Logs estructurados
- Métricas básicas
- Alertas por email

## 8. Respaldos
- Base de datos: diario
- Archivos: semanal
- Retención: 30 días

## Optimizaciones Adicionales

### Caché Avanzado
- Estrategias de invalidación
- Políticas de expiración
- Gestión de memoria

### Monitoreo Extendido
- Métricas de rendimiento detalladas
- Logs estructurados
- Sistema de alertas
