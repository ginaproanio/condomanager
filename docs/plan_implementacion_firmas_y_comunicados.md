# Plan de Implementación: Módulo "Firmas & Comunicados"

Este documento detalla el estado de implementación del módulo **"Firmas & Comunicados"**. Para eliminar cualquier ambigüedad, se presenta un resumen claro del estado de cada funcionalidad principal, seguido de los detalles técnicos de cada fase.

## Resumen de Estado Actual (Qué SÍ está y qué NO está)

| Característica | Estado | Implementado | Detalles |
| :--- | :--- | :--- | :--- |
| **Creación y Edición de Documentos** | ✅ **Implementado** | **SÍ** | Los usuarios autorizados pueden crear y editar documentos con un editor de texto enriquecido. |
| **Flujo de Firma Física** | ✅ **Implementado** | **SÍ** | El sistema permite descargar un PDF, firmarlo a mano, escanearlo y subirlo para registrar la firma. |
| **Control de Acceso (Módulo y Roles)** | ✅ **Implementado** | **SÍ** | El acceso está protegido por la activación del módulo en el condominio y por el rol del usuario. |
| **Recolección de Firmas Públicas** | ✅ **Implementado** | **SÍ** | Se puede generar un enlace público para que residentes o externos firmen peticiones. Incluye descarga en Excel. |
| **Nivel Básico vs Premium** | ✅ **Diseñado** | **NO** | Estrategia Freemium definida. Falta separar permisos para que todos accedan a "Documentos" (repositorio) y solo los premium a "Firmas". |
| **Firma Electrónica (.p12/.pfx)** | 🚧 **Parcialmente** | **NO** | La base de datos está lista para almacenar los certificados, pero la interfaz y la lógica para firmar no están implementadas. |
| **Envíos Inteligentes (Email/WhatsApp)** | ❌ **No Implementado** | **NO** | La funcionalidad para envíos masivos con filtros (morosos, propietarios, etc.) está diseñada pero no codificada. |

---

## Detalle por Fases del Proyecto

A continuación, se describe el estado técnico de cada fase.

1.  **Fundamentos y Firma Física:** El núcleo del sistema, cubriendo el 95% de los casos de uso.
2.  **Integración de Firma Electrónica:** Añadir la capacidad para usuarios con certificados digitales.
3.  **Comunicaciones y Envíos Inteligentes:** El sistema de envío masivo por WhatsApp/Email con filtros.
4.  **Recolección de Firmas Públicas:** La funcionalidad para peticiones a municipios, etc.

---

### **Fase 1: Fundamentos, Creación de Documentos y Firma Física (✅ Implementado)**

**Objetivo:** Permitir a los usuarios autorizados crear documentos, generar un PDF, descargarlo, firmarlo a mano, subir la versión escaneada y registrarla en el sistema.

**Pasos Técnicos:**

1.  **Actualizar Dependencias:**
    *   Se han añadido `reportlab` para la generación de PDFs y otras librerías necesarias al archivo `requirements.txt`.

2.  **Modelo de Datos (Base):**
    *   Implementar los modelos `Document` y `DocumentSignature` en `app/models.py`.
    *   Campos clave a incluir: `title`, `content`, `pdf_unsigned_path`, `pdf_signed_path`, `status`, `signature_type`, y las relaciones con `User` y `Condominium`.

3.  **Migración de Base de Datos:**
    *   Se ha ejecutado una migración única (`81ce0dfd395b_...`) que crea todas las tablas necesarias, incluyendo las de este módulo.

4.  **Control de Acceso por Perfil (Implementación Actual):**
    *   **Activación del Módulo:**
        *   El modelo `Condominium` tiene una columna booleana `has_documents_module`.
        *   El rol `MASTER` puede activar o desactivar este módulo para cada condominio a través del formulario de "Editar Condominio".
    *   **Permisos de Usuario:**
        *   Se ha creado un decorador `@module_required('documents')` en `app/decorators.py`.
        *   Este decorador se aplica a todas las rutas del módulo en `document_routes.py`.
        *   **Lógica del decorador:**
            1.  Verifica si el usuario está autenticado.
            2.  Si el usuario es `MASTER`, le concede acceso inmediato.
            3.  Si no es `MASTER`, busca el condominio del usuario y comprueba si el flag `has_documents_module` es `True`.
            4.  Si el módulo no está activo para el condominio, deniega el acceso.

5.  **Crear el Blueprint y Rutas Esenciales:**
    *   Crear el archivo `app/routes/document_routes.py`.
    *   Se han implementado todas las rutas necesarias para el CRUD de documentos (`/`, `/nuevo`, `/<id>/editar`, `/<id>`).

6.  **Interfaz de Usuario (Templates):**
    *   Integrar el editor **TinyMCE** en la plantilla de creación/edición para una experiencia de edición de texto enriquecida.
    *   Se han desarrollado las plantillas `index.html`, `editor.html`, `view.html` y `sign_options.html` dentro de `app/templates/services/`.
    *   La plantilla `sign_options.html` implementa el flujo de firma física:
        1.  **Botón "Descargar para firmar"**: Enlaza a una ruta que genera y sirve el `pdf_unsigned_path`.
        2.  **Botón "Subir documento firmado"**: Abre un modal con un formulario para subir el PDF escaneado, que se guardará en `pdf_signed_path` y cambiará el estado del documento a `signed`.

