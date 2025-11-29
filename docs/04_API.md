# Documentación de Endpoints y API
Versión: 2.1.0 (Sincronizado con el código base a fecha 2025-11-22)

> **Nota**: El proyecto actualmente no cuenta con una API RESTful pública y separada. Esta documentación describe los endpoints web principales (rutas servidas con plantillas HTML) y sienta las bases para una futura API REST.

## 1. Endpoints Web Actuales (Servidos por Flask)

Estos endpoints son accedidos a través de un navegador y renderizan plantillas HTML.

### 1.1 Rutas Públicas (`public_routes.py`)
- **`GET /`**: Página de inicio o landing page.
- **`GET, POST /ingresar`**: Muestra y procesa el formulario de inicio de sesión.
- **`GET, POST /registro`**: Muestra y procesa el formulario de registro de nuevos usuarios.
- **`GET /salir`**: Cierra la sesión del usuario y elimina las cookies JWT.

### 1.2 Rutas de Usuario (`user_routes.py`)
- **`GET /dashboard`**: Panel principal para usuarios con rol `USER`.

### 1.3 Rutas de Administrador (`admin_routes.py`)
Estas rutas están protegidas por el rol `ADMIN` (o `MASTER`).
- **`GET /admin`**: **(Despachador)** Redirige al panel de gestión correcto. No renderiza una vista.
- **`GET /admin/condominio/<int:id>`**: Panel de gestión principal para un condominio específico.
- **`GET /aprobar/<int:user_id>`**: Aprueba a un usuario pendiente, cambiando su estado a `active`.
- **`GET /rechazar/<int:user_id>`**: Rechaza a un usuario pendiente.

### 1.4 Rutas Maestras (`master_routes.py`)
Estas rutas están protegidas por el rol `MASTER`.
- **`GET /master`**: Panel de control global para el super-administrador.
- **`GET /master/condominios`**: Muestra y busca condominios.
- **`POST /master/condominios/importar`**: Procesa la carga masiva de condominios.
- **`GET /master/usuarios`**: Muestra y busca usuarios.
- **`POST /master/usuarios/manage`**: Gestiona usuarios pendientes (aprobar, rechazar, etc.).
- **`GET /supervise/<int:id>`**: Vista de supervisión de solo lectura de un condominio. No existe la suplantación de roles.

---

## 2. Propuesta para Futura API RESTful

Cuando se implemente una API REST, deberá seguir las siguientes convenciones:

### 2.1 Versionado y URL Base
- **URL Base**: `/api/v1/`
- **Ejemplo**: `https://{subdomain}.dominio.com/api/v1/units`

### 2.2 Autenticación
- **Método**: Tokens JWT enviados como `Bearer Token` en el header `Authorization`.
- **Endpoint de Login**: `POST /api/auth/login`

### 2.3 Endpoints Propuestos
- **Condominios**: `GET /api/v1/condominiums`, `GET /api/v1/condominiums/<int:id>`
- **Unidades**: `GET /api/v1/units`, `POST /api/v1/units`, `GET /api/v1/units/<int:id>`
- **Usuarios**: `GET /api/v1/users`, `GET /api/v1/users/<int:id>`

### 2.4 Formato de Respuesta Estándar
```json
{
    "status": "success" | "error",
    "data": { ... } | null,
    "message": "Descripción del resultado." | "Mensaje de error."
}
```

## 3. Respuestas
### 3.1 Formato Estándar
```json
{
    "status": "success|error",
    "data": {},
    "message": "Descripción",
    "condominio": "identificador_condominio"
}
```

## 4. Ejemplos

### Actual (Punta Blanca)
```http
GET https://gestion.puntablancaecuador.com/api/v1/unidades
Authorization: Bearer {token}
X-Condominio-ID: puntablanca
```

### Formato Futuro
```http
GET https://gestion.{condominio}.com/api/v1/unidades
Authorization: Bearer {token}
X-Condominio-ID: {identificador_condominio}
```

3. `docs/11_MONITORING.md`:
<augment_code_snippet path="docs/11_MONITORING.md" mode="EDIT">
```markdown
# Monitoreo del Sistema

## 1. Logs por Condominio

### 1.1 Aplicación
```
/home/usuario/condominios/{nombre_condominio}/logs/
├── app.log
├── error.log
├── access.log
└── celery.log
```

### 1.2 Nginx
```
/var/log/nginx/
├── puntablanca_access.log
├── puntablanca_error.log
└── [nuevo_condominio]_*.log
```

## 2. Métricas
### 2.1 Sistema
- CPU por condominio
- Memoria por condominio
- Almacenamiento
- Tráfico de red

### 2.2 Aplicación
- Tiempo de respuesta
- Usuarios activos
- Errores por condominio
- Transacciones por minuto

## 3. Alertas
### 3.1 Configuración por Condominio
```yaml
alertas:
  {nombre_condominio}:
    cpu_threshold: 80
    memory_threshold: 90
    error_rate: 5
    response_time: 2000
```

## 4. Dashboard
- URL: https://monitor.{nombre_condominio}.com
- Acceso: Administradores del condominio
```

4. Actualizar `docs/CHANGELOG.md`:
<augment_code_snippet path="docs/CHANGELOG.md" mode="EDIT">
```markdown
# Changelog

## [1.1.0] - 2024-03-XX

### Añadido
- Soporte multi-condominio
- Separación de bases de datos por condominio
- Templates configurables por condominio
- Sistema de respaldos independiente
- Monitoreo específico por condominio

### Modificado
- Arquitectura para soportar múltiples instancias
- Sistema de logs separado por condominio
- Configuración de Nginx y Supervisor

### Optimizado
- Rendimiento en consultas multi-tenant
- Uso de recursos por condominio
- Sistema de caché compartido

## [1.0.0] - 2024-03-XX
[contenido anterior...]
```

5. `docs/ROADMAP.md`:
<augment_code_snippet path="docs/ROADMAP.md" mode="EDIT">
```markdown
# Roadmap

## Fase 1: MVP Multi-Condominio (Actual)
- [x] Implementación Punta Blanca
- [x] Arquitectura multi-tenant
- [x] Sistema de respaldos por condominio

## Fase 2: Escalabilidad (Q2 2024)
- [ ] Panel de administración multi-condominio
- [ ] API centralizada con routing por condominio
- [ ] Sistema de métricas unificado
- [ ] Automatización de despliegue

## Fase 3: Expansión (Q3 2024)
- [ ] Templates específicos por tipo de condominio
- [ ] Marketplace de módulos
- [ ] Sistema de facturación por condominio
- [ ] Integración con más proveedores de pago
```

Estos cambios:
1. Establecen una estructura clara para múltiples condominios
2. Documentan procesos específicos por condominio
3. Facilitan la escalabilidad futura
4. Mantienen separación de recursos y configuraciones

¿Necesitas que profundice en algún aspecto específico de estos documentos?
