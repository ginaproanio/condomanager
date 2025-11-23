# Manual de Usuario
Sistema de Gestión de Condominios - v2.1.0

## 1. Acceso al Sistema (MVP)

> **Arquitectura Multi-Condominio**: El sistema está diseñado para dar servicio a múltiples condominios, cada uno con su propio subdominio de gestión.

### 1.1 Registro y Aprobación
#### Auto-registro de Usuario de Unidad
1. Usuario accede a https://gestion.[condominio].com/registro
   ```
   Ejemplo actual en producción:
   https://gestion.puntablancaecuador.com/registro
   https://gestion.[subdominio-del-condominio].com/registro
   ```

2. Completa formulario básico:
   - Email
   - Nombre completo
   - Contraseña

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
