# Roles y Permisos del Sistema
Versión: 1.5.0 (Actualizado: Noviembre 2025)

## Filosofía de Permisos
El sistema opera bajo un modelo de permisos acumulativos. Si un usuario tiene múltiples roles (ej. `ADMIN` y `PRESIDENTE`), sus permisos son la suma de todos sus roles. El acceso a funcionalidades específicas, como los módulos, se concede si CUALQUIERA de sus roles activos se lo permite.

La directiva del condominio (compuesta por roles especiales) elige a un `ADMINISTRADOR`. Tanto el `ADMINISTRADOR` como los miembros de la directiva autorizados pueden hacer uso de los módulos contratados.

## 1. Roles Base del Sistema

### 1.1 MAESTRO
**Filosofía:** El `MASTER` es el superadministrador de la **plataforma**, no de los datos de los condominios. Su acceso a los datos de un condominio es siempre de **solo lectura y de alto nivel (métricas)**.
- **Gestión de Plataforma:** Creación y configuración global de condominios y usuarios administradores.
- **Gestión del Catálogo de Módulos:** Creación y edición de los módulos que la plataforma ofrece.
- **Supervisión de Condominios (Solo Lectura):** Acceso a un panel de supervisión (`/supervise/<id>`) con estadísticas generales (conteos de unidades, usuarios activos/pendientes) para fines de facturación y seguimiento.
- **Reportería Global:** Acceso a `/master/reports` para exportar datos agregados. **Regla Crítica:** Todas las métricas de negocio (pagos, usuarios activos, etc.) deben filtrar y excluir los condominios con `environment = 'sandbox'` o `'internal'`.
- **Limitación Crítica de Seguridad:** El rol `MASTER` **NUNCA** puede operar, navegar o ejecutar acciones dentro del panel de un `ADMIN`. El sistema está diseñado para que la suplantación de roles sea imposible. El acceso del `MASTER` a los datos de un condominio se limita estrictamente a los datos agregados y métricas del panel de supervisión.
- **Gestión del Catálogo de Módulos:**
    - **Exclusividad:** Solo el `MASTER` puede crear, editar y definir los precios de los módulos en el catálogo global del sistema (tabla `modules`).
    - **Personalización Comercial:** Puede definir condiciones específicas para cada condominio (precio especial, tipo de cobro por usuario o por módulo, períodos de prueba) a través de la tabla `CondominiumModule`.
    - **Gestión de Estado Global:** Pone un módulo en estado `MAINTENANCE` para toda la plataforma. Esto bloquea el acceso incluso si el condominio lo ha pagado, mostrando un mensaje personalizado de mantenimiento (con fecha estimada de fin).
    - **Gestión de Estado Específico:** Registra períodos de mantenimiento para un módulo en un condominio específico, dejando un historial auditable.
- **Documentos Propios:** El MASTER tiene su propio módulo de "Documentos" para gestionar contratos, términos de servicio y comunicados de la plataforma, independiente de los condominios.
- **Sandbox:** El MASTER reside en un condominio de pruebas ("Sandbox") para sus configuraciones personales. Este condominio no debe ser incluido en los reportes de negocio.

### 1.2 ADMINISTRADOR
- Gestión completa de **un único condominio específico** al que está asignado (vía `tenant` y validación de `Condominium.admin_user_id`).
- Acceso a su panel de gestión a través de `/admin/condominio/<id>`.
- **Reportería Operativa:** Acceso a `/admin/condominio/<id>/reportes` para descargar listados de **propietarios** (incluyendo datos de contacto sensibles para garita) y estados de ocupación.
- **Gestión de Comunicaciones:** Configuración exclusiva del proveedor de WhatsApp (Gateway QR o Meta API) para su condominio.
- **Gestión Financiera (Pagos, Recaudación y Caja Chica):**
    - Configuración de pasarela PayPhone para cobros automáticos.
    - Validación manual de pagos por transferencia (conciliación bancaria).
    - Gestión del módulo de **Caja Chica** (ingreso de gastos menores y reposiciones).
    - Visualización de historial de transacciones y balances.
- Aprobación y rechazo de usuarios para su `tenant`.
- Creación y gestión de unidades para su condominio.
- **Gestión de Directiva:** Es el único rol autorizado para asignar y revocar Roles Especiales (`UserSpecialRole`) a los vecinos.
- **Módulo "Firmas & Comunicados"**: Si está activado, puede crear, firmar y enviar documentos oficiales.

