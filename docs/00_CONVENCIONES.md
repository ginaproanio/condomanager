# 00. Convenciones del Proyecto

Versión: 1.0 (2025-11-20)

> **Propósito**: Este documento es la fuente de verdad única para todas las convenciones de código, nomenclatura y flujo de trabajo en el proyecto CondoManager. El cumplimiento de estas reglas es **obligatorio** para mantener la calidad, consistencia y mantenibilidad del código.

---

## 1. Convención de Idioma (La Regla de Oro)

La regla más importante del proyecto es la separación de idiomas entre el código y la interfaz de usuario.

### 1.1. Código Fuente: **Inglés**

Todo el código y los identificadores técnicos **DEBEN** estar en inglés. Esto incluye, sin excepción:

- Nombres de variables, funciones, clases, y métodos.
- Nombres de archivos y directorios.
- Nombres de tablas y columnas en la base de datos (`app/models.py`).
- Endpoints de la API y nombres de rutas (`url_for(...)`).
- Comentarios dentro del código.
- Mensajes de commit en Git.

**✅ Correcto:**
```python
# app/models.py
class Condominium(db.Model):
    name = db.Column(db.String(200))

# app/routes/master_routes.py
@master_bp.route('/condominiums/new')
def create_condominium():
    # ...

flash("Condominio creado exitosamente.", "success")
return redirect(url_for('master.list_condominiums'))
```

**❌ Incorrecto:**
```python
# app/models.py
class Condominio(db.Model): # Mal: Nombre de clase en español
    nombre = db.Column(db.String(200)) # Mal: Nombre de columna en español

# app/routes/master_routes.py
@master_bp.route('/condominios/nuevo') # Mal: Endpoint en español
def crear_condominio(): # Mal: Nombre de función en español
    # ...

flash("Condominium created successfully.", "success") # Mal: Mensaje a usuario en inglés
return redirect(url_for('master.lista_condominios')) # Mal: Nombre de ruta en español
```

### 1.2. Interfaz de Usuario (UI): **Español**

Todo el texto que el usuario final ve en su pantalla **DEBE** estar en español. Esto incluye:

- Texto dentro de las plantillas HTML (`app/templates/`).
- Mensajes de `flash()` que se muestran al usuario.
- Etiquetas de formularios, títulos de páginas, etc.

## 2. Flujo de Trabajo (Git)

- **Ramas:** El trabajo nuevo siempre se realiza en una rama descriptiva (ej. `feature/user-profile`, `fix/login-error`). La rama `main` está protegida y solo se actualiza a través de Pull Requests.
- **Commits:** Los mensajes de commit deben ser claros, concisos y en inglés. Deben describir *qué* se cambió y *por qué*.

## 3. Estilo de Código

- **Python:** Se sigue el estándar **PEP 8**. Se recomienda usar un formateador como `autopep8` o `black` en VS Code para mantener la consistencia automáticamente.
- **HTML/CSS/JS:** Se sigue un estilo consistente, utilizando un formateador como `Prettier` en VS Code.