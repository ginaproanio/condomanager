# SISTEMA DE DISEÑO Y GUÍA DE ESTILOS – CondoManager SaaS

**Versión:** 2.0
**Fecha:** 24 de Noviembre de 2025
**Estado:** VIGENTE

Este documento establece las directrices oficiales de diseño visual, componentes y accesibilidad para toda la plataforma CondoManager (Frontend Público, Panel de Usuario, Panel Admin y Panel Master).

## 1. Principios Fundamentales

1.  **Legibilidad Primero:** Todo texto y elemento interactivo debe tener suficiente contraste con su fondo. "Botones blancos sobre fondo blanco" son inaceptables.
2.  **Consistencia:** Un botón de "Volver" debe verse y ubicarse igual en todas las pantallas.
3.  **Resiliencia:** El diseño no debe romperse si falta una configuración (ej. color primario del tenant no definido).

## 2. Paleta de Colores y Temas

El sistema es Multi-Tenant y permite personalizar el color primario. Sin embargo, el diseño base debe ser robusto.

### 2.1 Variables CSS (Globales)
Definidas en `base.html`.

*   `--primary`: Color principal de la marca del condominio.
    *   **REGLA CRÍTICA:** Nunca debe ser `None`, vacío o invisible.
    *   **Fallback:** Si la configuración del tenant falla o no existe, debe usarse `#2c5aa0` (Azul Corporativo).
    *   **Implementación Segura:** `{{ config.primary_color if config and config.primary_color else '#2c5aa0' }}`
*   `--secondary`: `#1e3a8a` (Azul Oscuro) - Usado para contrastes y fondos secundarios.
*   `--accent`: `#f59e0b` (Naranja) - Usado para alertas o llamadas a la acción secundarias.
*   `--light`: `#f8fafc` (Gris muy claro) - Fondos de página.
*   `--dark`: `#1e293b` (Gris oscuro azulado) - Texto principal.

## 3. Componentes: Botones

### 3.1 Reglas de Contraste
*   **PROHIBIDO:** Usar botones con texto claro sobre fondo claro.
*   **PROHIBIDO:** Usar botones "Outline" (ej. `btn-outline-white` o `btn-outline-light`) sobre fondos blancos.
*   **PRECAUCIÓN:** Al usar `btn-outline-primary`, asegurar que el color primario no sea demasiado claro (amarillo, blanco, cian pálido). Si hay duda, preferir botones sólidos (`btn-primary`).

### 3.2 Estilos Estándar

| Acción | Clase Bootstrap | Apariencia | Uso |
| :--- | :--- | :--- | :--- |
| **Acción Principal** | `btn btn-primary` | Fondo Sólido (Color Tenant) | Guardar, Enviar, Confirmar, Crear Nuevo. |
| **Acción Secundaria** | `btn btn-secondary` | Fondo Gris Sólido | Cancelar, Cerrar Modal. |
| **Volver / Atrás** | `btn btn-outline-secondary` | Borde Gris, Fondo Transparente | Navegación jerárquica (ver sección 4.1). |
| **Acción Positiva** | `btn btn-success` | Fondo Verde | Aprobar, Activar, Pagar. |
| **Acción Destructiva** | `btn btn-danger` | Fondo Rojo | Eliminar, Rechazar, Salir. |
| **Informativo/Editar**| `btn btn-info text-white` | Fondo Cian + **Texto Blanco** | Editar, Ver Detalles. **Nota:** Siempre añadir `text-white` para contraste. |

## 4. Navegación y Layouts

### 4.1 Botón "Volver" (Estándar)
Para mantener la consistencia en toda la plataforma (Master y Admin), el botón de retorno debe seguir estas reglas:

*   **Ubicación:** Esquina superior izquierda del área de contenido principal (dentro del `card-body` o contenedor principal).
*   **Estilo:** `btn btn-outline-secondary`.
*   **Icono:** Flecha izquierda (`fas fa-arrow-left me-2`).
*   **Texto:** "Volver" o "Volver a [Destino]".

**Ejemplo de Implementación (FLEXBOX):**
```html
<div class="d-flex justify-content-between align-items-center mb-4">
    <a href="{{ url_for('ruta_destino') }}" class="btn btn-outline-secondary">
        <i class="fas fa-arrow-left me-2"></i>Volver
    </a>
    <h2 class="text-primary mb-0 text-center flex-grow-1">
        <!-- Título de la Página -->
    </h2>
    <div style="width: 100px;"></div> <!-- Espaciador para centrar el título -->
</div>
```

### 4.2 Encabezados de Página
*   **Color:** `text-primary`.
*   **Fondo:** Preferiblemente blanco o gris muy claro (`bg-light`).
*   **Evitar:** `card-header` con fondo sólido oscuro (`bg-primary text-white`) a menos que sea un panel de datos muy denso. El diseño limpio es preferible.

## 5. Formularios

*   **Etiquetas (`labels`):** Siempre visibles, color oscuro.
*   **Inputs:** Bordes estándar de Bootstrap.
*   **Botones de Formulario:**
    *   Derecha inferior o ancho completo (móvil).
    *   Orden: [Cancelar] [Guardar].
    *   "Cancelar" debe ser visualmente menos prominente (`btn-secondary` o `btn-link`).
    *   "Guardar" debe ser la acción visualmente dominante (`btn-primary` o `btn-success`).

## 6. Accesibilidad

*   **Textos sobre imágenes:** Usar sombra de texto o fondo semitransparente.
*   **Iconos:** Siempre acompañados de `aria-label` o texto visible, o marcados como decorativos.
*   **Validación:** Los errores de formulario deben mostrarse en rojo (`text-danger`) y explicar claramente el problema.

---
**Nota Técnica:** Cualquier cambio en este documento debe reflejarse inmediatamente en `app/templates/base.html` y los componentes reutilizables.

