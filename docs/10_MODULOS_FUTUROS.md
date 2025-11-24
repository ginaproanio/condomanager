# 10. Planificación de Módulos Futuros y Expansión IoT

Este documento describe la especificación funcional y técnica para los próximos módulos a desarrollar en CondoManager, enfocados en la automatización, seguridad (IoT) y comercialización de unidades.

---

## 1. Módulo de Control de Accesos y Registro de Visitas (IoT Ready)

Este módulo permitirá a los **Propietarios** autorizar el ingreso de visitas de manera anticipada, agilizando el control en garita y permitiendo la integración futura con dispositivos IoT (barreras, portones).

### Funcionalidades Clave
1.  **Pre-Registro de Visitas (App Propietario):**
    *   El propietario ingresa los datos del visitante: Nombre, Cédula (opcional), Placa del vehículo (si aplica), Fecha y Hora estimada.
    *   Generación de un **Código QR Temporal** o **Pin de Acceso** único para esa visita.
    *   Posibilidad de compartir el acceso vía WhatsApp al visitante.

2.  **Panel de Garita / Guardia (Web/Tablet):**
    *   Listado en tiempo real de "Visitas Esperadas".
    *   Escáner de QR (usando la cámara de la tablet/celular) para validar el ingreso instantáneamente.
    *   Registro manual de visitas no anunciadas (requiere llamada de confirmación al propietario).

3.  **Integración IoT (Internet of Things):**
    *   **Objetivo:** Automatizar la apertura de barreras vehiculares o puertas peatonales.
    *   **Protocolo:** Uso de controladores (ej. Raspberry Pi, ESP32) conectados a la nube de CondoManager vía MQTT o Webhooks.
    *   **Flujo:** 
        1. El visitante escanea su QR en un lector en la entrada.
        2. El lector valida con el servidor de CondoManager.
        3. Si es válido, el servidor envía la señal de "Abrir" al controlador de la barrera.

### Beneficios
*   Reducción de tiempos de espera en garita.
*   Mayor seguridad al tener trazabilidad digital de todos los ingresos.
*   Eliminación del error humano o llamadas telefónicas innecesarias.

---

## 2. Módulo de Marketplace Inmobiliario (Modelo Sindicado)

**Concepto de Negocio:** CondoManager actúa como la fuente de inventario verificado (Headless CMS). El propietario paga por publicar, y el anuncio se visualiza centralizadamente en el portal externo **ecoinmobiliaria.ec**.

### Flujo de Valor (Cerrando el Círculo)
1.  **Captura:** El propietario, desde su perfil en CondoManager, carga su propiedad para venta o arriendo (ya que el sistema ya conoce la unidad, m2, ubicación, etc., la carga es simplificada).
2.  **Monetización:** El anuncio se crea en estado `PENDING_PAYMENT`. El usuario paga una tarifa única (Pay-per-post) usando la pasarela PayPhone integrada.
3.  **Sindicación:** Una vez pagado, CondoManager expone los datos de la propiedad a través de una **API Pública (Feed JSON)**.
4.  **Visualización:** El portal externo `ecoinmobiliaria.ec` consume esta API y muestra los anuncios al público general.

### Funcionalidades Técnicas
1.  **Gestión de Anuncios (Backend CondoManager):**
    *   Modelo `MarketplaceListing`: `unit_id`, `price`, `type` (SALE/RENT), `photos` (URLs), `description`, `payment_status`, `valid_until`.
    *   Integración con módulo de Pagos para cobrar la "Tarifa de Publicación".

2.  **API de Sindicación (Feed):**
    *   Endpoint: `GET /api/v1/marketplace/feed`
    *   Seguridad: Token de API (API Key) para que solo `ecoinmobiliaria.ec` pueda consumir los datos.
    *   Payload:
        ```json
        [
          {
            "id": 123,
            "condominium_location": {"lat": -0.12, "lng": -78.45, "city": "Quito"},
            "type": "VENTA",
            "price": 150000,
            "features": {"m2": 120, "rooms": 3},
            "contact": {"whatsapp": "+59399...", "email": "propietario@..."},
            "images": ["url1.jpg", "url2.jpg"]
          }
        ]
        ```

### Beneficios del Modelo
*   **Inventario Real:** A diferencia de otros portales, aquí sabemos que la unidad existe y el usuario es realmente el propietario o administrador.
*   **Ingresos Adicionales:** Generación de cash-flow por cada publicación.
*   **Ecosistema:** Fortalece la marca `ecoinmobiliaria.ec` con oferta exclusiva.

---

## Estado de Desarrollo
Estos módulos se encuentran en fase de **Diseño y Especificación**. Su implementación requerirá:
1.  Creación de tablas en Base de Datos.
2.  Desarrollo de Endpoints API REST.
3.  Integración (en el caso del Marketplace) con el desarrollo web de `ecoinmobiliaria.ec`.
