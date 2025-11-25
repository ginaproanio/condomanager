# CondoManager SaaS - Documentación de Diseño y Desarrollo

Bienvenido a la documentación de CondoManager SaaS. Este sistema está diseñado para ser escalable, seguro y amigable para el usuario.

## 📄 Documentos Clave

### 1. Estándares de Diseño y UX
*   **[docs/design.md](docs/design.md)**: (CRÍTICO) Contiene las guías de estilos, paleta de colores, ubicación de botones y estándares visuales que **deben respetarse** en toda la plataforma.

### 2. Arquitectura y Módulos
*   **[docs/02_ARQUITECTURA.md](docs/02_ARQUITECTURA.md)**: Visión técnica global, estructura de carpetas y tecnologías.
*   **[docs/11_MODULOS_FINANCIEROS.md](docs/11_MODULOS_FINANCIEROS.md)**: Detalle de los módulos financieros (Recaudación, Caja Chica, Contabilidad, Club de Compras).
*   **[docs/10_MODULOS_FUTUROS.md](docs/10_MODULOS_FUTUROS.md)**: Hoja de ruta para módulos como Marketplace, Visitors y IoT.

### 3. Roles y Permisos
*   **[docs/08_ROLES_Y_PERMISOS.md](docs/08_ROLES_Y_PERMISOS.md)**: Matriz de acceso para Master, Admin, Tesorero, Presidente y Usuario.

## 🚀 Guía Rápida para Desarrolladores

1.  **Leer `docs/design.md`**: Antes de crear cualquier vista nueva, verifica los componentes estándar (botones, títulos, formularios).
2.  **Multi-Tenancy**: Recuerda que el sistema filtra datos por `subdomain` y `condominium_id`.
3.  **Migraciones**: Siempre usa `flask db migrate` y `flask db upgrade` al modificar modelos.

## 🛠️ Instalación Local

```bash
python -m venv venv
source venv/bin/activate  # o venv\Scripts\activate en Windows
pip install -r requirements.txt
flask db upgrade
python seed_initial_data.py
flask run
```