7.  **Integración al Menú Principal:**
    *   **⚠️ Pendiente:** Se debe añadir el enlace "Firmas & Comunicados" en el layout principal (`base.html`), haciéndolo visible solo para los usuarios con el permiso correspondiente.

**Resultado de la Fase 1:** Un sistema funcional donde los usuarios autorizados pueden gestionar todo el ciclo de vida de un documento con firma física, con permisos estrictamente controlados por perfil y por activación de módulo.

---

### **Fase 2: Integración de Firma Electrónica Real (.p12/.pfx) (🚧 Parcialmente Implementado)**

**Objetivo:** Permitir que usuarios avanzados con un certificado digital puedan firmar documentos directamente en la plataforma.

**Pasos Técnicos:**

1.  **✅ (SÍ) Extender el Modelo `User`:**
    *   Se han añadido a `app/models.py` los campos para almacenar el certificado y la contraseña hasheada: `has_electronic_signature`, `signature_certificate`, `signature_cert_password_hash`. La base de datos está lista.

1.  **Nuevas Dependencias:**
    *   Añadir `cryptography` y `endesive` (o similar) a `requirements.txt`.

2.  **Extender el Modelo `User`:**
    *   Añadir los campos para almacenar el certificado y la contraseña hasheada: `has_electronic_signature`, `signature_certificate`, `signature_cert_password_hash`.

3.  **Perfil de Usuario:**
    *   **❌ (NO)** Falta por crear la ruta y la plantilla (`/perfil/firma-electronica`) donde el usuario pueda subir su archivo `.p12` o `.pfx` y su contraseña.

4.  **Lógica de Firma Digital:**
    *   **❌ (NO)** Falta por crear la función helper (ej. `sign_pdf_with_certificate`) que use `endesive` para aplicar la firma digital al PDF.

5.  **Actualizar la Interfaz de Firma:**
    *   **❌ (NO)** Falta por modificar la plantilla de firma para que muestre la opción "Firmar Electrónicamente" y el modal que solicita la contraseña del certificado.

**Resultado de la Fase 2:** La base de datos está preparada, pero la funcionalidad no es usable por el usuario final.

---

### **Fase 3: Comunicaciones y Envíos Inteligentes (❌ No Implementado)**

**Objetivo:** Transformar el módulo en una potente herramienta de comunicación, permitiendo envíos masivos y segmentados.

**Pasos Técnicos:**

1.  **Dependencias de Envío:**
    *   Añadir `Flask-Mail` y `twilio` a `requirements.txt`.
    *   Configurar las variables de entorno para Mail y Twilio en Railway o en el archivo `.env`.

2.  **Interfaz de Envío Avanzada:**
    *   **❌ (NO)** Falta por crear la plantilla `send.html` que incluya:
        *   **Filtros rápidos:** Radio buttons para "Todos", "Solo Propietarios", "Solo Inquilinos", "Solo Morosos".
        *   **Filtros avanzados:** Selects para filtrar por "Tipo de Unidad" o "Estado de Unidad".
        *   **Vista previa de destinatarios:** Una lista que se actualiza para mostrar a quién se enviará el comunicado.

3.  **Lógica de Backend para Filtros:**
    *   **❌ (NO)** Falta por implementar la función `get_recipients_by_filters` que consulte la base de datos para obtener los destinatarios.

4.  **Función de Envío y Prueba:**
    *   **❌ (NO)** Falta por crear el helper `send_document_notification` para enviar los mensajes y la funcionalidad de **"Enviar prueba a mi WhatsApp"**.

**Resultado de la Fase 3:** Esta funcionalidad está completamente en fase de diseño. No hay código implementado.

---

### **Fase 4: Recolección de Firmas Públicas (✅ Implementado)**

**Objetivo:** Añadir la capacidad de usar la plataforma para recolectar firmas de residentes para causas comunes (ej. peticiones al municipio).

**Pasos Técnicos:**

1.  **Extender Modelo `Document`:**
    *   Añadir los campos `collect_signatures_from_residents`, `public_signature_link`, y `signature_count`.

2.  **Nuevo Modelo `ResidentSignature`:**
    *   Crear este modelo para almacenar las firmas públicas (nombre, cédula, etc.), desvinculadas de los usuarios del sistema.

3.  **Rutas y Plantillas Públicas:**
    *   Crear una ruta pública (`/firmar/<public_link>`) que no requiera login.
    *   Diseñar una plantilla simple y adaptable a móviles para que cualquier persona con el enlace pueda registrar su firma.

4.  **Funcionalidad Adicional:**
    *   En la vista de creación/edición del documento, añadir el checkbox para "Activar recolección de firmas".
    *   En la vista del documento para el administrador, mostrar el contador de firmas y un botón para **"Descargar Firmas en Excel"**, que generará y servirá un archivo CSV o XLSX con los datos recolectados.

**Resultado de la Fase 4:** El sistema ahora también sirve como una herramienta de participación comunitaria, útil para organizar y validar el apoyo de los residentes en iniciativas externas.
