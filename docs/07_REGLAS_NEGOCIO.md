# Reglas de Negocio
Versión: 1.0.0 (Actualizado: 2025-11-18)

## 1. Roles del Sistema

### 1.1 Perfil Maestro (SUPER_ADMIN)
Rol encargado de la gestión global de condominios.
- ✅ Crear nuevos condominios (Individual y CSV - implementado en /master/condominios)
- ✅ Asignar administradores a condominios (Al crear/editar usuarios en /master/usuarios y asignar condominium_id)
- 🚧 Gestionar configuraciones globales del sistema (Interfaz de gestión pendiente en /master/configuracion)
- ❌ NO gestiona unidades dentro de los condominios

### 1.2 Perfil Administrador (ADMIN)
Rol asignado por el Perfil Maestro para gestionar un condominio específico.
- ✅ Cargar unidades en su condominio asignado (Vía importación CSV en /admin/condominio/<id>)
- 🚧 Aprobar registros de usuarios (El ADMIN de su condominio debe poder aprobar usuarios con tenant_id coincidente - pendiente)
- ✅ Asignar unidades a usuarios (Al importar usuarios de unidad vía CSV y asociar a unit_property_number)
- 🚧 Gestionar configuraciones de su condominio (Interfaz de gestión de CondominioConfig pendiente)
- ❌ NO puede crear condominios
- ❌ NO puede asignar administradores
- ❌ NO puede gestionar otros condominios

### 1.3 Perfil Usuario (UNIT_USER)
Usuario final que gestiona sus unidades asignadas.
- ✅ Ver información de sus unidades asignadas (En /dashboard)
- 🚧 Actualizar su información personal (Interfaz de perfil pendiente)
- ❌ NO puede asignar unidades
- ❌ NO puede aprobar usuarios
- ❌ NO puede crear unidades

### 1.4 Roles Especiales de Condominio

#### 1.4.1 Presidente
Rol encargado de la representación legal del condominio.
- 🚧 Acceder a reportes de gestión (Módulo de reportes pendiente)
- 🚧 Visualizar indicadores administrativos (Módulo de indicadores pendiente)
- 🚧 Supervisar decisiones administrativas (Funcionalidad pendiente)
- ❌ NO puede modificar configuraciones del sistema
- ❌ NO puede realizar operaciones contables

#### 1.4.2 Secretario
Rol responsable de la documentación oficial.
- 🚧 Generar y gestionar actas (Módulo de actas pendiente)
- 🚧 Manejar documentos oficiales (Módulo de documentos pendiente)
- 🚧 Gestionar sesiones de asamblea (Módulo de asambleas pendiente)
- ❌ NO puede modificar información financiera
- ❌ NO puede aprobar gastos

#### 1.4.3 Tesorero
Rol encargado de la supervisión financiera.
- 🚧 Acceder al módulo de recaudación (Módulo de recaudación pendiente)
- 🚧 Supervisar ingresos y gastos (Módulo financiero pendiente)
- 🚧 Ver reportes financieros (Módulo de reportes pendiente)
- ❌ NO puede modificar registros contables
- ❌ NO puede aprobar usuarios

#### 1.4.4 Contador
Rol responsable de la gestión contable.
- 🚧 Acceso completo al módulo contable (Módulo contable pendiente)
- 🚧 Gestionar asientos contables (Módulo contable pendiente)
- 🚧 Generar reportes financieros (Módulo de reportes pendiente)
- ❌ NO puede aprobar gastos
- ❌ NO puede modificar configuraciones

#### 1.4.5 Vocal
Rol con funciones específicas asignadas.
- 🚧 Acceder a información general (Funcionalidad pendiente)
- 🚧 Participar en decisiones asignadas (Funcionalidad pendiente)
- ❌ NO puede modificar configuraciones
- ❌ NO puede aprobar gastos

## 2. Jerarquía y Alcance

