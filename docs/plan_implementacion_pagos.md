# Plan de Implementación: Módulo de Pagos (PayPhone)

## 1. Filosofía de Recaudación (Multi-Merchant)
El sistema opera como una **Plataforma SaaS** donde cada Condominio actúa como un **Comercio Independiente**.
- **SaaS (Plataforma):** Provee la tecnología. NO toca el dinero de las alícuotas.
- **Condominio (Cliente):** Cobra directamente a sus residentes. El dinero va de la tarjeta del residente a la cuenta PayPhone del Condominio.
- **Administrador:** Es el responsable de configurar las credenciales de su pasarela (PayPhone) y gestionar la recaudación.

## 2. Arquitectura de Datos

### 2.1 Modelo `Condominium` (Configuración)
Se han añadido campos para descentralizar el cobro:
- `payment_provider`: 'PAYPHONE' (Default).
- `payment_config`: JSON que almacena `{ "token": "...", "client_id": "...", "secret": "..." }`.

### 2.2 Modelo `Payment` (Transacción)
Registra cada intento de pago vinculado a un usuario, una unidad y un condominio.

## 3. Roles y Flujos de Aprobación

### 3.1 Pagos Automáticos (PayPhone)
1. **Residente:** Inicia el pago desde su panel.
2. **Sistema:** Usa las credenciales del condominio para procesar el cobro.
3. **Pasarela:** Valida fondos y confirma transacción.
4. **Sistema:** Registra el pago como `APPROVED` automáticamente.
5. **Notificación:** Se alerta al Admin y Tesorero del ingreso.
   * *Nota: Al ser dinero ya ingresado en el banco, no requiere aprobación manual, solo conciliación.*

### 3.2 Pagos Manuales (Transferencia / Efectivo)
1. **Residente:** Sube comprobante de transferencia.
2. **Estado:** El pago entra como `PENDING_REVIEW`.
3. **Aprobación:**
   - **Nivel 1:** El **ADMINISTRADOR** verifica que el dinero esté en el banco y marca "Verificado".
   - **Nivel 2 (Opcional):** Si existe **CONTADOR** o **TESORERO** activo, pueden requerir un segundo clic de "Conciliado" para cerrar el ciclo contable.
   - *Si no hay directiva, el Admin tiene potestad total.*

## 4. Roadmap de Implementación

### Fase 1: Configuración (Admin)
- [x] Actualizar Modelo `Condominium` y Migración DB.
- [x] Crear vista `/admin/configuracion/pagos`: Formulario para ingresar ID y Token de PayPhone.
- [ ] Validar credenciales con una llamada de prueba a PayPhone.

### Fase 2: Botón de Pago (Usuario)
- [x] Crear Modelo `Payment` y Migración DB.
- [x] Implementar Helper `PayPhoneService` que lea las credenciales dinámicamente del objeto `current_user.unit.condominium`.
- [x] Vista `/pagos`: Mostrar deuda (mockup inicial) y botón "Pagar con PayPhone".

### Fase 3: Callbacks y Seguridad
- [ ] Endpoint de retorno para actualizar estado del pago. (Parcialmente implementado en `payment_routes.py`)
- [ ] Protección CSRF en botones de pago.

### Fase 4: Reportes
- [x] Admin: Listado de recaudación diaria (Implementado tabla de historial en `/admin/configuracion/pagos` y `/admin/reportes`).
- [x] User: Historial personal de pagos en `/reportes`.
- [ ] Master: Métricas de volumen transaccional global (anonimizado).

### Fase 5: Pagos Manuales (Pendiente)
- [ ] Formulario para subir comprobante de transferencia (imagen/pdf).
- [ ] Vista de Admin para conciliar pagos manuales.

## 5. Credenciales de Prueba (SORSABSA)
Se utilizarán las credenciales provistas para simular el condominio "Algarrobos" durante el desarrollo.
