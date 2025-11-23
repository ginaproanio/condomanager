# Roles y Permisos del Sistema
Versión: 1.0.0

## 1. Roles Base del Sistema

### 1.1 MAESTRO
- Gestión global de condominios
- Gestión global de usuarios (creación, asignación, aprobación)
- Supervisión de condominios en modo **solo lectura** (`/supervise/<id>`).
- Acceso de emergencia a paneles de administrador mediante **suplantación explícita** (`/impersonate/admin/<id>`).
- Activación/Desactivación de módulos contratables por condominio (ej. "Firmas & Comunicados").
- Configuración global del sistema.

### 1.2 ADMINISTRADOR
- Gestión completa de **un único condominio específico** al que está asignado (vía `tenant`).
- Acceso a su panel de gestión a través de `/admin/condominio/<id>`.
- Aprobación y rechazo de usuarios para su `tenant`.
- Creación y gestión de unidades para su condominio.
- **Módulo "Firmas & Comunicados"**: Si está activado, puede crear, firmar y enviar documentos oficiales.

### 1.3 USUARIO
- Acceso básico a unidades asignadas
- Visualización de información personal
- Interacción con servicios básicos del condominio
- **Módulo "Firmas & Comunicados"**: No tiene acceso a la gestión. Solo recibe y visualiza los documentos que le son enviados.

## 2. Roles Especiales del Condominio

### 2.1 PRESIDENTE
**Descripción**: Representante legal principal del condominio
**Permisos**:
- Acceso a reportes de gestión
- **Módulo "Firmas & Comunicados"**: Si está activado, puede crear, firmar y enviar documentos en nombre del condominio.
- Visualización de indicadores administrativos
- Supervisión de decisiones administrativas

### 2.2 SECRETARIO
**Descripción**: Encargado de documentación oficial
**Permisos**:
- Generación y gestión de actas
- Manejo de documentos oficiales
- **Módulo "Firmas & Comunicados"**: Si está activado, tiene permisos completos para gestionar documentos.
- Gestión de sesiones de asamblea

### 2.3 TESORERO
**Descripción**: Responsable de supervisión financiera
**Permisos**:
- Acceso a módulo de recaudación
- Supervisión de ingresos y gastos
- Reportes financieros

### 2.4 CONTADOR
**Descripción**: Gestión contable del condominio
**Permisos**:
- Acceso completo al módulo de contabilidad
- Gestión de asientos contables
- Generación de reportes financieros

### 2.5 VOCAL
**Descripción**: Miembro de directiva con funciones específicas
**Permisos**:
- Acceso a información general
- Participación en decisiones según asignación

## 3. Gestión de Roles Especiales

### 3.1 Asignación
- Solo el ADMINISTRADOR puede asignar roles especiales
- Un usuario puede tener múltiples roles especiales
- Los roles tienen período de vigencia definido

### 3.2 Restricciones
- Un usuario solo puede tener un rol especial activo de cada tipo por condominio
- Los roles especiales no son transferibles entre condominios
- Debe mantenerse registro histórico de asignaciones

### 3.3 Vigencia
- Fecha de inicio obligatoria
- Fecha de fin opcional
- Estado activo/inactivo para control temporal

## 4. Implementación Técnica

### 4.1 Estructura de Base de Datos
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

### 4.2 Validaciones de Seguridad
- Verificar pertenencia al condominio
- Validar autorización del administrador
- Comprobar no duplicidad de roles activos
- Validar coherencia de fechas

## 5. Flujos de Trabajo

### 5.1 Asignación de Rol Especial
1. Administrador selecciona usuario
2. Verifica roles actuales
3. Selecciona nuevo rol especial
4. Define período de vigencia
5. Confirma asignación

### 5.2 Revocación de Rol
1. Administrador selecciona asignación activa
2. Establece fecha de finalización
3. Actualiza estado a inactivo
4. Sistema registra cambio en histórico

## 6. Consideraciones Importantes

### 6.1 Usuarios con Múltiples Roles
- Un usuario puede ser USUARIO (con unidades asignadas) y tener roles especiales
- Los permisos son acumulativos
- Prioridad de acceso según rol más alto

### 6.2 Auditoría
- Registro de quién asignó cada rol
- Histórico de cambios en asignaciones
- Trazabilidad de acciones por rol

### 6.3 Marketplace y Módulos Especiales
- Roles especiales pueden tener accesos adicionales según módulos contratados
- Permisos específicos por módulo del marketplace
- Configuración flexible según necesidades del condominio

## 7. Mejores Prácticas

### 7.1 Asignación de Roles
- Documentar motivo de asignación
- Establecer períodos de vigencia claros
- Mantener actualizado el registro de directiva

### 7.2 Seguridad
- Validar permisos en cada acción
- Implementar principio de mínimo privilegio
- Revisar periódicamente asignaciones activas

### 7.3 Mantenimiento
- Limpieza periódica de roles vencidos
- Actualización de permisos según necesidades
- Documentación de cambios en estructura de roles