# Reglas de Negocio
Versión: 4.0.0 (Sincronizado con Arquitectura de Módulos: Noviembre 2025)
*(Nota: Este documento refleja el estado real de la implementación.)*

## 1. Roles del Sistema

### 1.1 Perfil Maestro (MASTER)
Rol con el más alto nivel de acceso, encargado de la gestión global de la plataforma.
- ✅ **Gestión Global:** Crea condominios (Individual/Masivo), inactiva tenants y gestiona usuarios globales.
- ✅ **Catálogo de Módulos:** Puede activar/desactivar módulos a nivel global (activando flag de Mantenimiento) o por condominio.
- ✅ **Acceso Transversal:** Tiene acceso "Premium" inherente a todos los módulos para fines de supervisión y soporte, sin importar si el tenant tiene el módulo contratado.

### 1.2 Perfil Administrador (ADMIN)
Rol para gestionar un condominio específico.
- ✅ **Gestión de Usuarios:** Aprueba/Rechaza registros y gestiona roles de su condominio.
- ✅ **Gestión de la Directiva:** Puede asignar y revocar **Roles Especiales** (Presidente, Tesorero, etc.) a usuarios existentes.
- ✅ **Gestión de Unidades:** Crea y asigna unidades (implementación básica).
- ✅ **Acceso a Módulos Premium:** Tiene acceso completo a las funcionalidades de pago activas en su condominio (ej. Crear/Firmar documentos).

### 1.3 Perfil Usuario (USER - Residente/Propietario)
Usuario final del sistema.
- ✅ **Panel de Residente:** Visualiza su unidad asignada y accesos directos.
- ✅ **Acceso Freemium a Documentos:** Puede visualizar y descargar documentos públicos/enviados de su condominio sin costo adicional.
- ❌ **Restricción:** No puede crear documentos ni firmar (salvo en flujos públicos específicos o si se le otorga un Rol Especial).

### 1.4 Roles Especiales (Directiva)
Roles acumulativos asignados por el ADMIN (`UserSpecialRole`).
- ✅ **Implementación:** Modelo `UserSpecialRole` activo.
- ✅ **Permisos:** Un usuario con rol "Presidente" o "Secretario" hereda permisos "Premium" en el módulo de Documentos (puede crear y firmar), manteniendo su perfil de Usuario normal.
- ✅ **Temporalidad:** Los roles tienen fecha de inicio y fin, gestionados automáticamente.

---

## 2. Módulo "Firmas & Comunicados" (Modelo Freemium)

### 2.1 Estrategia de Acceso
- ✅ **Nivel Básico (Gratis/Incluido):**
    - Disponible para **todos** los usuarios (`USER`, `ADMIN`, `MASTER`) de un condominio activo.
    - Funcionalidad: Visualizar repositorio (`index`), descargar PDF sin firmar.
    - *Justificación:* Fomenta la transparencia y el uso de la plataforma.
- ✅ **Nivel Premium (Pago/Restringido):** Disponible para `MASTER`, `ADMIN` y `Directiva` (con Roles Especiales activos).
    - **Requisito de Acceso:** El acceso se concede si se cumplen dos condiciones:
        1. El módulo (`documents`) está `ACTIVE` en el catálogo global (tabla `Module`).
        2. Existe una entrada `ACTIVE` para ese condominio y ese módulo en la tabla `CondominiumModule`.
    - **Funcionalidad:** Crear documentos (`editor`), Editar, Firmar, Enviar.

### 2.2 Ciclo de Vida del Documento
1. **Borrador:** Creado por un usuario Premium.
2. **Firmado (Físico):** Se descarga, se firma en papel, se escanea y se sube la evidencia.
3. **Publicado:** Visible para los residentes (Nivel Básico).

### 2.3 Restricciones Técnicas
- ✅ **Mantenimiento Global:** Si el módulo está en estado `MAINTENANCE` en la tabla `Module`, nadie puede acceder a funciones Premium, mostrando un mensaje de "Mejoras en curso".
- ✅ **Validación de Tenant:** Los documentos están estrictamente aislados por `condominium_id`.

---

## 3. Jerarquía y Seguridad

### 3.1 Autenticación y Sesión
- ✅ **JWT en Cookies:** Token seguro HTTP-Only.
- ✅ **Contexto Global:** Un `context_processor` inyecta el objeto `user` en todos los templates para consistencia de UI.

### 3.2 Validación de Permisos
- ✅ **Decoradores en Cascada:**
    1. `@login_required`: Usuario autenticado.
    2. `@module_required('documents')`:
        - **Paso 1 (Global):** Verifica que el módulo no esté en mantenimiento en la tabla `Module`.
        - **Paso 2 (Tenant):** Verifica que el condominio actual (`g.condominium`) tenga una suscripción activa al módulo en la tabla `CondominiumModule`.
        - **Paso 3 (Rol):** Verifica que el `current_user` tenga un rol permitido (`MASTER`, `ADMIN` o un `UserSpecialRole` válido).

---

## 4. Auditoría y Trazabilidad
- ❌ **Logs de Actividad:** No implementado (Deuda Técnica). No hay registro histórico de quién borró o editó un documento.
