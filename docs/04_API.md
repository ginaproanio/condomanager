# Documentación de Endpoints y API
Versión: 3.0.0 (Sincronizado con la arquitectura "Path-Based": Noviembre 2025)

> **Nota**: El proyecto utiliza una API interna para operaciones asíncronas (como el login) y endpoints web que renderizan plantillas HTML. Esta documentación describe ambos.

## 1. Endpoints Web Actuales (Servidos por Flask)

Estas rutas son accedidas a través de un navegador y renderizan plantillas HTML. La identificación del tenant se realiza a través del primer segmento de la URL (`<tenant_slug>`).

### 1.1 Rutas Públicas (`public_routes.py`)
No requieren un `tenant_slug`.
- **`GET /`**: Página de inicio o landing page.
- **`GET /solicitar-demo`**: Formulario para solicitar una demostración.
- **`GET /salir`**: Cierra la sesión del usuario y elimina las cookies JWT.

### 1.2 Rutas de Autenticación (`auth.py`)
No requieren un `tenant_slug`.
- **`GET, POST /ingresar`**: Muestra y procesa el formulario de inicio de sesión.
- **`GET, POST /registro`**: Muestra y procesa el formulario de registro de nuevos usuarios.

### 1.3 Rutas de Tenant (Protegidas)
Estas rutas **deben** estar prefijadas con `/<tenant_slug>/`.
- **`GET /<tenant_slug>/user/dashboard`**: Panel principal para usuarios con rol `USER`.
- **`GET /<tenant_slug>/admin/panel`**: Panel de gestión principal para un condominio específico (rol `ADMIN`).
- **`GET /<tenant_slug>/admin/usuarios/roles_especiales`**: Asignación de roles de directiva.
- **`GET /<tenant_slug>/petty_cash/`**: Panel del módulo de Caja Chica.

### 1.4 Rutas Maestras (`master_routes.py`)
Protegidas por el rol `MASTER`. No requieren `tenant_slug`.
- **`GET /master`**: Panel de control global para el super-administrador.
- **`GET /master/modules`**: Catálogo global de módulos.

---

## 2. API Interna (`api_routes.py`)

Esta API se utiliza para operaciones que no recargan la página, como el login.

### 2.1 Autenticación
- **`POST /api/auth/login`**:
    - **Propósito:** Autentica al usuario y devuelve la URL de redirección correcta.
    - **Request Body:** `{"email": "...", "password": "..."}`.
    - **Lógica Clave:** El middleware `resolve_tenant` determina el contexto (`g.condominium`) a partir de la URL desde la que se llama a la API. La API usa este contexto para validar al usuario contra el tenant correcto.
    - **Response (Success):**
      ```json
      {
          "status": "success",
          "message": "Login exitoso",
          "user_role": "ADMIN",
          "redirect_url": "/algarrobos/admin/panel"
      }
      ```
    - **Cookies:** Establece una cookie `access_token_cookie` HTTP-Only con el JWT.

### 2.2 Formato de Respuesta Estándar
```json
{
    "status": "success" | "error",
    "data": { ... } | null,
    "message": "Descripción del resultado." | "Mensaje de error."
}
