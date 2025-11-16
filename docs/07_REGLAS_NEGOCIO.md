# Reglas de Negocio
Versión: 1.0.0

## 1. Roles del Sistema

### 1.1 Perfil Maestro (SUPER_ADMIN)
Rol encargado de la gestión global de condominios.
- ✅ Crear nuevos condominios
- ✅ Asignar administradores a condominios
- ✅ Gestionar configuraciones globales del sistema
- ❌ NO gestiona unidades dentro de los condominios

### 1.2 Perfil Administrador (ADMIN)
Rol asignado por el Perfil Maestro para gestionar un condominio específico.
- ✅ Crear unidades en su condominio asignado
- ✅ Aprobar registros de usuarios
- ✅ Asignar unidades a usuarios
- ✅ Gestionar configuraciones de su condominio
- ❌ NO puede crear condominios
- ❌ NO puede asignar administradores
- ❌ NO puede gestionar otros condominios

### 1.3 Perfil Usuario (UNIT_USER)
Usuario final que gestiona sus unidades asignadas.
- ✅ Ver información de sus unidades asignadas
- ✅ Actualizar su información personal
- �� NO puede asignar unidades
- ❌ NO puede aprobar usuarios
- ❌ NO puede crear unidades

### 1.4 Roles Especiales de Condominio

#### 1.4.1 Presidente
Rol encargado de la representación legal del condominio.
- ✅ Acceder a reportes de gestión
- ✅ Visualizar indicadores administrativos
- ✅ Supervisar decisiones administrativas
- ❌ NO puede modificar configuraciones del sistema
- ❌ NO puede realizar operaciones contables

#### 1.4.2 Secretario
Rol responsable de la documentación oficial.
- ✅ Generar y gestionar actas
- ✅ Manejar documentos oficiales
- ✅ Gestionar sesiones de asamblea
- ❌ NO puede modificar información financiera
- ❌ NO puede aprobar gastos

#### 1.4.3 Tesorero
Rol encargado de la supervisión financiera.
- ✅ Acceder al módulo de recaudación
- ✅ Supervisar ingresos y gastos
- ✅ Ver reportes financieros
- ❌ NO puede modificar registros contables
- ❌ NO puede aprobar usuarios

#### 1.4.4 Contador
Rol responsable de la gestión contable.
- ✅ Acceso completo al módulo contable
- ✅ Gestionar asientos contables
- ✅ Generar reportes financieros
- ❌ NO puede aprobar gastos
- ❌ NO puede modificar configuraciones

#### 1.4.5 Vocal
Rol con funciones específicas asignadas.
- ✅ Acceder a información general
- ✅ Participar en decisiones asignadas
- ❌ NO puede modificar configuraciones
- ❌ NO puede aprobar gastos

## 2. Jerarquía y Alcance

### 2.1 Perfil Maestro
- Nivel más alto de administración
- Gestiona la creación de condominios
- Asigna administradores a cada condominio
- No interviene en la gestión interna de los condominios

### 2.2 Perfil Administrador
- Gestiona un condominio específico
- Asignado por el Perfil Maestro
- Gestiona unidades y usuarios dentro de su condominio
- No tiene acceso a otros condominios

### 2.3 Perfil Usuario
- Acceso limitado a sus unidades asignadas
- Asignado por el Administrador de su condominio
- Solo puede ver y gestionar sus propias unidades

### 2.4 Roles Especiales
- Asignados únicamente por el Administrador
- Vigencia definida por período
- Pueden coexistir con rol de Usuario
- Limitados a un condominio específico
- Permisos no transferibles entre condominios

## 3. Flujos de Trabajo

### 3.1 Creación de Condominio
1. Perfil Maestro crea nuevo condominio
2. Perfil Maestro asigna administrador(es)
3. Administrador configura el condominio

### 3.2 Gestión de Unidades
1. Administrador crea unidades en su condominio
2. Administrador aprueba registros de usuarios
3. Administrador asigna unidades a usuarios

### 3.3 Acceso de Usuarios
1. Usuario se registra en el sistema
2. Administrador del condominio aprueba registro
3. Administrador asigna unidades al usuario
4. Usuario accede a gestionar sus unidades

### 3.4 Asignación de Roles Especiales
1. Administrador identifica necesidad de rol especial
2. Selecciona usuario calificado
3. Define período de vigencia
4. Asigna permisos específicos
5. Registra en sistema

### 3.5 Gestión de Directiva
1. Administrador registra nueva directiva
2. Asigna roles especiales correspondientes
3. Define períodos de gestión
4. Configura permisos específicos
5. Notifica a involucrados

## 4. Restricciones y Validaciones

### 4.1 Nivel Maestro
- Solo puede existir un perfil maestro por instalación
- Gestiona exclusivamente la creación de condominios y asignación de administradores

### 4.2 Nivel Administrador
- Solo puede gestionar el condominio asignado
- No puede acceder a la gestión de otros condominios
- Responsable de toda la gestión interna de su condominio

### 4.3 Nivel Usuario
- Solo puede acceder a las unidades asignadas
- No tiene permisos de gestión administrativa
- Limitado a su propio condominio

### 4.4 Roles Especiales
- Un usuario puede tener múltiples roles especiales
- Roles especiales requieren período de vigencia
- No puede haber duplicidad de roles activos
- Debe mantenerse registro histórico

## 5. Auditoría y Trazabilidad

### 5.1 Registro de Acciones por Nivel
- Perfil Maestro: Creación de condominios y asignación de administradores
- Perfil Administrador: Gestión de unidades y usuarios
- Perfil Usuario: Accesos y actualizaciones de información personal

### 5.2 Datos a Registrar
- Usuario que realiza la acción
- Nivel de acceso utilizado
- Fecha y hora
- Tipo de acción
- Detalles del cambio

### 5.3 Auditoría de Roles Especiales
- Registro de asignación y revocación
- Historial de cambios en permisos
- Seguimiento de acciones por rol
- Documentación de períodos de vigencia

## 6. Restricciones Técnicas

### 6.1 Validaciones de Seguridad
- Verificar pertenencia al mismo condominio
- Validar permisos según rol
- Verificar estados activos

### 6.2 Integridad de Datos
- No permitir duplicados en asignaciones activas
- Mantener histórico de cambios
- Validar fechas coherentes

### 6.3 Gestión de Roles
- Validación de períodos de vigencia
- Control de duplicidad de roles
- Verificación de permisos heredados
- Registro de cambios en asignaciones

## 7. Flujos de Trabajo

### 7.1 Registro de Usuario
1. Usuario se registra
2. Estado PENDIENTE
3. Administrador revisa
4. Aprueba y asigna unidad(es)
5. Usuario ACTIVO

### 7.2 Asignación de Unidad
1. Administrador selecciona usuario
2. Verifica disponibilidad de unidad
3. Establece tipo de asignación
4. Define fechas
5. Confirma asignación

### 7.3 Cambio de Directiva
1. Administrador registra fin de período actual
2. Desactiva roles especiales anteriores
3. Registra nueva directiva
4. Asigna nuevos roles especiales
5. Actualiza permisos y accesos
