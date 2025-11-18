# Reglas de Negocio
Versión: 1.0.0 (Actualizado: 2025-11-18)
*(Nota: Este documento es un borrador. El estado de implementación se indica con ✅ Implementado, 🚧 En Proceso/Pendiente, ❌ Faltante. Las variables y la estructura del código existente tienen prioridad.)*

## 1. Roles del Sistema

### 1.1 Perfil Maestro (SUPER_ADMIN)
Rol encargado de la gestión global de condominios.
- ✅ Crear nuevos condominios (Individual y CSV)
- ✅ Asignar administradores a condominios (al crear/editar usuarios)
- 🚧 Gestionar configuraciones globales del sistema (Ruta placeholder existente)
- ✅ NO gestiona unidades dentro de los condominios (Coherente con la implementación)

### 1.2 Perfil Administrador (ADMIN)
Rol asignado por el Perfil Maestro para gestionar un condominio específico.
- ✅ Crear unidades en su condominio asignado (Vía importación CSV. Falta individual)
- 🚧 Aprobar registros de usuarios (Actualmente gestionado por MASTER. Pendiente que ADMIN gestione *sus* usuarios)
- ✅ Asignar unidades a usuarios (Vía importación CSV. Falta individual)
- 🚧 Gestionar configuraciones de su condominio (Falta interfaz de gestión)
- ✅ NO puede crear condominios (Coherente con la implementación)
- ✅ NO puede asignar administradores (Coherente con la implementación)
- ✅ NO puede gestionar otros condominios (Asegurado por decorador)

### 1.3 Perfil Usuario (UNIT_USER)
Usuario final que gestiona sus unidades asignadas.
- ✅ Ver información de sus unidades asignadas
- 🚧 Actualizar su información personal (Falta interfaz de perfil)
- ✅ NO puede asignar unidades (Coherente con la implementación)
- ✅ NO puede aprobar usuarios (Coherente con la implementación)
- ✅ NO puede crear unidades (Coherente con la implementación)

### 1.4 Roles Especiales de Condominio
*(**❌ Faltante:** No hay modelos ni lógica implementados para roles especiales.)*

#### 1.4.1 Presidente
Rol encargado de la representación legal del condominio.
- ❌ Acceder a reportes de gestión
- ❌ Visualizar indicadores administrativos
- ❌ Supervisar decisiones administrativas
- ❌ NO puede modificar configuraciones del sistema
- ❌ NO puede realizar operaciones contables

#### 1.4.2 Secretario
Rol responsable de la documentación oficial.
- ❌ Generar y gestionar actas
- ❌ Manejar documentos oficiales
- ❌ Gestionar sesiones de asamblea
- ❌ NO puede modificar información financiera
- ❌ NO puede aprobar gastos

#### 1.4.3 Tesorero
Rol encargado de la supervisión financiera.
- ❌ Acceder al módulo de recaudación
- ❌ Supervisar ingresos y gastos
- ❌ Ver reportes financieros
- ❌ NO puede modificar registros contables
- ❌ NO puede aprobar usuarios

#### 1.4.4 Contador
Rol responsable de la gestión contable.
- ❌ Acceso completo al módulo contable
- ❌ Gestionar asientos contables
- ❌ Generar reportes financieros
- ❌ NO puede aprobar gastos
- ❌ NO puede modificar configuraciones

#### 1.4.5 Vocal
Rol con funciones específicas asignadas.
- ❌ Acceder a información general
- ❌ Participar en decisiones asignadas
- ❌ NO puede modificar configuraciones
- ❌ NO puede aprobar gastos

## 2. Jerarquía y Alcance

### 2.1 Perfil Maestro
- ✅ Nivel más alto de administración
- ✅ Gestiona la creación de condominios
- ✅ Asigna administradores a cada condominio
- ✅ No interviene en la gestión interna de los condominios

### 2.2 Perfil Administrador
- ✅ Gestiona un condominio específico (Asegurado por decorador)
- ✅ Asignado por el Perfil Maestro (A través de `condominium_id`)
- ✅ Gestiona unidades y usuarios dentro de su condominio (Vía CSV. Falta gestión individual)
- ✅ No tiene acceso a otros condominios (Asegurado por decorador)

### 2.3 Perfil Usuario
- ✅ Acceso limitado a sus unidades asignadas
- ✅ Asignado por el Administrador de su condominio (Vía `unit_id`)
- ✅ Solo puede ver y gestionar sus propias unidades (Gestión pendiente)

### 2.4 Roles Especiales
*(**❌ Faltante:** No hay modelos ni lógica implementados.)*
- ❌ Asignados únicamente por el Administrador
- ❌ Vigencia definida por período
- ❌ Pueden coexistir con rol de Usuario
- ❌ Limitados a un condominio específico
- ❌ Permisos no transferibles entre condominios

## 3. Flujos de Trabajo

### 3.1 Creación de Condominio
1. ✅ Perfil Maestro crea nuevo condominio
2. ✅ Perfil Maestro asigna administrador(es)
3. 🚧 Administrador configura el condominio (Falta interfaz)