### 1.3 USUARIO / PROPIETARIO
- Acceso básico a unidades asignadas.
- **Historial Personal:** Acceso a `/reportes` para ver su historial de documentos firmados digitalmente y sus pagos realizados.
- Interacción con servicios básicos del condominio.
- **Pagos:** Puede realizar pagos con tarjeta (PayPhone) o subir comprobantes de transferencia.
- **Módulo "Firmas & Comunicados"**:
    - **Nivel Básico (Gratis):** Acceso de solo lectura al repositorio de documentos públicos.
    - **Nivel Premium:** No tiene acceso a la gestión/creación. Solo recibe y visualiza los documentos que le son enviados o firma peticiones públicas.
- **Módulo Marketplace (Futuro):** Podrá publicar anuncios de venta/arriendo previo pago.
- **Módulo Accesos (Futuro):** Podrá pre-registrar visitas y generar códigos QR.

### 1.4 USUARIO DEMO (Nuevo)
- **Origen:** Creado automáticamente a través de `/solicitar-demo`.
- **Rol:** `ADMIN`.
- **Condominio:** Se le asigna un condominio temporal en estado `DEMO` (ej: `demo-usuario-2023`).
- **Limitaciones:**
    - Tiene todas las capacidades de un ADMIN durante el período de prueba (15 días).
    - No puede cambiar su subdominio ni acceder a otros condominios.
    - Al expirar el período, el condominio pasa a estado `SUSPENDED` o `EXPIRED`.

## 2. Roles Especiales del Condominio

### 2.1 PRESIDENTE
**Descripción**: Representante legal principal del condominio
**Permisos**:
- Acceso a reportes de gestión
- **Módulo "Firmas & Comunicados"**: Si está activado (Premium), puede crear, firmar y enviar documentos en nombre del condominio.
- Visualización de indicadores administrativos
- Supervisión de decisiones administrativas

### 2.2 SECRETARIO
**Descripción**: Encargado de documentación oficial
**Permisos**:
- Generación y gestión de actas
- Manejo de documentos oficiales
- **Módulo "Firmas & Comunicados"**: Si está activado (Premium), tiene permisos completos para gestionar documentos.
- Gestión de sesiones de asamblea

> **Nota Importante:** El acceso de un rol especial a un módulo específico (ej. `PRESIDENTE` al módulo de firmas) está condicionado a la **vigencia de su cargo**. El sistema debe validar que la fecha actual esté dentro del `start_date` y `end_date` del rol, y que el rol esté marcado como `is_active`. Si el cargo ha expirado, el acceso al módulo se revoca automáticamente.

### 2.3 TESORERO
**Descripción**: Responsable de supervisión financiera
**Permisos**:
- Acceso a módulo de recaudación y conciliación de pagos.
- Supervisión de ingresos y gastos (Caja Chica).
- Reportes financieros.

### 2.4 CONTADOR
**Descripción**: Gestión contable del condominio
**Permisos**:
- Acceso completo al módulo de contabilidad (Futuro).
- Gestión de asientos contables
- Generación de reportes financieros formales.

### 2.5 VOCAL
**Descripción**: Miembro de directiva con funciones específicas
**Permisos**:
- Acceso a información general
- Participación en decisiones según asignación

## 3. Roles Futuros / En Análisis

### 3.1 PERFIL COMERCIAL (SALES)
**Estado:** 🚧 En Análisis (No Implementado).
**Descripción:** Rol global diseñado para agentes de ventas de la plataforma SaaS.
**Permisos Propuestos:**
- Acceso de **solo lectura** a un dashboard específico (`/sales/leads`).
- Visualización de **datos de contacto** de Directivas (Presidentes) y Administradores para gestión comercial.
- **Restricciones Críticas:**
    - NO tiene acceso a módulos operativos (Documentos, Finanzas).
    - NO puede editar ni gestionar condominios.
    - NO tiene acceso a la configuración global de la plataforma.

## 4. Gestión de Roles Especiales

### 4.1 Asignación
- **Solo el ADMINISTRADOR puede asignar roles especiales** desde su panel de gestión.
- Un usuario puede tener múltiples roles especiales (ej. ser `VOCAL` y `TESORERO` simultáneamente).
- Los roles tienen período de vigencia definido.

### 4.2 Restricciones
- Un usuario solo puede tener un rol especial activo de cada tipo por condominio.
- Los roles especiales no son transferibles entre condominios.
- Debe mantenerse registro histórico de asignaciones (tabla `user_special_roles`).

