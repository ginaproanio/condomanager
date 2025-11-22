# Documentación de Diseño: /master/condominios

**Versión:** 1.0
**Fecha:** 22 de Noviembre de 2025

Este documento describe el diseño visual y funcional existente de la página de "Gestión de Condominios" para el rol de `MASTER`. El objetivo es registrar el estado actual de la interfaz sin proponer cambios.

## 1. Estructura y Layout General

La página utiliza un layout centrado dentro de un contenedor principal. El contenido principal se presenta dentro de una tarjeta grande (`<div class="card">`) que tiene las siguientes características:

- **Bordes**: No tiene bordes visibles (`border-0`).
- **Sombra**: Posee una sombra prominente para darle profundidad y separarla del fondo (`shadow-lg`).
- **Padding**: El contenido dentro de la tarjeta tiene un padding amplio (`p-5`).

## 2. Encabezado

- **Título**: "Gestión de Condominios", centrado, con un ícono de edificio (`fas fa-building`).
- **Subtítulo**: "Panel de control para crear y administrar condominios.", en un tono de texto más claro (`text-muted`).

## 3. Botones y Controles

A continuación se detallan los botones principales y sus estilos actuales, basados en las clases de Bootstrap 5.

### Tabla Descriptiva de Botones

| Elemento | Clase(s) CSS | Color Fondo (Normal) | Color Texto (Normal) | Ícono (Font Awesome) | Estilos Adicionales | Ubicación y Propósito |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Crear Nuevo Condominio** | `btn btn-success` | Verde (`#198754`) | Blanco | `fas fa-plus-circle` | Ninguno | Esquina superior derecha. Lleva al formulario de creación. |
| **Buscar** | `btn btn-outline-primary` | Transparente | Azul (`#0d6efd`) | `fas fa-search` | Borde azul. | Parte del campo de búsqueda. Ejecuta la consulta. |
| **Limpiar Búsqueda** | `btn btn-outline-secondary` | Transparente | Gris (`#6c757d`) | `fas fa-times` | Borde gris. | Aparece solo si hay una búsqueda activa. Limpia el filtro. |
| **Editar (en tabla)** | `btn btn-info` | Cian (`#0dcaf0`) | Blanco/Negro | `fas fa-edit` | Botón pequeño (`btn-sm`). | Dentro del grupo de acciones de cada fila. Edita el condominio. |
| **Inactivar (en tabla)** | `btn btn-danger` | Rojo (`#dc3545`) | Blanco | `fas fa-power-off` | Botón pequeño (`btn-sm`). | Dentro de un formulario. Inactiva el condominio (con `confirm`). |
| **Importar CSV** | `btn btn-info` | Cian (`#0dcaf0`) | Blanco/Negro | `fas fa-upload` | Ninguno | Dentro de la pestaña de importación. Envía el formulario del CSV. |
| **Volver al Panel Maestro** | `btn btn-secondary` | Gris (`#6c757d`) | Blanco | `fas fa-arrow-left` | Ninguno | Al final de la página. Regresa a la vista principal del panel maestro. |

### Estados de los Botones (Comportamiento Estándar de Bootstrap 5)

- **Normal**: Colores y estilos descritos en la tabla.
- **Hover (Cursor encima)**:
  - **Botones con fondo (`btn-success`, `btn-danger`, etc.)**: El color de fondo se oscurece ligeramente.
  - **Botones de contorno (`btn-outline-primary`)**: El fondo se rellena con el color del botón (ej. azul) y el texto se vuelve blanco.
- **Activo (Durante el clic)**:
  - **Botones con fondo**: El color de fondo se oscurece aún más.
  - **Botones de contorno**: El fondo se oscurece más que en el estado hover.
- **Deshabilitado (`disabled`)**: El botón se muestra con opacidad reducida y no reacciona a los clics. (No hay botones deshabilitados por defecto en esta vista).

## 4. Pestañas de Navegación

La interfaz utiliza un sistema de pestañas (`nav-tabs`) para separar la lista de condominios de la funcionalidad de importación.

- **Pestaña Activa**: Tiene un borde que la conecta con el panel de contenido y el texto es más prominente.
- **Pestaña Inactiva**: El texto es de color azul (enlace) y no tiene conexión visual con el panel de contenido.

Las pestañas son:
1.  **Listar Condominios** (activa por defecto).
2.  **Importar CSV**.

## 5. Pestaña "Listar Condominios"

### Tabla de Condominios

- **Estilo**: La tabla tiene un efecto `hover` (`table-hover`), que resalta la fila sobre la que se encuentra el cursor.
- **Responsividad**: La tabla es responsiva (`table-responsive`), permitiendo el desplazamiento horizontal en pantallas pequeñas.
- **Nombre del Condominio**: Es un hipervínculo que redirige al panel de administración de ese condominio específico (`admin.admin_panel`).
- **Estado**: Se muestra con una "insignia" (badge) de color según el estado:
  - `ACTIVO`: Fondo verde (`bg-success`).
  - `INACTIVO`: Fondo rojo (`bg-danger`).
  - Otros: Fondo amarillo (`bg-warning`).

## 6. Pestaña "Importar CSV"

Esta sección permite la creación masiva de condominios a través de la subida de un archivo `.csv`.

### Formato de Importación

La interfaz documenta explícitamente el formato requerido para el archivo CSV.

- **Columnas y Orden**: El sistema espera un archivo CSV con las siguientes columnas, en este orden exacto:
  ```
  name,legal_name,email,ruc,main_street,cross_street,city,country,subdomain,admin_email
  ```

- **Validaciones Mencionadas**:
  - El campo `admin_email` **debe corresponder a un usuario con rol `ADMIN` o `MASTER` que ya exista** en el sistema.
  - El estado por defecto de los condominios importados será `ACTIVO`.

- **Ejemplo de Fila Válida**:
  ```csv
  "Condominio del Sol","Condosol S.A.","contacto@condosol.com","0991234567001","Av. Principal 123","Calle Secundaria","Guayaquil","Ecuador","condominio-del-sol","admin_existente@email.com"
  ```

### Componentes de la Interfaz de Importación

- **Input de Archivo**: Un campo de formulario estándar de Bootstrap (`form-control`) que solo acepta archivos con la extensión `.csv`.
- **Botón "Importar CSV"**: Un botón de color cian (`btn-info`) que inicia el proceso de subida y procesamiento del archivo.

---