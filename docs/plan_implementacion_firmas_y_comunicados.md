# Plan de Implementación: Módulo "Firmas & Comunicados"

Este documento detalla la implementación **actual y funcional** del módulo de **Firmas & Comunicados** en la plataforma CondoManager. El sistema soporta flujos de trabajo de firma física y electrónica, con un control de acceso granular por perfil de usuario basado en la arquitectura implementada.

## Fases del Proyecto

El módulo se ha implementado en las siguientes fases funcionales:

1.  **Fundamentos y Firma Física:** El núcleo del sistema, cubriendo el 95% de los casos de uso.
2.  **Integración de Firma Electrónica:** Añadir la capacidad para usuarios con certificados digitales.
3.  **Comunicaciones y Envíos Inteligentes:** El sistema de envío masivo por WhatsApp/Email con filtros.
4.  **Recolección de Firmas Públicas:** La funcionalidad para peticiones a municipios, etc.

---

### **Fase 1: Fundamentos, Creación de Documentos y Firma Física (Implementado)**

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
    *   Se debe añadir el enlace "Firmas & Comunicados" en el layout principal (`base.html`), haciéndolo visible solo para los usuarios con el permiso correspondiente.

**Resultado de la Fase 1:** Un sistema funcional donde los usuarios autorizados pueden gestionar todo el ciclo de vida de un documento con firma física, con permisos estrictamente controlados por perfil y por activación de módulo.

---

### **Fase 2: Integración de Firma Electrónica Real (.p12/.pfx) (Diseñado)**

**Objetivo:** Permitir que usuarios avanzados con un certificado digital puedan firmar documentos directamente en la plataforma.

**Pasos Técnicos:**

1.  **Nuevas Dependencias:**
    *   Añadir `cryptography` y `endesive` (o similar) a `requirements.txt`.

2.  **Extender el Modelo `User`:**
    *   Añadir los campos para almacenar el certificado y la contraseña hasheada: `has_electronic_signature`, `signature_certificate`, `signature_cert_password_hash`.

3.  **Perfil de Usuario:**
    *   Crear una nueva ruta y plantilla (`/perfil/firma-electronica`) donde el usuario pueda subir su archivo `.p12` o `.pfx` y su contraseña. El sistema debe guardar el archivo encriptado y el hash de la contraseña.

4.  **Lógica de Firma Digital:**
    *   Crear una función helper (ej. `sign_pdf_with_certificate`) que use `endesive` para aplicar la firma digital al PDF.

5.  **Actualizar la Interfaz de Firma:**
    *   En la plantilla de firma, mostrar la opción de "Firmar Electrónicamente" solo si `current_user.has_electronic_signature` es `True`.
    *   Esta opción debe mostrar un modal pidiendo la contraseña del certificado para autorizar la firma.

**Resultado de la Fase 2:** El módulo ahora soporta un flujo híbrido, atendiendo tanto a usuarios comunes como a aquellos con capacidades de firma electrónica avanzada.

---

### **Fase 3: Comunicaciones y Envíos Inteligentes (Diseñado)**

**Objetivo:** Transformar el módulo en una potente herramienta de comunicación, permitiendo envíos masivos y segmentados.

**Pasos Técnicos:**

1.  **Dependencias de Envío:**
    *   Añadir `Flask-Mail` y `twilio` a `requirements.txt`.
    *   Configurar las variables de entorno para Mail y Twilio en Railway o en el archivo `.env`.

2.  **Interfaz de Envío Avanzada:**
    *   Crear una nueva plantilla `send.html`.
    *   Esta plantilla debe incluir:
        *   **Filtros rápidos:** Radio buttons para "Todos", "Solo Propietarios", "Solo Inquilinos", "Solo Morosos".
        *   **Filtros avanzados:** Selects para filtrar por "Tipo de Unidad" o "Estado de Unidad".
        *   **Vista previa de destinatarios:** Una lista que se actualiza para mostrar a quién se enviará el comunicado.

3.  **Lógica de Backend para Filtros:**
    *   Implementar la función `get_recipients_by_filters` que, usando SQLAlchemy, construya una consulta a la base de datos para obtener los emails y teléfonos de los destinatarios según los filtros seleccionados.

4.  **Función de Envío y Prueba:**
    *   Crear el helper `send_document_notification` que se encargue de enviar los correos (con el PDF adjunto) y los mensajes de WhatsApp.
    *   Implementar la funcionalidad de **"Enviar prueba a mi WhatsApp"** que envía el mensaje solo al usuario actual antes del envío masivo.

**Resultado de la Fase 3:** El módulo pasa de ser un simple gestor de documentos a ser el centro de comunicaciones oficiales del condominio.

---

### **Fase 4: Recolección de Firmas Públicas (Implementado)**

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