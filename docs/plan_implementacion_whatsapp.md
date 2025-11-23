# Plan de Implementación: Módulo de Comunicaciones (WhatsApp Híbrido)

Este documento detalla la estrategia técnica y de negocio para la implementación del sistema de notificaciones masivas vía WhatsApp en CondoManager, utilizando un enfoque **Híbrido (Multi-Proveedor)**.

## 1. Estrategia de Negocio: El Modelo Híbrido

Para maximizar el mercado y reducir riesgos, CondoManager ofrecerá dos modalidades de conexión. Esto permite atender tanto a condominios pequeños (sensibles al precio) como a grandes corporaciones (sensibles al riesgo y la reputación).

| Característica | **Modalidad A: Gateway QR (Standard)** | **Modalidad B: Meta API Oficial (Premium)** |
| :--- | :--- | :--- |
| **Perfil de Cliente** | Pequeños/Medianos, informales, bajo presupuesto. | Grandes condominios, administradoras profesionales. |
| **Infraestructura** | El cliente usa SU propio chip/celular. | Cuenta oficial de WhatsApp Business API verificada. |
| **Costo Operativo** | **$0 / mensaje.** (Solo plan de datos del cliente). | **~$0.06 - $0.10 USD / conversación.** (Tarifa de Meta). |
| **Monetización** | Incluido en el plan base del SaaS. | Se cobra un "Add-on" mensual + Bolsa de crédito prepago. |
| **Riesgo de Bloqueo** | **ALTO** si abusan (Spam). Responsabilidad del cliente. | **NULO**. Canal oficial garantizado. |
| **Velocidad** | Lenta (1 msg cada 20 seg) para evitar bloqueos. | Inmediata (cientos de mensajes por segundo). |
| **Funcionalidad** | Texto plano e imágenes básicas. | Botones interactivos, listas, plantillas verificadas. |

---

## 2. Arquitectura Técnica Agnóstica

El sistema se diseñará con un patrón de **"Drivers" o "Adaptadores"**. El núcleo de la aplicación no sabrá qué tecnología se usa por debajo, solo enviará la orden `enviar_mensaje(destinatario, texto)`.

### 2.1 Modelo de Datos Flexible
En la tabla de configuración del condominio (`Condominium` o `CondominiumConfig`), se añadirán campos para soportar ambos modos:

*   `whatsapp_provider`: Enum (`'GATEWAY_QR'`, `'META_API'`).
*   `whatsapp_config`: Campo JSON para almacenar credenciales según el proveedor:
    *   *Gateway:* `{'session_id': 'xyz', 'status': 'connected'}`
    *   *Meta:* `{'business_id': '...', 'phone_id': '...', 'access_token': '...'}`

### 2.2 Componentes del Backend
1.  **Interface de Envío (Clase Base):** Define el método `send_message()`.
2.  **Driver Gateway:** Implementa la conexión con el contenedor de Waha (escaneo de QR).
    *   *Lógica Crítica:* Implementa una **Cola de Espera (Throttling)** obligatoria para simular comportamiento humano.
3.  **Driver Meta:** Implementa la conexión HTTP con la Graph API de Facebook.
    *   *Lógica:* Envío directo y gestión de respuestas/webhooks de estado (entregado, leído).

---

## 3. Experiencia de Usuario (UX)

### 3.1 Panel de Configuración
El Administrador verá una pantalla de selección clara:

> **Elija su método de envío:**
>
> *   **[Opción A] Conectar Teléfono Existente:** "Escanee el QR con su celular. Ideal para empezar. Tenga en cuenta que WhatsApp podría bloquear su número si envía spam."
> *   **[Opción B] Habilitar Línea Corporativa:** "Contrate una línea verificada. Sin riesgos de bloqueo. Costo adicional por mensaje."

---

## 4. Hoja de Ruta de Implementación

### ✅ Fase 1: Interfaz y Base (Completado)
*   Interfaz de gestión creada en el Panel Admin.
*   Estructura visual lista para el método QR.

### ✅ Fase 2: Backend Multi-Driver (Completado)
*   Campos `whatsapp_provider` y `whatsapp_config` (JSON) creados y migrados en DB.
*   Ruta de configuración `/configurar-whatsapp` implementada y funcional.
*   Interfaz de Admin actualizada para guardar preferencias y tokens de Meta.

### ❌ Fase 3: Integración de Proveedores (Futuro)
*   Desplegar motor Waha (Gateway).
*   Desarrollar integración real con Meta Business API.
*   Implementar la lógica de "Cola de Mensajes" (Queue) en la base de datos para el modo Gateway.

---

## 5. Recomendación Legal
Para el **Modo Gateway (QR)**, es imperativo incluir un descargo de responsabilidad (Disclaimer) visible antes de escanear el QR:
*"CondoManager provee la herramienta de automatización, pero NO se hace responsable por suspensiones de cuenta aplicadas por WhatsApp Inc. debido al uso de este servicio. Recomendamos usar un número secundario exclusivo para el condominio."*
