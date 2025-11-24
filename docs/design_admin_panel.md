# Documentación de Diseño: /admin (Panel de Administración)

**Versión:** 1.1
**Fecha:** 24 de Noviembre de 2025

Este documento describe el diseño visual y funcional existente de la página "Panel de Administración" (`/admin`), accesible por los roles `ADMIN` y `MASTER`. El objetivo es registrar el estado actual de la interfaz.

## 1. Estructura y Layout General

La página utiliza un layout de ancho completo dentro de un contenedor (`<div class="container py-5">`). El contenido se organiza en tarjetas (`<div class="card">`) con las siguientes características:

- **Bordes**: No tienen bordes visibles (`border-0`).
- **Sombra**: Poseen una sombra sutil para darles profundidad (`shadow-sm`).
- **Fondo**: El encabezado de la tarjeta principal tiene un fondo claro (`bg-light`) o blanco si se usa el estilo limpio.

## 2. Encabezado y Navegación

### 2.1 Botón "Volver" (Estándar)
Para mantener la consistencia en toda la plataforma (Master y Admin), el botón de retorno debe seguir estas reglas:

*   **Ubicación:** Esquina superior izquierda del área de contenido principal (dentro del `card-body` o contenedor principal).
*   **Estilo:** `btn btn-outline-secondary`.
*   **Icono:** Flecha izquierda (`fas fa-arrow-left me-2`).
*   **Texto:** "Volver" o "Volver a [Destino]".

**Ejemplo de Implementación:**
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

### 2.2 Títulos de Sección
*   Deben usar `text-primary` sobre fondo blanco para máxima legibilidad.
*   Evitar `card-header` con colores sólidos oscuros (`bg-primary text-white`) si no es estrictamente necesario, prefiriendo un diseño limpio y minimalista.

## 3. Estadísticas y Tarjetas Informativas

Se muestra una fila con tres tarjetas de estadísticas sin borde y con colores de fondo sólidos:

| Propósito | Color Fondo (Clase) | Color Texto | Ícono (Font Awesome) |
| :--- | :--- | :--- | :--- |
| **Pendientes** | Azul (`bg-primary`) | Blanco | `fas fa-clock` |
| **Activos** | Verde (`bg-success`) | Blanco | `fas fa-check-circle` |
| **Rechazados** | Gris (`bg-secondary`) | Blanco | `fas fa-times-circle` |

## 4. Tabla de Usuarios y Listados

Es el componente principal de la página y se presenta dentro de una tarjeta.

- **Estilo de Tabla**: Utiliza un efecto `hover` (`table-hover`) que resalta la fila sobre la que se encuentra el cursor.
- **Responsividad**: La tabla es responsiva (`table-responsive`), permitiendo el desplazamiento horizontal en pantallas pequeñas.
- **Estado "Sin Datos"**: Si no hay registros, se muestra un mensaje centrado con un ícono grande y texto descriptivo.

## 5. Botones y Controles

A continuación se detallan los botones de acción de esta interfaz.

### Tabla Descriptiva de Botones

| Elemento | Clase(s) CSS | Color Fondo (Normal) | Color Texto (Normal) | Ícono (Font Awesome) | Estilos Adicionales | Ubicación y Propósito |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Aprobar** | `btn btn-success` | Verde (`#198754`) | Blanco | `fas fa-check` | Botón pequeño (`btn-sm`). | Dentro del grupo de acciones de cada fila. Aprueba el registro del usuario. |
| **Rechazar** | `btn btn-danger` | Rojo (`#dc3545`) | Blanco | `fas fa-times` | Botón pequeño (`btn-sm`). | Dentro del grupo de acciones de cada fila. Rechaza el registro del usuario. |
| **Gestionar** | `btn btn-info` | Cian (`#0dcaf0`) | Negro | `fas fa-edit` | Botón pequeño (`btn-sm`). | Editar o gestionar un recurso. |
| **Eliminar** | `btn btn-danger` | Rojo (`#dc3545`) | Blanco | `fas fa-trash` | Botón pequeño (`btn-sm`). | Eliminar un recurso (siempre con confirmación). |

### Estados de los Botones (Comportamiento Estándar de Bootstrap 5)

- **Normal**: Colores y estilos descritos en la tabla.
- **Hover (Cursor encima)**:
  - **Botones con fondo (`btn-success`, `btn-danger`, etc.)**: El color de fondo se oscurece ligeramente.
  - **Botones de contorno (`btn-outline-primary`)**: El fondo se rellena con el color del botón (ej. azul) y el texto se vuelve blanco.
- **Activo (Durante el clic)**:
  - **Botones con fondo**: El color de fondo se oscurece aún más.
- **Deshabilitado (`disabled`)**: El botón se muestra con opacidad reducida (`opacity: .65`) y el cursor cambia a `not-allowed`, impidiendo cualquier interacción.

---
