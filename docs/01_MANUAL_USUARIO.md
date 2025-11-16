# Manual de Usuario
Sistema de Gestión de Condominios - v1.0.0-beta

## 1. Acceso al Sistema (MVP)

> **Implementación Inicial**: Este sistema inicia operaciones con el condominio "Punta Blanca" 
> (gestion.puntablancaecuador.com) como primer caso de uso, validando la arquitectura multi-condominio.

### 1.1 Registro y Aprobación
#### Auto-registro de Usuario de Unidad
1. Usuario accede a https://gestion.[condominio].com/registro
   ```
   Ejemplo actual en producción:
   https://gestion.puntablancaecuador.com/registro
   ```

2. Completa formulario básico:
   - Email
   - Nombre completo
   - Teléfono
   - Contraseña
   - Selección de condominio (lista desplegable)
     ```
     MVP inicial: Solo "Punta Blanca" disponible
     Preparado para: Múltiples condominios
     ```

#### Aprobación por Administrador
1. Administrador ingresa a panel de solicitudes pendientes
2. Visualiza solicitudes de su condominio
3. Acciones disponibles:
   - Aprobar y asignar:
     - Unidad(es)
     - Rol (propietario/inquilino)
   - Rechazar (indicando motivo)

### 1.2 Estados de Usuario
- Pendiente: Esperando revisión
- Activo: Aprobado con unidad(es) asignada(s)
- Rechazado: Solicitud denegada
- Inactivo: Acceso suspendido

### 1.3 Pruebas Iniciales
Para validar el sistema multi-condominio, se utilizará:
1. Punta Blanca (Producción)
   - URL: gestion.puntablancaecuador.com
   - Tipo: Lotes/Terrenos
   - Estado: Activo

2. Condominio de Prueba (Desarrollo)
   - URL: gestion.testcondominio.com
   - Tipo: Por definir
   - Estado: En implementación

### 1.4 Recuperación de Contraseña
1. Opción "Olvidé mi contraseña"
2. Ingresar email
3. Seleccionar condominio
4. Recibir contraseña temporal

### 1.5 Soporte MVP
- Email: soporte@[condominio].com
- Horario: L-V 9:00-18:00

## 2. Gestión de Unidades
### 2.1 Tipos de Unidades
- Los tipos de unidades son configurables según las necesidades específicas de cada condominio
- El administrador puede crear y gestionar los tipos de unidades necesarios
- Cada tipo puede tener sus propias características y campos personalizados

### 2.2 Listado de Unidades
- Visualización de unidades
- Filtros por tipo de unidad configurado
- Búsqueda en tiempo real:
  - Comienza a buscar desde 3 caracteres
  - Muestra hasta 20 resultados
  - Actualización automática mientras escribe
  - Resultados instantáneos con caché
- Exportar listado en múltiples formatos:
  - Excel (.xlsx)
  - CSV
  - PDF

## 3. Comunicaciones
### 3.1 WhatsApp
- Recibir notificaciones
- Responder mensajes
- Plantillas según tipo de unidad

### 3.2 Notificaciones
- Estados de cuenta
- Recordatorios de pago
- Comunicados generales
- Notificaciones específicas por tipo de unidad

## 4. Pagos
### 4.1 Realizar Pagos
- Pago con PayPhone
- Registro de transferencias
- Comprobantes

### 4.2 Historial
- Ver transacciones
- Descargar comprobantes
- Estados de cuenta

## 5. FAQ
### 5.1 Problemas Comunes
- Error de acceso
- Problemas con pagos
- Notificaciones

### 5.2 Soporte
- Contacto técnico
- Horarios de atención
- Canales de comunicación