### 2.1 Perfil Maestro
- ✅ Nivel más alto de administración
- ✅ Gestiona la creación de condominios
- ✅ Asigna administradores a cada condominio
- ✅ No interviene en la gestión interna de los condominios

### 2.2 Perfil Administrador
- ✅ Gestiona un condominio específico
- ✅ Asignado por el Perfil Maestro
- ✅ Gestiona unidades y usuarios dentro de su condominio (Carga masiva implementada, gestión individual pendiente)
- ✅ No tiene acceso a otros condominios

### 2.3 Perfil Usuario
- ✅ Acceso limitado a sus unidades asignadas
- 🚧 Asignado por el Administrador de su condominio (La asignación existe, pero la interfaz del ADMIN para hacer esto directamente está en desarrollo)
- ✅ Solo puede ver y gestionar sus propias unidades (Ver implementado, gestionar pendiente)

### 2.4 Roles Especiales
- ❌ Asignados únicamente por el Administrador (Funcionalidad pendiente)
- ❌ Vigencia definida por período (Funcionalidad pendiente)
- ❌ Pueden coexistir con rol de Usuario (Funcionalidad pendiente)
- ❌ Limitados a un condominio específico (Funcionalidad pendiente)
- ❌ Permisos no transferibles entre condominios (Funcionalidad pendiente)

## 3. Flujos de Trabajo

### 3.1 Creación de Condominio
1. ✅ Perfil Maestro crea nuevo condominio
2. ✅ Perfil Maestro asigna administrador(es)
3. 🚧 Administrador configura el condominio (Configuraciones y funcionalidades individuales pendientes)

### 3.2 Gestión de Unidades
1. 🚧 Administrador crea unidades en su condominio (Carga masiva implementada, individual pendiente)
2. 🚧 Administrador aprueba registros de usuarios (Aprobación por ADMIN de su condominio pendiente)
3. 🚧 Administrador asigna unidades a usuarios (Al importar usuarios de unidad vía CSV y asociar a unit_property_number)

### 3.3 Acceso de Usuarios
1. ✅ Usuario se registra en el sistema
2. ✅ Estado PENDIENTE (Implementado)
3. 🚧 Administrador revisa (Interfaz y lógica de aprobación por ADMIN de su condominio pendiente)
4. 🚧 Aprueba y asigna unidad(es) (Asignación vía CSV implementada, aprobación y asignación individual por ADMIN pendiente)
5. ✅ Usuario ACTIVO (Implementado)

### 3.4 Asignación de Roles Especiales
1. ❌ Administrador identifica necesidad de rol especial (Funcionalidad pendiente)
2. ❌ Selecciona usuario calificado (Funcionalidad pendiente)
3. ❌ Define período de vigencia (Funcionalidad pendiente)
4. ❌ Asigna permisos específicos (Funcionalidad pendiente)
5. ❌ Registra en sistema (Funcionalidad pendiente)

### 3.5 Gestión de Directiva
1. ❌ Administrador registra fin de período actual (Funcionalidad pendiente)
2. ❌ Desactiva roles especiales anteriores (Funcionalidad pendiente)
3. ❌ Registra nueva directiva (Funcionalidad pendiente)
4. ❌ Asigna nuevos roles especiales (Funcionalidad pendiente)
5. ❌ Actualiza permisos y accesos (Funcionalidad pendiente)

## 4. Restricciones y Validaciones

### 4.1 Nivel Maestro
- 🚧 Solo puede existir un perfil maestro por instalación (Actualmente no hay una validación que impida crear más de uno si se fuerza la creación, pero la lógica de inicialización solo crea uno)
- ✅ Gestiona exclusivamente la creación de condominios y asignación de administradores

### 4.2 Nivel Administrador
- ✅ Solo puede gestionar el condominio asignado
- ✅ No puede acceder a la gestión de otros condominios
- ✅ Responsable de toda la gestión interna de su condominio (En proceso de implementación de herramientas)

### 4.3 Nivel Usuario
- ✅ Solo puede acceder a las unidades asignadas
- ✅ No tiene permisos de gestión administrativa
- ✅ Limitado a su propio condominio