### 4.3 Vigencia
- Fecha de inicio obligatoria
- Fecha de fin opcional
- Estado activo/inactivo para control temporal

## 5. Implementación Técnica

### 5.1 Estructura de Base de Datos
```sql
-- Tabla de asignación de roles especiales
CREATE TABLE user_special_roles (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    condominium_id BIGINT NOT NULL,
    role ENUM('PRESIDENTE', 'SECRETARIO', 'TESORERO', 'CONTADOR', 'VOCAL') NOT NULL,
    asignado_por BIGINT NOT NULL,
    fecha_inicio DATE NOT NULL,
    fecha_fin DATE,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (condominium_id) REFERENCES condominiums(id),
    FOREIGN KEY (asignado_por) REFERENCES users(id),
    
    UNIQUE KEY unique_active_role_per_user_condominium (user_id, condominium_id, role, activo)
);
```

### 5.2 Validaciones de Seguridad
- Verificar pertenencia al condominio
- Validar autorización del administrador
- Comprobar no duplicidad de roles activos
- Validar coherencia de fechas

### ⚠️ NOTA CRÍTICA DE SEGURIDAD (Testing vs Producción)
En el entorno de pruebas (Railway), la validación estricta de roles por subdominio (Tenant) se ha relajado intencionalmente para permitir el login desde la URL principal.
**Para Producción:** Se debe auditar y reactivar la validación estricta en `app/tenant.py` y `app/routes/api_routes.py` para asegurar que un usuario con rol `ADMIN` o `USER` solo pueda autenticarse desde el subdominio que le corresponde (ej: `algarrobos.condomanager.com`), evitando fugas de información cruzada entre inquilinos.

## 6. Flujos de Trabajo

### 6.1 Asignación de Rol Especial
1. Administrador selecciona usuario existente en su panel.
2. Verifica roles actuales.
3. Selecciona nuevo rol especial (cargo) y fechas de vigencia.
4. Confirma asignación.

### 6.2 Revocación de Rol
1. Administrador selecciona asignación activa en la tabla de "Directiva Vigente".
2. Ejecuta la acción de revocación.
3. El sistema establece fecha de finalización a "hoy" y estado a inactivo.

## 7. Consideraciones Importantes

### 7.1 Usuarios con Múltiples Roles (Polimorfismo de Usuario)
- **Compatibilidad Total:** No existe exclusión mutua entre roles. Un mismo usuario puede acumular:
    1. **Rol Base:** Ser `ADMIN` del sistema para ese condominio.
    2. **Rol de Directiva 1:** Ser `PRESIDENTE` (vía `UserSpecialRole`).
    3. **Rol de Directiva 2:** Ser `TESORERO` (vía otra entrada en `UserSpecialRole`).
    4. **Rol de Propietario:** Tener una unidad asignada (`Unit`).
- **Permisos Acumulativos:** El sistema otorgará el "superset" de permisos. Si como `ADMIN` tiene acceso total, el hecho de ser `TESORERO` no le restará acceso, simplemente le dará atribuciones formales adicionales.
- **El Administrador-Directivo:** Es un caso de uso válido y común que el Administrador del software sea también un miembro de la directiva.

### 7.2 Auditoría
- Registro de quién asignó cada rol
- Histórico de cambios en asignaciones
- Trazabilidad de acciones por rol (ej. quién aprobó un pago manual) mediante logging estructurado con **structlog**.

### 7.3 Marketplace y Módulos Especiales
- Roles especiales pueden tener accesos adicionales según módulos contratados.
- **Estrategia Freemium:**
    - El módulo de "Documentos" tiene un nivel básico gratuito (repositorio).
    - Las funcionalidades de creación y firma son Premium.
    - El decorador `@module_required` verifica tanto el contrato del condominio como el estado global del módulo (`Module.status`).
- Permisos específicos por módulo del marketplace.
- Configuración flexible según necesidades del condominio.

## 8. Mejores Prácticas

### 8.1 Asignación de Roles
- Documentar motivo de asignación
- Establecer períodos de vigencia claros
- Mantener actualizado el registro de directiva

### 8.2 Seguridad
- Validar permisos en cada acción
- Implementar principio de mínimo privilegio
- Revisar periódicamente asignaciones activas

### 8.3 Mantenimiento
- Limpieza periódica de roles vencidos
- Actualización de permisos según necesidades
- Documentación de cambios en estructura de roles
