# Reglas de Negocio
Versión: 2.0.0 (Sincronizado con el código base actual: 2025-11-18)
*(Nota: Este documento refleja el estado actual del proyecto. El estado de implementación se indica con ✅ Implementado, 🚧 En Proceso/Parcial, ❌ Faltante/Visión a Futuro.)*

## 1. Roles del Sistema

### 1.1 Perfil Maestro (MASTER)
Rol con el más alto nivel de acceso, encargado de la gestión global de la plataforma.
- ❌ **Crear nuevos condominios:** Funcionalidad crítica no implementada en la interfaz de usuario. El modelo `Condominium` existe, pero no hay cómo crearlos desde la aplicación.
- ❌ **Asignar administradores a condominios:** No implementado, depende de la creación de condominios.
- 🚧 **Gestionar configuraciones globales:** No implementado. Existe una ruta (`/master`) pero es un placeholder.
- ✅ **Acceso a funciones de Administrador:** Un `MASTER` puede acceder a las vistas y acciones de un `ADMIN` (comprobado en `admin_routes`).

### 1.2 Perfil Administrador (ADMIN)
Rol para gestionar un condominio específico. Asignado por el Perfil Maestro.
- 🚧 **Crear unidades en su condominio:** Parcialmente implementado. Existe una ruta para **descargar** una plantilla CSV (`/master/descargar-plantilla-unidades`), pero **no existe la lógica para cargar o procesar el archivo CSV**. La creación individual tampoco está implementada.
- ✅ **Aprobar/Rechazar registros de usuarios:** Implementado en `admin_routes`. Un `ADMIN` puede aprobar o rechazar usuarios de su propio `tenant`.
- ❌ **Asignar unidades a usuarios:** No implementado. Depende de la creación de unidades.
- ❌ **Gestionar configuraciones de su condominio:** No implementado.
- ✅ **Restricción de acceso:** No puede crear condominios ni gestionar otros condominios. El acceso a las rutas de admin está protegido.

### 1.3 Perfil Usuario (USER)
Usuario final del sistema.
- ✅ **Ver su panel principal (`/dashboard`):** Implementado.
- ❌ **Actualizar su información personal:** No implementado. No existe una interfaz de perfil de usuario.
- ✅ **Acceso restringido:** No puede realizar acciones administrativas (asegurado por `jwt_required` y lógica de roles).

### 1.4 Roles Especiales de Condominio (Visión a Futuro)
Roles con permisos específicos dentro de un condominio (Presidente, Tesorero, etc.).
- 🚧 **Estructura de datos:** El modelo `UserSpecialRole` **existe** en `app/models.py`, sentando las bases para esta funcionalidad.
- ❌ **Lógica de negocio:** No hay ninguna lógica implementada para asignar, gestionar, o validar estos roles.

---

## 2. Jerarquía y Alcance

### 2.1 Perfil Maestro
- ✅ **Nivel más alto:** Confirmado por la lógica de roles en las rutas.
- ❌ **Gestión de condominios:** No implementada.

### 2.2 Perfil Administrador
- ✅ **Gestión de un condominio específico:** El `ADMIN` está asociado a un `tenant`. Las rutas de aprobación/rechazo de usuarios validan que el `ADMIN` solo pueda gestionar usuarios de su propio `tenant`.

### 2.3 Perfil Usuario
- ✅ **Acceso limitado:** Confirmado. El usuario solo ve su panel y páginas de servicios básicos.

### 2.4 Roles Especiales
- 🚧 **Modelo de datos existente:** El modelo `UserSpecialRole` está definido.
- ❌ **Lógica de asignación y permisos:** Totalmente ausente.

---

## 3. Flujos de Trabajo

### 3.1 Creación de Condominio
- ❌ **Flujo no implementado.**

### 3.2 Gestión de Unidades
- 🚧 **Paso 1: Crear unidades:** Solo descarga de plantilla CSV. Carga y procesamiento no implementados.
- ❌ **Paso 2: Asignar unidades a usuarios:** No implementado.

### 3.3 Acceso de Usuarios
1. ✅ **Registro:** Usuario se registra (`/registro`) y queda en estado `pending`.
2. ✅ **Aprobación:** Un `ADMIN` o `MASTER` puede aprobar al usuario (`/aprobar/:id`), cambiando su estado a `active`.
3. ✅ **Login:** El usuario `active` puede iniciar sesión (`/login`).

### 3.4 Asignación de Roles Especiales (Visión a Futuro)
- ❌ **Flujo no implementado.**

---

## 4. Restricciones y Validaciones

### 4.1 Nivel Maestro
- ✅ **Rol único:** La lógica en las rutas asegura que solo este rol accede a sus funciones.

### 4.2 Nivel Administrador
- ✅ **Aislamiento de Condominio (Tenant):** Las rutas de gestión de usuarios en `admin_routes` verifican que el `ADMIN` pertenezca al mismo `tenant` que el usuario que está gestionando.

### 4.3 Nivel Usuario
- ✅ **Acceso Básico:** Correctamente limitado a vistas no administrativas.

### 4.4 Roles Especiales
- ❌ **Toda la lógica de validación está ausente.**

---

## 5. Auditoría y Trazabilidad (Visión a Futuro)
- ❌ **Módulo no implementado.** No existe ninguna tabla o lógica para registrar las acciones de los usuarios.

---

## 6. Restricciones Técnicas

### 6.1 Validaciones de Seguridad
- ✅ **Validación de Rol:** Implementada a través de la lógica en cada ruta protegida.
- ✅ **Validación de Estado:** El login (`/login`) verifica que el usuario esté `active`.
- ✅ **Pertenencia a Condominio (Tenant):** Implementada en las rutas de `admin_routes` para la gestión de usuarios.

### 6.2 Integridad de Datos
- ✅ **Email de usuario único:** Validado en la ruta de registro (`/registro`).
- ❌ **Histórico de cambios:** No implementado.