### 4.4 Roles Especiales
- ❌ Un usuario puede tener múltiples roles especiales (Funcionalidad pendiente)
- ❌ Roles especiales requieren período de vigencia (Funcionalidad pendiente)
- ❌ No puede haber duplicidad de roles activos (Funcionalidad pendiente)
- ❌ Debe mantenerse registro histórico (Funcionalidad pendiente)

## 5. Auditoría y Trazabilidad

### 5.1 Registro de Acciones por Nivel
- ❌ Perfil Maestro: Creación de condominios y asignación de administradores (Funcionalidad pendiente)
- ❌ Perfil Administrador: Gestión de unidades y usuarios (Funcionalidad pendiente)
- ❌ Perfil Usuario: Accesos y actualizaciones de información personal (Funcionalidad pendiente)

### 5.2 Datos a Registrar
- ❌ Usuario que realiza la acción (Funcionalidad pendiente)
- ❌ Nivel de acceso utilizado (Funcionalidad pendiente)
- ❌ Fecha y hora (Funcionalidad pendiente)
- ❌ Tipo de acción (Funcionalidad pendiente)
- ❌ Detalles del cambio (Funcionalidad pendiente)

### 5.3 Auditoría de Roles Especiales
- ❌ Registro de asignación y revocación (Funcionalidad pendiente)
- ❌ Historial de cambios en permisos (Funcionalidad pendiente)
- ❌ Seguimiento de acciones por rol (Funcionalidad pendiente)
- ❌ Documentación de períodos de vigencia (Funcionalidad pendiente)

## 6. Restricciones Técnicas

### 6.1 Validaciones de Seguridad
- ✅ Verificar pertenencia al mismo condominio (En decoradores y rutas)
- ✅ Validar permisos según rol (Con decoradores)
- ✅ Verificar estados activos (En login y otras verificaciones)

### 6.2 Integridad de Datos
- 🚧 No permitir duplicados en asignaciones activas (En importación CSV, se salta si email ya existe. Para roles especiales, pendiente)
- ❌ Mantener histórico de cambios (Funcionalidad pendiente)
- ❌ Validar fechas coherentes (Funcionalidad pendiente, especialmente para roles especiales)

### 6.3 Gestión de Roles
- ❌ Validación de períodos de vigencia (Funcionalidad pendiente)
- ❌ Control de duplicidad de roles (Funcionalidad pendiente)
- ❌ Verificación de permisos heredados (Funcionalidad pendiente)
- ❌ Registro de cambios en asignaciones (Funcionalidad pendiente)

## 7. Flujos de Trabajo (Detalle)

### 7.1 Registro de Usuario
1. ✅ Usuario se registra
2. ✅ Estado PENDIENTE
3. 🚧 Administrador revisa (Interfaz y lógica de aprobación por ADMIN de su condominio pendiente)
4. 🚧 Aprueba y asigna unidad(es) (Asignación vía CSV implementada, aprobación y asignación individual por ADMIN pendiente)
5. ✅ Usuario ACTIVO

### 7.2 Asignación de Unidad
1. 🚧 Administrador selecciona usuario (Interfaz pendiente)
2. 🚧 Verifica disponibilidad de unidad (Lógica pendiente)
3. 🚧 Establece tipo de asignación (Funcionalidad pendiente)
4. ❌ Define fechas (Funcionalidad pendiente)
5. 🚧 Confirma asignación (Funcionalidad pendiente)

### 7.3 Cambio de Directiva
1. ❌ Administrador registra fin de período actual (Funcionalidad pendiente)
2. ❌ Desactiva roles especiales anteriores (Funcionalidad pendiente)
3. ❌ Registra nueva directiva (Funcionalidad pendiente)
4. ❌ Asigna nuevos roles especiales (Funcionalidad pendiente)
5. ❌ Actualiza permisos y accesos (Funcionalidad pendiente)
