# Sistema de Gestión de Condominios

Sistema web para la gestión de condominios desarrollado con Flask.

## Inicio Rápido

### 1. Inicialización del Proyecto
```batch
# Windows
scripts\init_project.bat

# Linux/Mac
./scripts/init_project.sh
```
Este script:
- Crea la estructura completa de directorios
- Inicializa la base de datos 'condominio'
- Crea el archivo .env con configuración inicial
- Crea usuario administrador por defecto

### 2. Configuración del Repositorio
```batch
# Windows
scripts\init_repo.bat

# Linux/Mac
./scripts/init_repo.sh
```
Este script:
- Inicializa repositorio Git
- Crea .gitignore
- Realiza commit inicial
- Configura estructura base del proyecto

### 3. Respaldos
```batch
# Windows
scripts\backup_code.bat

# Linux/Mac
./scripts/backup_code.sh
```
Este script:
- Crea respaldo completo del código
- Incluye archivos de configuración
- Genera archivo comprimido con timestamp

### 4. Siguiente Paso
Después de la inicialización:
1. Crear entorno virtual: `python -m venv venv`
2. Activar entorno: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
3. Instalar dependencias: `pip install -r requirements.txt`
4. Ejecutar la aplicación: `flask run`

> ⚠️ **Credenciales Iniciales**:
> - Email: gina.proanio76@gmail.com
> - Contraseña: admin123
> 
> **¡Cambiar en producción!**

## 1. Convenciones del Proyecto
Este proyecto sigue estrictas convenciones de código y documentación, especialmente en cuanto al uso del español como idioma principal. Ver [docs/00_CONVENCIONES.md](./docs/00_CONVENCIONES.md) para más detalles.

> **IMPORTANTE**: Toda la documentación y el código de este proyecto DEBE estar en español, incluyendo:
> - Nombres de variables, funciones y clases
> - Comentarios en el código
> - Documentación técnica y de usuario
> - Mensajes de commit
> - Issues y Pull Requests
>
> Excepciones permitidas:
> - Palabras reservadas de Python/Flask (class, def, import, etc.)
> - Nombres de métodos HTTP (GET, POST, etc.)
> - Términos técnicos estándar (id, email, password, etc.)

## 2. Estructura del Proyecto (INMUTABLE)

> ⚠️ **IMPORTANTE**: Esta estructura es INMUTABLE y NO DEBE modificarse sin la autorización explícita del arquitecto principal. 
> Cualquier propuesta de cambio debe ser documentada y justificada técnicamente antes de su evaluación.

```
/condominio
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth/
│   │       ├── admin/
│   │       └── public/
│   ├── core/
│   │   ├── config/
│   │   ├── database/
│   │   └── security/
│   ├── models/
│   │   ├── auth/
│   │   ├── admin/
│   │   └── public/
│   └── templates/
│       ├── auth/
│       ├── admin/
│       ├── public/
│       └── shared/
├── config/
│   ├── dev/
│   ├── prod/
│   └── test/
├── scripts/
│   ├── windows/
│   └── database/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

### 2.1 Propósito de cada Directorio

#### app/
- **api/**: Endpoints REST de la aplicación
  - **v1/**: Primera versión de la API
    - **auth/**: Autenticación y autorización
    - **admin/**: Funcionalidades administrativas
    - **public/**: Endpoints públicos
- **core/**: Núcleo del sistema
  - **config/**: Configuraciones centrales
  - **database/**: Gestión de base de datos
  - **security/**: Seguridad y permisos
- **models/**: Modelos de datos por módulo
- **templates/**: Plantillas HTML organizadas por módulo

#### config/
- **dev/**: Configuraciones de desarrollo
- **prod/**: Configuraciones de producción
- **test/**: Configuraciones de pruebas

#### scripts/
- **windows/**: Scripts específicos para Windows
- **database/**: Scripts de base de datos

#### tests/
- **unit/**: Pruebas unitarias
- **integration/**: Pruebas de integración
- **e2e/**: Pruebas end-to-end

## 3. Documentación Técnica

### 3.1 Documentación Base
- [00_CONVENCIONES.md](./docs/00_CONVENCIONES.md): Reglas y estándares del proyecto
- [01_MANUAL_USUARIO.md](./docs/01_MANUAL_USUARIO.md): Manual de usuario detallado
- [02_ARQUITECTURA.md](./docs/02_ARQUITECTURA.md): Diseño y especificaciones técnicas
- [03_API.md](./docs/03_API.md): Documentación de endpoints
- [04_DATABASE.md](./docs/04_DATABASE.md): Estructura y gestión de base de datos
- [05_INSTALACION.md](./docs/05_INSTALACION.md): Guía de instalación general

### 3.2 Documentación de Despliegue y Operaciones
- [06_DEPLOYMENT.md](./docs/06_DEPLOYMENT.md): Guía de despliegue en producción
- [07_MONITORING.md](./docs/07_MONITORING.md): Sistema de monitoreo y logs
- [08_ROLES_Y_PERMISOS.md](./docs/08_ROLES_Y_PERMISOS.md): Gestión de roles y permisos

### 3.3 Documentación Específica por Sistema Operativo
- [WINDOWS_SETUP.md](./docs/WINDOWS_SETUP.md): Guía específica para Windows

### 3.4 Documentación de Control de Versiones
- [CHANGELOG.md](./docs/CHANGELOG.md): Historial de cambios
- [ROADMAP.md](./docs/ROADMAP.md): Plan de desarrollo futuro

## 4. Versionamiento
Este proyecto sigue [Versionamiento Semántico](https://semver.org/lang/es/).
