# Integración de Firmas Electrónicas OneShot (Nexxit/Uanataca)

Este documento describe la integración del servicio de firma electrónica OneShot (Piccolo) de Nexxit/Uanataca en CondoManager.

## Visión General

El módulo permite a usuarios que **no disponen de firma electrónica propia** (archivo .p12) firmar documentos PDF generados por el sistema utilizando un flujo "OneShot". El usuario recibe un enlace o QR, valida su identidad y estampa su firma en el documento.

## Arquitectura

La integración utiliza el **Patrón Estrategia** para permitir cambiar de proveedor en el futuro.

*   **`SignatureProvider` (Abstract Base Class):** Define la interfaz común (`create_flow`, `get_flow_details`, `download_file`).
*   **`NexxitOneshotProvider`:** Implementación concreta para la API de Nexxit V1.3.
*   **`SignatureServiceFactory`:** Se encarga de instanciar el proveedor correcto según la configuración del Condominio (Tenant).

## Configuración por Condominio

Cada condominio puede tener sus propias credenciales. Esto se almacena en la base de datos:

**Tabla:** `condominiums`
**Columna:** `signature_provider_config` (JSON)

```json
{
  "api_key": "x-nexxit-key-del-condominio",
  "provider": "NEXXIT"
}
```

> **Nota:** Existe un fallback hardcoded para el subdominio `puntablanca` si no se encuentra configuración en la base de datos.

## Flujo de Integración

### 1. Creación del Flujo (`POST /wf/flow`)

Cuando un usuario solicita firmar un documento:

1.  Se genera el PDF sin firmar en el servidor.
2.  Se convierte el PDF a Base64.
3.  Se envía una solicitud a la API de Nexxit con:
    *   `flowType`: ID de plantilla (Default: `-NXk9JhsCP7KvP9eQa_4_pb`)
    *   `userData`: Datos del firmante (Cédula, Email, Nombres).
    *   `customData`: PDF en Base64 y metadatos de posición de firma.

**Respuesta esperada:** JSON con el `id` del flujo creado. Este ID se guarda en `documents.external_flow_id`.

### 2. Verificación de Estado (`GET /wf/flow-files/{id}`)

El frontend realiza polling (o verificación manual) al endpoint interno `/documentos/{id}/verificar-uanataca`. Este a su vez consulta a Nexxit.

Estados clave:
*   `pending`: El usuario aún no firma.
*   `completed` / `signed`: El proceso ha finalizado.

### 3. Descarga de Documento Firmado (`POST /wf/file`)

Una vez que el estado es `signed`, el sistema solicita la descarga del archivo firmado usando el `path` retornado en el paso anterior.

*   El archivo se descarga y se guarda en `app/static/uploads/documents/signed/`.
*   El estado del documento en CondoManager cambia a `signed`.
*   Se crea un registro en `document_signatures` con tipo `uanataca`.

## API Reference (Nexxit V1.3)

Basado en la colección Postman `Oneshot Punta Blanca`.

### Headers
*   `x-nexxit-key`: API Key del cliente.
*   `Content-Type`: `application/json`

### Endpoints Utilizados

*   **Crear Flujo:** `POST https://wfdev.nexxit.dev/wf/flow`
*   **Consultar Flujo:** `GET https://wfdev.nexxit.dev/wf/flow-files/{flowId}`
*   **Descargar Archivo:** `POST https://wfdev.nexxit.dev/wf/file` (Body: `{"path": "ruta/remota"}`)

## Manejo de Errores

*   Si la API de Nexxit falla (Timeouts, 500), se captura la excepción y se muestra un mensaje de error al usuario.
*   Los logs de la aplicación (`current_app.logger`) registran los detalles de errores de conexión para depuración.

## Futuras Mejoras

*   Implementar Webhooks para recibir notificaciones pasivas de firma (campo `endpointNotify` en `customData`).
*   Soportar múltiples firmantes en un mismo flujo.
*   Configuración de posición de firma dinámica según el tipo de documento.

