# CondoManager SaaS - Documentación Técnica

## 🟢 Estado Actual: 100% EN PRODUCCIÓN

*   **Dominio definitivo**: [https://condomanager.vip](https://condomanager.vip)
*   **Wildcard activo**: `*.condomanager.vip` (todos los subdominios funcionan automáticamente)
*   **Versión**: 1.0.0 (Noviembre 2025)

---

## 🏗️ Infraestructura de Producción

El sistema opera en una arquitectura **Multi-Tenant** aislada por subdominios, desplegada en **Railway**.

| Componente | Detalle |
| :--- | :--- |
| **Hosting** | Railway.app (Plan Hobby) |
| **Base de Datos** | PostgreSQL en Railway (Volumen persistente, esquemas separados por tenant) |
| **Dominio & DNS** | Cloudflare Registrar + Cloudflare DNS (Full Setup) |
| **SSL** | Cloudflare Universal SSL + Wildcard automático (Full Strict) |
| **Puerto** | 8080 (Expuesto en Railway) |
| **Repositorio** | [github.com/ginaproanio/condomanager](https://github.com/ginaproanio/condomanager) |
| **Rama Principal** | `main` (Despliegue automático a producción) |

### Variables de Entorno Críticas
*   `PORT=8080`
*   `DATABASE_URL=postgresql://...`
*   `PAYPHONE_*` (Credenciales de pasarela de pagos)

---

## 🏛️ Arquitectura Multi-Tenant

Cada condominio tiene su propio entorno aislado:
1.  **Subdominio personalizado**: `edificio1.condomanager.vip`
2.  **Aislamiento de Datos**: Esquema separado en PostgreSQL para cada tenant.
3.  **Demo**: [https://demo.condomanager.vip](https://demo.condomanager.vip)

---

## 📝 Descripción del Producto

**Gestión inteligente de condominios y edificios residenciales**

CondoManager es la plataforma SaaS líder en gestión de condominios y edificios residenciales en Latinoamérica. Arquitectura multi-tenant con datos aislados por edificio, integración de pagos PayPhone, gestión de usuarios y roles, reservas de áreas comunes y mantenimiento digital. Subdominio personalizado automático (`tuedificio.condomanager.vip`). Desarrollado por SORSABSA.

**Hashtags Oficiales:**
`#PropTech` `#CondoTech` `#HOAManagement` `#SaaS` `#LatamTech` `#GestiónDeCondominios`

---

## 📄 Documentos Clave

### 1. Estándares de Diseño y UX
*   **[docs/design.md](docs/design.md)**: (CRÍTICO) Guías de estilo y componentes UI.

### 2. Arquitectura y Módulos
*   **[docs/02_ARQUITECTURA.md](docs/02_ARQUITECTURA.md)**: Visión técnica global.
*   **[docs/11_MODULOS_FINANCIEROS.md](docs/11_MODULOS_FINANCIEROS.md)**: Módulos de Recaudación, Caja Chica y Contabilidad.
*   **[docs/10_MODULOS_FUTUROS.md](docs/10_MODULOS_FUTUROS.md)**: Hoja de ruta (Marketplace, IoT, etc.).

### 3. Roles y Permisos
*   **[docs/08_ROLES_Y_PERMISOS.md](docs/08_ROLES_Y_PERMISOS.md)**: Matriz de acceso.

---

## 🚀 Guía Rápida para Desarrolladores

### Configuración de DNS (Cloudflare)
Si se realiza un redeploy que cambie la dirección de Railway, actualizar los registros CNAME:

| Type | Name | Content | Proxy |
| :--- | :--- | :--- | :--- |
| CNAME | `@` | `8zbz4b4a.up.railway.app` | Proxied (Nube Naranja) |
| CNAME | `*` | `8zbz4b4a.up.railway.app` | Proxied (Nube Naranja) |

### Crear Nuevo Tenant (Condominio)
1.  Acceder al panel Master (`/master`).
2.  Crear nuevo condominio asignando un `subdomain` único.
3.  El sistema creará automáticamente el esquema en PostgreSQL y activará el subdominio (gracias al DNS Wildcard).

### Instalación Local
```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
flask db upgrade
python seed_initial_data.py
flask run
```

---

## ✅ Tareas Pendientes / Recordatorios Técnicos

1.  **Monitorización**: Revisar logs en Railway regularmente.
2.  **Escalabilidad**: Preparar upgrade a plan Pro de Railway al superar límites de Custom Domain o recursos.
3.  **Mantenimiento**: Mantener actualizadas las variables de entorno si cambian proveedores externos.
