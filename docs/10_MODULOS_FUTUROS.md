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

## 2. Módulo de Marketplace Inmobiliario (Venta y Arriendo)

Este módulo convierte a CondoManager en una herramienta comercial, permitiendo a los propietarios listar sus propiedades disponibles y darles visibilidad automática.

### Funcionalidades Clave
1.  **Publicación de Propiedad (Propietario/Agente):**
    *   Opción en el perfil del propietario: "Poner mi Unidad en Venta/Arriendo".
    *   Formulario de detalles: Precio, Fotos, Características (automáticas desde el registro de la unidad), Contacto.
    *   Estado: *Borrador, Pendiente de Aprobación (Admin), Publicado*.

2.  **Catálogo Público (Frontend):**
    *   Sección pública en el sitio web del condominio (ej. `mifinca.condomanager.com/propiedades`).
    *   Filtros de búsqueda (Venta, Arriendo, Precio, Habitaciones).
    *   Formulario de contacto directo con el propietario o administrador.

3.  **Gestión Administrativa:**
    *   El administrador puede aprobar o rechazar publicaciones para mantener la calidad.
    *   Posibilidad de destacar propiedades (feature freemium/premium).

4.  **Integración con Perfil Comercial:**
    *   Los agentes inmobiliarios (Perfil Comercial) pueden tener acceso a este inventario para ofrecerlo a clientes externos.

### Impacto en el Negocio
*   Valor agregado para el propietario (facilidad para monetizar su activo).
*   Posible fuente de ingresos para la administración o la plataforma (comisión o costo por publicación destacada).

---

## Estado de Desarrollo
Estos módulos se encuentran en fase de **Diseño y Especificación**. Su implementación dependerá de la hoja de ruta priorizada por la gerencia del proyecto.

