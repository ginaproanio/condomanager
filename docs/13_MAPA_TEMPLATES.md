# 12. Mapa de Templates Principales

Este documento es la **fuente de verdad** para localizar los archivos de template (`.html`) que corresponden a los paneles y vistas principales de cada rol. Su propósito es eliminar confusiones y servir como guía de referencia rápida durante el desarrollo y la auditoría.

---

### `app/templates/public/`
Vistas públicas que no requieren autenticación.
- **`home.html`**: Página de inicio y marketing (landing page).
- **`demo_request.html`**: Formulario para solicitar una demostración.

### `app/templates/auth/`
Formularios de autenticación.
- **`login.html`**: Formulario de inicio de sesión.
- **`registro.html`**: Formulario de registro de nuevos usuarios.

### `app/templates/admin/`
Vistas para el rol `ADMIN`. **Opera en el contexto de un tenant (`/<tenant_slug>/...`)**.
- **`panel.html`**: Panel principal del administrador con estadísticas de usuarios pendientes.
- **`condominio_panel.html`**: Panel de gestión detallada del condominio (unidades, usuarios, directiva, etc.).
- **`crear_editar_unidad.html`**: Formulario para crear o modificar una unidad inmobiliaria.
- **`editar_usuario_unidad.html`**: Formulario para editar los datos de un usuario dentro del condominio.
- **`finanzas.html`**: Panel para la gestión de pagos (aprobación/rechazo de transferencias).
- **`config_pagos.html`**: Formulario para configurar la pasarela de pagos (PayPhone) del condominio.
- **`petty_cash.html`**: Panel para la gestión de caja chica (ingresos y egresos menores).
- **`reportes.html`**: Panel para la descarga de reportes en formato CSV.
- **`comunicaciones.html`**: Panel para la configuración y envío de comunicaciones por WhatsApp.

### `app/templates/master/`
Vistas para el rol `MASTER`. **Opera a nivel global (`/master/...`)**.
- **`panel.html`**: Panel principal del MASTER con acceso a la gestión de condominios, usuarios globales y configuración de la plataforma.
- **`condominios.html`**: Listado y gestión de todos los condominios de la plataforma.
- **`crear_condominio.html`**: Formulario para registrar un nuevo condominio.
- **`editar_condominio.html`**: Formulario para editar los datos de un condominio existente.
- **`usuarios.html`**: Listado y gestión de todos los usuarios de la plataforma.
- **`crear_usuario.html`**: Formulario para crear un nuevo usuario (ADMIN o USER).
- **`editar_usuario.html`**: Formulario para editar los datos de cualquier usuario (permite cambiar rol y condominio).
- **`configuracion.html`**: Panel para configurar parámetros globales de la plataforma (APIs, cuentas bancarias, etc.).
- **`reports.html`**: Panel para la visualización de métricas y descarga de reportes gerenciales.
- **`module_catalog.html`**: Panel para gestionar el catálogo global de módulos (precios, estados).
- **`configure_condo_modules.html`**: Vista para personalizar los módulos y precios para un condominio específico.
- **`comunicaciones.html`**: Panel para la configuración y envío de comunicaciones corporativas por WhatsApp.
- **`document_audit.html`**: Vista de auditoría para todos los documentos generados en la plataforma.
- **`supervise_condominium.html`**: Panel de supervisión de solo lectura para un condominio específico.

### `app/templates/user/`
Vistas para el rol `USER` (residente/propietario).
- **`dashboard.html`**: Panel principal del usuario final.
- **`profile.html`**: Formulario para que el usuario edite su propio perfil.

### `app/templates/documents/`
Vistas para el módulo de "Firmas & Comunicados".
- **`index.html`**: Listado de documentos del usuario/condominio.
- **`editor.html`**: Editor de texto enriquecido para crear/editar documentos.
- **`view.html`**: Vista de lectura de un documento, con opciones de firma.

### `app/templates/services/`
Vistas para módulos específicos.
- **`pagos.html`**: Interfaz para que el usuario realice y reporte sus pagos.

