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
| **Firma Electrónica (.p12)** | 🚧 **Base Lista** | Base de datos lista. Falta interfaz de carga de certificado y lógica de firma criptográfica. |
| **Envíos Inteligentes** | ❌ **Pendiente** | No hay integración con WhatsApp/Email masivo. |

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

### **Fase 3: Firma Electrónica Avanzada (🚧 En Progreso)**
**Objetivo:** Permitir firma legal con certificado digital.
- ✅ **Backend:** Campos en tabla `User` para almacenar `.p12`.
- ❌ **Frontend:** Interfaz para subir certificado y contraseña.
- ❌ **Lógica:** Integración con librería `endesive` para firma criptográfica de PDFs.

### **Fase 4: Comunicaciones y Notificaciones (❌ Pendiente)**
**Objetivo:** Convertir documentos en comunicados masivos.
- ❌ **Envíos:** Integración con Twilio (WhatsApp) y SMTP (Email).
- ❌ **Filtros:** Lógica para seleccionar destinatarios (Solo Morosos, Solo Propietarios).

---

## Deuda Técnica y Mejoras Futuras
1.  **Auditoría:** Implementar tabla `AuditLog` para registrar quién borró o editó un documento.
2.  **Tests:** Crear pruebas unitarias para la lógica de permisos acumulativos (Admin + Presidente).
3.  **Validación de Archivos:** Mejorar seguridad en la subida de PDFs firmados (validar mime-types estrictamente).
