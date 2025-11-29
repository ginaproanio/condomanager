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
Este proyecto sigue convenciones de código y documentación para asegurar claridad y mantenibilidad. Ver [00_CONVENCIONES.md](./00_CONVENCIONES.md) para más detalles.

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
> - Documentación de alto nivel (como este Índice) puede estar en español para claridad del equipo.

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

## 3. Índice de Documentación Técnica

### 3.1 Arquitectura y Core
- **[00_CONVENCIONES.md](./00_CONVENCIONES.md)**: Constitución Técnica (Reglas y Antipatrones).
- **[01_INDICE.md](./01_INDICE.md)**: Este archivo (Mapa de navegación).
- **[02_ARQUITECTURA.md](./02_ARQUITECTURA.md)**: Diseño de alto nivel, Multi-Tenancy y decisiones técnicas.
- **[03_PLAN_IMPLEMENTACION_LOGIN.md](./03_PLAN_IMPLEMENTACION_LOGIN.md)**: **Fuente de Verdad** sobre el flujo de login Multi-Tenant.
- **[03_DATABASE.md](./03_DATABASE.md)**: Esquema de base de datos, modelos y migraciones.
- **[04_API.md](./04_API.md)**: Referencia de Endpoints y flujos de datos.
- **[05_INSTALACION.md](./05_INSTALACION.md)**: Guía de setup para desarrolladores.
- **[06_DEPLOYMENT.md](./06_DEPLOYMENT.md)**: Guía de operaciones en Railway y Cloudflare.

### 3.2 Reglas de Negocio y Seguridad
- **[07_REGLAS_NEGOCIO.md](./07_REGLAS_NEGOCIO.md)**: Lógica específica del dominio (Cobros, Multas, etc.).
- **[08_ROLES_Y_PERMISOS.md](./08_ROLES_Y_PERMISOS.md)**: Matriz de accesos y perfiles de usuario.

### 3.3 UI/UX
- **[09_DESIGN_SYSTEM.md](./09_DESIGN_SYSTEM.md)**: Guía de estilos, componentes y estándares de interfaz.

### 3.4 Roadmap y Estrategia
- **[10_MODULOS_FUTUROS.md](./10_MODULOS_FUTUROS.md)**: Roadmap de features (Marketplace, B2B).
- **[11_MODULOS_FINANCIEROS.md](./11_MODULOS_FINANCIEROS.md)**: Estrategia de monetización.

### 3.5 Soporte
- **[12_MANUAL_USUARIO.md](./12_MANUAL_USUARIO.md)**: Guía para administradores y usuarios finales.

### 3.6 Planificación e Integraciones (Subcarpetas)
- **Integraciones (`/docs/integrations/`)**:
  - [Google Drive](./integrations/google_drive_integration.md)
- **Planificación (`/docs/planning/`)**:
  - [API Firmas OneShot](./planning/api_firmas_oneshot.md)
  - [Módulo Firmas](./planning/firmasycom.md)
  - [Implementación Pagos](./planning/plan_implementacion_pagos.md)
  - [Implementación WhatsApp](./planning/plan_implementacion_whatsapp.md)

### 3.7 Referencias
- **`/docs/references/`**: Manuales externos y especificaciones.

## 4. Versionamiento
Este proyecto sigue [Versionamiento Semántico](https://semver.org/lang/es/).
