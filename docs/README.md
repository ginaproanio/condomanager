# Sistema de Gestión de Condominios

**CondoManager** es un sistema web multi-tenant para la gestión de condominios, desarrollado con Flask y SQLAlchemy.

*   **Repositorio Principal:** [https://github.com/ginaproanio/condomanager](https://github.com/ginaproanio/condomanager)
*   **Ambiente de Producción:** [https://condomanager.puntablancaecuador.com/](https://condomanager.puntablancaecuador.com/)

## Inicio Rápido

### 1. Configuración del Entorno
1.  **Clonar el repositorio.**
2.  **Crear y activar un entorno virtual:**
    ```bash
    python -m venv venv
    # Windows
    venv\Scripts\activate
    # Linux/Mac
    source venv/bin/activate
    ```
3.  **Instalar dependencias:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configurar variables de entorno:**
    Crea un archivo `.env` en la raíz del proyecto basándote en `.env.example` (si existe) y define las variables necesarias como `SECRET_KEY`, `JWT_SECRET_KEY` y `SQLALCHEMY_DATABASE_URI`.

### 2. Ejecutar la Aplicación
```bash
flask run
```

> ⚠️ **Credenciales Iniciales**:
> El usuario `MASTER` se crea a través del script `initialize_db.py` o al iniciar la aplicación por primera vez, utilizando las variables de entorno `MASTER_EMAIL` y `MASTER_PASSWORD`.
> 
> **¡Cambiar en producción!**

## 1. Convenciones del Proyecto
Este proyecto sigue convenciones de código y documentación para asegurar claridad y mantenibilidad. Ver [docs/00_CONVENCIONES.md](./docs/00_CONVENCIONES.md) para más detalles.

> **IMPORTANTE**: Todo el código y los identificadores técnicos de este proyecto DEBEN estar en **inglés**, incluyendo:
> - Nombres de variables, funciones, clases, atributos y métodos.
> - Nombres de tablas y columnas en la base de datos.
> - Endpoints de la API.
> - Comentarios en el código
> - Mensajes de commit.
> - Nombres de archivos y directorios.
>
> Excepciones permitidas:
> > - **Texto visible para el usuario final**: El contenido de texto destinado a la interfaz de usuario (UI), como etiquetas en plantillas HTML, mensajes de `flash` o alertas, **debe estar en español**.
> - Documentación de alto nivel (como este README) puede estar en español para claridad del equipo.

## 2. Estructura del Proyecto (INMUTABLE)

```bash
/condomanager-saas/
├── app/
│   ├── __init__.py         # Inicialización de la aplicación Flask y registro de componentes.
│   ├── auth.py             # Funciones auxiliares de autenticación.
│   ├── decorators.py       # Decoradores personalizados para control de acceso (roles).
│   ├── extensions.py       # Instancia de SQLAlchemy (db).
│   ├── models.py           # Definición de todos los modelos de la base de datos.
│   ├── tenant.py           # Lógica para determinar el tenant de la solicitud.
│   ├── routes/             # Módulo que contiene todas las rutas (endpoints).
│   ├── static/             # Archivos estáticos (CSS, JS, imágenes).
│   └── templates/          # Plantillas HTML (vistas).
├── docs/                   # Documentación del proyecto.
├── .env                    # Variables de entorno (no versionado).
├── config.py               # Clases de configuración para la aplicación.
├── requirements.txt        # Dependencias de Python.
└── wsgi.py                 # Punto de entrada para servidores WSGI como Gunicorn.
```

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
