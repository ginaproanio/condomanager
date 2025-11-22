# Documentación de Diseño: /admin (Panel de Administración)

**Versión:** 1.0
**Fecha:** 22 de Noviembre de 2025

Este documento describe el diseño visual y funcional existente de la página "Panel de Administración" (`/admin`), accesible por los roles `ADMIN` y `MASTER`. El objetivo es registrar el estado actual de la interfaz.

## 1. Estructura y Layout General

La página utiliza un layout de ancho completo dentro de un contenedor (`<div class="container py-5">`). El contenido se organiza en tarjetas (`<div class="card">`) con las siguientes características:

- **Bordes**: No tienen bordes visibles (`border-0`).
- **Sombra**: Poseen una sombra sutil para darles profundidad (`shadow-sm`).
- **Fondo**: El encabezado de la tarjeta principal tiene un fondo claro (`bg-light`).

## 2. Encabezado y Estadísticas

- **Título**: "Panel de Administración", alineado a la izquierda, con un ícono de engranaje (`fas fa-cog`).
- **Insignia de Tenant**: A la derecha del título, se muestra el nombre del condominio actual (ej. "Punta Blanca") dentro de una insignia (`badge bg-primary`).

### Tarjetas de Estadísticas

Se muestra una fila con tres tarjetas de estadísticas sin borde y con colores de fondo sólidos:

| Propósito | Color Fondo (Clase) | Color Texto | Ícono (Font Awesome) |
| :--- | :--- | :--- | :--- |
| **Pendientes** | Azul (`bg-primary`) | Blanco | `fas fa-clock` |
| **Activos** | Verde (`bg-success`) | Blanco | `fas fa-check-circle` |
| **Rechazados** | Gris (`bg-secondary`) | Blanco | `fas fa-times-circle` |

## 3. Tabla de "Usuarios Pendientes de Aprobación"

Es el componente principal de la página y se presenta dentro de una tarjeta.

- **Estilo de Tabla**: Utiliza un efecto `hover` (`table-hover`) que resalta la fila sobre la que se encuentra el cursor.
- **Responsividad**: La tabla es responsiva (`table-responsive`), permitiendo el desplazamiento horizontal en pantallas pequeñas.
- **Estado "Sin Usuarios"**: Si no hay usuarios pendientes, se muestra un mensaje centrado con un ícono grande de check (`fas fa-check-circle fa-3x text-success`) y texto descriptivo.

### Componentes dentro de la Tabla

- **Insignia de Condominio**: El nombre del `tenant` del usuario se muestra dentro de una insignia de color cian con texto oscuro (`badge bg-info text-dark`).

## 4. Botones y Controles

A continuación se detallan los botones de acción de esta interfaz.

### Tabla Descriptiva de Botones

| Elemento | Clase(s) CSS | Color Fondo (Normal) | Color Texto (Normal) | Ícono (Font Awesome) | Estilos Adicionales | Ubicación y Propósito |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Aprobar** | `btn btn-success` | Verde (`#198754`) | Blanco | `fas fa-check` | Botón pequeño (`btn-sm`). | Dentro del grupo de acciones de cada fila. Aprueba el registro del usuario. |
| **Rechazar** | `btn btn-danger` | Rojo (`#dc3545`) | Blanco | `fas fa-times` | Botón pequeño (`btn-sm`). | Dentro del grupo de acciones de cada fila. Rechaza el registro del usuario. |
| **Gestionar Mi Condominio** | `btn btn-primary` | Azul (`#0d6efd`) | Blanco | `fas fa-building` | Ninguno. | En la tarjeta "Acciones Rápidas". Es un enlace para recargar el panel. |
| **Gestionar Unidades** | `btn btn-outline-primary disabled` | Transparente | Azul (`#0d6efd`) | `fas fa-building` | Deshabilitado. Borde azul. | En la tarjeta "Acciones Rápidas". Funcionalidad futura. |
| **Ver Reportes** | `btn btn-outline-primary disabled` | Transparente | Azul (`#0d6efd`) | `fas fa-chart-bar` | Deshabilitado. Borde azul. | En la tarjeta "Acciones Rápidas". Funcionalidad futura. |

### Estados de los Botones (Comportamiento Estándar de Bootstrap 5)

- **Normal**: Colores y estilos descritos en la tabla.
- **Hover (Cursor encima)**:
  - **Botones con fondo (`btn-success`, `btn-danger`, etc.)**: El color de fondo se oscurece ligeramente.
  - **Botones de contorno (`btn-outline-primary`)**: El fondo se rellena con el color del botón (ej. azul) y el texto se vuelve blanco.
- **Activo (Durante el clic)**:
  - **Botones con fondo**: El color de fondo se oscurece aún más.
- **Deshabilitado (`disabled`)**: El botón se muestra con opacidad reducida (`opacity: .65`) y el cursor cambia a `not-allowed`, impidiendo cualquier interacción.

---