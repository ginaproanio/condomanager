# Anexo: Plan de Implementación Definitivo para el Flujo de Login Multi-Tenant

**Propósito:** Este documento actualiza el plan de implementación de login para reflejar la solución arquitectónica correcta, derivada del análisis forense del error `DNS_PROBE_FINISHED_NXDOMAIN` y el `ImportError` subsiguiente. Su objetivo es servir como la **fuente de verdad** para cualquier desarrollo futuro relacionado con la autenticación y redirección en un entorno multi-tenant.

---

#### 1. Análisis Forense del Problema Original

La investigación determinó que el error de DNS no era un problema de red, sino el síntoma final de una reacción en cadena causada por una violación arquitectónica fundamental:

1.  **La Causa Raíz (El Antipatrón):** Los archivos de rutas de administración (`admin_routes.py`, `petty_cash_routes.py`) definían endpoints que **exigían un ID de condominio en la URL** (ej. `/admin/condominio/<int:condominium_id>`). Esto violaba directamente la **Prohibición 1.1 (Multi-Tenancy)** de `00_CONVENCIONES.md`, que obliga al uso de `g.condominium` en lugar de IDs en la URL.

2.  **El Fallo en la API de Login (`api_routes.py`):**
    *   Al intentar redirigir a un administrador, la función `api_login` llamaba a `url_for('admin.admin_condominio_panel')`.
    *   Flask, al ver que la ruta de destino requería un `condominium_id`, y al no recibirlo, lanzaba una excepción `BuildError` (Error de Construcción de URL).
    *   Esta excepción era capturada silenciosamente, la `redirect_url` quedaba nula o incorrecta, y el frontend intentaba redirigir a una dirección inexistente, causando el error de DNS.

3.  **La Refactorización Incompleta:** En un intento por solucionar el problema, se eliminó la función de ayuda `is_authorized_admin_for_condo`, pero no se reemplazó su uso en todas las rutas. Esto provocó un `ImportError` en el despliegue, impidiendo que la aplicación se iniciara y resultando en un error `502 Bad Gateway`.

**Conclusión Forense:** El problema no era el login en sí, sino que la arquitectura de las rutas de destino era incompatible con las convenciones multi-tenant del proyecto.

---

#### 2. Arquitectura de la Solución (El Flujo Correcto)

Para garantizar un flujo de login seguro y compatible, se establece el siguiente plan de implementación como **mandatorio**:

**Fase 1: Saneamiento de las Rutas de Destino**

1.  **Eliminar IDs de las URLs:** Todas las rutas dentro de los blueprints de administración (`admin_bp`, `petty_cash_bp`, etc.) **deben** ser refactorizadas para no aceptar `<int:condominium_id>` como parámetro.
    *   **Incorrecto:** `@admin_bp.route('/admin/condominio/<int:condominium_id>/panel')`
    *   **Correcto:** `@admin_bp.route('/admin/panel')`

2.  **Usar `g.condominium`:** Dentro de estas rutas, el objeto del condominio actual **debe** obtenerse exclusivamente de `g.condominium`, que es inyectado por el middleware `resolve_tenant`.

3.  **Centralizar la Autorización:** La lógica para verificar si un usuario es el administrador del tenant actual **debe** estar encapsulada en un decorador.
    *   **Acción:** Se ha creado y se **debe** usar el decorador `@admin_tenant_required` (definido en `app/decorators.py`) para proteger todas las rutas de administración de tenant. Este decorador se encarga de verificar el token JWT, la existencia de `g.condominium` y el rol del usuario.

**Fase 2: Implementación de la Redirección en la API de Login**

1.  **Punto de Entrada:** El login siempre se realiza en el dominio principal (ej. `condomanager.vip`) a través de la ruta `/api/auth/login`.

2.  **Autenticación y Descubrimiento:** La ruta `api_login` valida las credenciales. Si el usuario es un `ADMIN`, realiza una única consulta a la base de datos (`Condominium.query.filter_by(admin_user_id=user.id)`) con el único propósito de **descubrir el subdominio** al que debe ser redirigido. Esta consulta está permitida por las convenciones porque su fin es el enrutamiento, no el acceso a datos.

3.  **Construcción de URL Absoluta:** La `redirect_url` **debe** ser construida como una URL absoluta que incluya el subdominio.
    *   **Lógica:** `redirect_url = f"{scheme}://{subdominio}.{dominio_principal}{ruta_del_panel}"`
    *   **Ejemplo:** `https://algarrobos.condomanager.vip/admin/panel`

4.  **Respuesta de la API:** La API devuelve un JSON con `status: "success"` y la `redirect_url` absoluta. El frontend es responsable de ejecutar esta redirección.

**Fase 3: El Círculo de Confianza (Middleware y Autorización)**

1.  **Redirección:** El navegador del usuario es redirigido a la URL absoluta (ej. `https://algarrobos.condomanager.vip/admin/panel`).

2.  **Activación del Middleware:** En esta nueva petición, el middleware `resolve_tenant` (definido en `app/middleware.py`) se activa, extrae `algarrobos` del host y carga el condominio correspondiente en `g.condominium`.

3.  **Ejecución del Decorador:** El decorador `@admin_tenant_required` se ejecuta. Verifica que `g.condominium` existe y que el `current_user` (obtenido del token JWT) es el administrador de ese condominio.

4.  **Acceso Concedido:** Si todas las verificaciones pasan, la función de la ruta se ejecuta, operando de forma segura dentro del contexto de su tenant.

---

Este plan de implementación detallado ahora forma parte de la documentación oficial del proyecto. Asegura que la lección aprendida durante la resolución de este complejo problema se convierta en una guía robusta para el futuro, garantizando la integridad de la arquitectura multi-tenant de CondoManager.