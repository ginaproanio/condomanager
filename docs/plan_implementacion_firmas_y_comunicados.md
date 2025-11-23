# Plan de Implementación: Módulo "Firmas & Comunicados"

Este documento detalla el estado de implementación del módulo **"Firmas & Comunicados"**. Para eliminar cualquier ambigüedad, se presenta un resumen claro del estado de cada funcionalidad principal.

## Resumen de Estado Actual

| Característica | Estado | Detalles |
| :--- | :--- | :--- |
| **Editor HTML (TinyMCE)** | ✅ **Implementado** | Editor Open Source (Costo Cero) configurado con CDNJS. |
| **Creación y Edición** | ✅ **Implementado** | Los usuarios con permisos pueden crear, editar y visualizar documentos. |
| **Control de Acceso** | ✅ **Implementado** | Modelo **Freemium** activo. Acceso básico para residentes, acceso Premium para Admin/Directiva si el condominio paga. |
| **Directiva (Roles Especiales)**| ✅ **Implementado** | Admin puede asignar Presidente/Secretario, quienes heredan permisos de firma. |
| **Recolección de Firmas** | ✅ **Implementado** | Enlaces públicos para peticiones. Descarga de Excel no implementada en UI pero modelo listo. |
| **Firma Física** | ✅ **Implementado** | Flujo completo: Descargar PDF -> Firmar manual -> Escanear -> Subir evidencia. |
| **Firma Electrónica (.p12)** | ✅ **Configurada** | Interfaz de usuario para subir certificado y validación criptográfica de contraseña implementada. |
| **Notificaciones UI** | ✅ **Implementado** | Alerta visual (Badge Rojo) en el Dashboard del usuario cuando hay documentos nuevos. |
| **Envíos WhatsApp** | 🚧 **En Progreso** | Interfaz de gestión e integración híbrida (Gateway/Meta) diseñada y codificada. Falta motor de envío. |

---

## Detalle por Fases

### **Fase 1: Fundamentos y Arquitectura (✅ Completado)**
**Objetivo:** Establecer la base segura y el flujo principal de documentos.
- ✅ **Base de Datos:** Modelos `Document`, `DocumentSignature` y `UserSpecialRole` creados y migrados.
- ✅ **Seguridad:** Decorador `@module_required` con verificación global de mantenimiento y estado del contrato.
- ✅ **Frontend:** Integración de TinyMCE (Open Source) y plantillas Jinja2 estructuradas en `app/templates/documents/`.
- ✅ **Navegación:** Integración fluida en Dashboards de Usuario y Maestro.

### **Fase 2: Lógica de Negocio y Roles (✅ Completado)**
**Objetivo:** Implementar las reglas de negocio complejas.
- ✅ **Estrategia Freemium:**
    - **Basic:** Todos ven repositorio.
    - **Premium:** Solo Admin/Directiva crean y firman.
- ✅ **Gestión de Directiva:** Interfaz para que el Administrador asigne roles como Presidente o Secretario, otorgando permisos automáticamente.

### **Fase 3: Firma Electrónica Avanzada (✅ Implementado - Configuración)**
**Objetivo:** Permitir firma legal con certificado digital.
- ✅ **Backend:** Campos en tabla `User` para almacenar `.p12`.
- ✅ **Frontend:** Nueva pantalla "Mi Perfil" donde el usuario sube su archivo `.p12` y contraseña.
- ✅ **Seguridad:** Validación criptográfica estricta al subir el archivo (verifica que la clave abra el certificado y que no esté corrupto).
- 🚧 **Uso:** Falta la integración final para estampar esta firma digitalmente en el PDF (usando `endesive`).

### **Fase 4: Comunicaciones y Notificaciones (🚧 En Progreso)**
**Objetivo:** Convertir documentos en comunicados masivos.
- ✅ **Estrategia:** Modelo Híbrido definido (Gateway QR vs Meta API).
- ✅ **Base de Datos:** Campos `whatsapp_provider` y `whatsapp_config` añadidos a `Condominium`.
- ✅ **Interfaz Admin:** Consola de "Comunicaciones" creada con selector de proveedor y configuración.
- ✅ **Interfaz Usuario:** Badge de notificación en tarjeta de documentos.
- ❌ **Motor de Envío:** Falta conectar con el servicio de mensajería real (Waha/Meta).

---

## Deuda Técnica y Mejoras Futuras
1.  **Auditoría:** Implementar tabla `AuditLog` para registrar quién borró o editó un documento.
2.  **Tests:** Crear pruebas unitarias para la lógica de permisos acumulativos (Admin + Presidente).
3.  **Motor de Firma PDF:** Completar la función que toma el `.p12` validado y firma el PDF criptográficamente.
