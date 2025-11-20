# Sistema de Gestión de Condominios

**CondoManager** es un sistema web multi-tenant para la gestión de condominios, desarrollado con Flask y SQLAlchemy.

*   **Repositorio Principal:** [https://github.com/ginaproanio/condomanager](https://github.com/ginaproanio/condomanager)
*   **Ambiente de Producción:** [https://condomanager.puntablancaecuador.com/](https://condomanager.puntablancaecuador.com/)

## Flujo de Trabajo y Desarrollo

El desarrollo de este proyecto sigue un flujo de trabajo basado en GitOps, donde el repositorio de GitHub es la única fuente de verdad y los despliegues son automáticos.

1.  **Desarrollo Local:** Todo el código se edita localmente usando un editor como **Visual Studio Code**. No es necesario ejecutar la aplicación ni una base de datos localmente.
2.  **Control de Versiones:** Los cambios se confirman y se suben a un branch en el repositorio de **GitHub**.
3.  **Despliegue:** Al hacer merge a la rama principal, **Railway** detecta los cambios y despliega automáticamente la nueva versión.

> ⚠️ **Proceso de Despliegue en Railway**:
> El archivo `Procfile` le indica a Railway que ejecute dos comandos en la fase `release`:
> 1.  `flask db upgrade`: Aplica cualquier nueva migración de la base de datos usando **Flask-Migrate**.
> 2.  `python seed_initial_data.py`: Ejecuta un script que siembra los datos iniciales (como el usuario MASTER) solo si la base de datos es nueva.

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

```
/condomanager-saas/
├── app/
│   ├── __init__.py         # Fábrica de la aplicación (create_app).
│   ├── routes/             # Módulo que agrupa todos los Blueprints de rutas.
│   ├── models.py           # Modelos de la base de datos (SQLAlchemy).
│   ├── static/             # Archivos estáticos (CSS, JS).
│   └── templates/          # Plantillas HTML.
├── migrations/             # Directorio de Flask-Migrate para las versiones de la DB.
├── docs/                   # Documentación del proyecto.
├── .env                    # Variables de entorno (no versionado).
├── Procfile                # Comandos de ejecución para Railway.
├── seed_initial_data.py    # Script para sembrar datos iniciales.
├── config.py               # Clases de configuración para la aplicación.
├── requirements.txt        # Dependencias de Python.
└── run.py                  # Punto de entrada para Gunicorn.
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