### 3.2 Gestión de Unidades
1. ✅ Administrador crea unidades en su condominio (Vía CSV. Falta individual)
2. 🚧 Administrador aprueba registros de usuarios (Pendiente ajuste de alcance)
3. ✅ Administrador asigna unidades a usuarios (Vía CSV. Falta individual)

### 3.3 Acceso de Usuarios
1. ✅ Usuario se registra en el sistema
2. ✅ Estado PENDIENTE
3. 🚧 Administrador revisa (Actualmente lo hace MASTER. Pendiente que ADMIN gestione *sus* usuarios)
4. 🚧 Aprueba y asigna unidad(es) (Asignación vía CSV. Aprobación por MASTER. Pendiente ajuste para ADMIN)
5. ✅ Usuario ACTIVO

### 3.4 Asignación de Roles Especiales
*(**❌ Faltante:** Flujo no implementado.)*
1. ❌ Administrador identifica necesidad de rol especial
2. ❌ Selecciona usuario calificado
3. ❌ Define período de vigencia
4. ❌ Asigna permisos específicos
5. ❌ Registra en sistema

### 3.5 Gestión de Directiva
*(**❌ Faltante:** Flujo no implementado.)*
1. ❌ Administrador registra fin de período actual
2. ❌ Desactiva roles especiales anteriores
3. ❌ Registra nueva directiva
4. ❌ Asigna nuevos roles especiales
5. ❌ Actualiza permisos y accesos

## 4. Restricciones y Validaciones

### 4.1 Nivel Maestro
- 🚧 Solo puede existir un perfil maestro por instalación (Actualmente validación solo al crear en `initialize_db.py`)
- ✅ Gestiona exclusivamente la creación de condominios y asignación de administradores

### 4.2 Nivel Administrador
- ✅ Solo puede gestionar el condominio asignado (Asegurado por decorador)
- ✅ No puede acceder a la gestión de otros condominios (Asegurado por decorador)
- ✅ Responsable de toda la gestión interna de su condominio (Funcionalidades en proceso)

### 4.3 Nivel Usuario
- ✅ Solo puede acceder a las unidades asignadas
- ✅ No tiene permisos de gestión administrativa
- ✅ Limitado a su propio condominio

### 4.4 Roles Especiales
*(**❌ Faltante:** No hay modelos ni lógica implementados.)*
- ❌ Un usuario puede tener múltiples roles especiales
- ❌ Roles especiales requieren período de vigencia
- ❌ No puede haber duplicidad de roles activos
- ❌ Debe mantenerse registro histórico

## 5. Auditoría y Trazabilidad
*(**❌ Faltante:** No hay un módulo de auditoría estructurado.)*

### 5.1 Registro de Acciones por Nivel
- ❌ Perfil Maestro: Creación de condominios y asignación de administradores
- ❌ Perfil Administrador: Gestión de unidades y usuarios
- ❌ Perfil Usuario: Accesos y actualizaciones de información personal

### 5.2 Datos a Registrar
- ❌ Usuario que realiza la acción
- ❌ Nivel de acceso utilizado
- ❌ Fecha y hora
- ❌ Tipo de acción
- ❌ Detalles del cambio

### 5.3 Auditoría de Roles Especiales
- ❌ Registro de asignación y revocación
- ❌ Historial de cambios en permisos
- ❌ Seguimiento de acciones por rol
- ❌ Documentación de períodos de vigencia

## 6. Restricciones Técnicas

### 6.1 Validaciones de Seguridad
- ✅ Verificar pertenencia al mismo condominio (En decoradores y lógica de rutas)
- ✅ Validar permisos según rol (En decoradores)
- ✅ Verificar estados activos (En login y decoradores)

### 6.2 Integridad de Datos
- 🚧 No permitir duplicados en asignaciones activas (Parcialmente: Email de usuario, etc.)
- ❌ Mantener histórico de cambios
- 🚧 Validar fechas coherentes (No aplicable directamente aún a flujos implementados)

### 6.3 Gestión de Roles
- ❌ Validación de períodos de vigencia
- ❌ Control de duplicidad de roles
- ❌ Verificación de permisos heredados
- ❌ Registro de cambios en asignaciones

## 7. Flujos de Trabajo (Detalle)

### 7.1 Registro de Usuario
1. ✅ Usuario se registra
2. ✅ Estado PENDIENTE
3. 🚧 Administrador revisa (Actualmente MASTER)
4. 🚧 Aprueba y asigna unidad(es) (Aprobación por MASTER, asignación por ADMIN vía CSV)
5. ✅ Usuario ACTIVO

### 7.2 Asignación de Unidad
1. 🚧 Administrador selecciona usuario (Vía CSV. Falta interfaz individual)
2. 🚧 Verifica disponibilidad de unidad (Lógica pendiente en interfaz)
3. ❌ Establece tipo de asignación
4. ❌ Define fechas
5. 🚧 Confirma asignación (Vía CSV. Falta interfaz individual)
