# Reporte de Implementación: Lógica de Login Seguro

**Versión:** 3.0 (Reporte Post-Implementación)
**Fecha:** 2025-11-29

## 1. Objetivo

Centralizar la lógica de autenticación en un nuevo blueprint (`auth_bp`) para crear un sistema de login seguro, robusto y que cumpla con las reglas de negocio y seguridad del proyecto, incluyendo protección multi-tenant, redirección por roles y mitigación de ataques comunes.

---

## 2. Aclaración sobre Formularios: `FlaskForm` vs. `login.html`

El plan **NO** requiere crear un nuevo archivo HTML. Se utilizará el archivo `app/templates/auth/login.html` que ya existe.

La confusión surge de la terminología de Flask:

- **Formulario HTML (`login.html`):** Es la estructura visual que el usuario ve en el navegador. Ya está creado.
- **Clase de Formulario (`LoginForm` en Python):** Es una clase en el backend que se encarga de:
    1.  Recibir los datos del formulario HTML.
    2.  **Validar** que los datos sean correctos (ej. que el email tenga formato de email).
    3.  **Generar y validar un token de seguridad CSRF**, que es una regla crítica del proyecto.

El plan consiste en crear esta clase en Python y conectar la lógica a tu HTML existente.

---

## 3. Arquitectura de Implementación

### Paso 1: Crear la Clase `LoginForm` en Python

Crearemos la clase que procesará los datos del login.

**Archivo:** `app/forms.py`

```python
# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email(), Length(max=255)])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Ingresar')
```

### Paso 2: Modificar `login.html` para Añadir Seguridad CSRF

Para que el formulario web se comunique de forma segura con el backend, es mandatorio que envíe los datos vía `POST` y que incluya un token de protección contra ataques CSRF (Cross-Site Request Forgery).

**Archivo:** `app/templates/auth/login.html`

**Cambios Requeridos:**
1.  Asegurar que la etiqueta `<form>` use `method="POST"` y apunte a la ruta correcta con `action="{{ url_for('auth.login') }}"`.
2.  Añadir `{{ form.hidden_tag() }}` inmediatamente después de abrir la etiqueta `<form>`. Esto inyecta el campo oculto con el token CSRF, un requisito de seguridad no negociable.

```html
<!-- Formulario JWT -->
<form id="login-form" method="POST" action="{{ url_for('auth.login') }}">
    {{ form.hidden_tag() }} <!-- ✅ LÍNEA AÑADIDA: Protección CSRF obligatoria -->

    <!-- El resto de los campos del formulario (email, password) van aquí -->
    <!-- ... -->
```
*Nota: También se añade `method="POST"` y la acción que apunta a la ruta de login del backend.*

### Paso 3: Implementar la Lógica en la Ruta (Backend)

La ruta `/ingresar` en `app/auth.py` debe contener la lógica completa para validar al usuario, verificar su rol y redirigirlo al panel correcto.

**Archivo:** `app/auth.py`

```python
from flask import render_template, flash, redirect, url_for, g, current_app, make_response
from flask_jwt_extended import create_access_token, set_access_cookies
from werkzeug.security import check_password_hash, generate_password_hash
from .forms import LoginForm  # Importar la clase del paso 1
from .models import User, Condominium
from .extensions import limiter

@auth_bp.route('/ingresar', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # ✅ REGLA: Previene ataques de fuerza bruta
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email_lower = form.email.data.lower()
        try:
            # Lógica de búsqueda de usuario consciente del tenant
            user = User.query.filter_by(email=email_lower).first() if not g.condominium else \
                   User.query.filter_by(email=email_lower, condominium_id=g.condominium.id).first()

            if user and check_password_hash(user.password_hash, form.password.data):
                if user.status != 'active':
                    flash('Tu cuenta se encuentra pendiente de aprobación o ha sido desactivada.', 'warning')
                    return render_template('auth/login.html', form=form)

                # --- LÓGICA DE REDIRECCIÓN POR ROL (CRÍTICA) ---
                redirect_url = url_for('user.dashboard') # Destino por defecto para USER
                if user.role == 'MASTER':
                    redirect_url = url_for('master.master_panel')
                elif user.role == 'ADMIN':
                    admin_condo = Condominium.query.filter_by(admin_user_id=user.id).first()
                    if admin_condo:
                        redirect_url = url_for('admin.admin_condominio_panel', condominium_id=admin_condo.id)
                
                access_token = create_access_token(identity=str(user.id))
                response = make_response(redirect(next_url or redirect_url))
                set_access_cookies(response, access_token)
                current_app.logger.info(f"Login exitoso para user {user.id}.")
                return response

            flash('Usuario o contraseña incorrectos.', 'danger')
        except Exception as e:
            current_app.logger.error(f"Error en login: {str(e)}")
            flash('Error interno del servidor.', 'danger')

    return render_template('auth/login.html', form=form)
```

---

## 4. Verificación Arquitectónica y de Consistencia

La implementación del login no está completa sin asegurar la consistencia en todo el sistema. Los siguientes puntos son críticos y deben ser verificados:

1.  **Actualización del Middleware de Acceso:** Para que las rutas de login y los paneles globales (`/master`, `/documentos`) funcionen sin un subdominio, el middleware debe ser actualizado para permitir el paso a los blueprints correspondientes.

    **Archivo:** `app/middleware.py`
    ```python
    if request.endpoint and not (
        request.endpoint.startswith('public.') or
        request.endpoint.startswith('auth.') or
        request.endpoint.startswith('api.') or
        request.endpoint.startswith('master.') or
        request.endpoint.startswith('document.')
    ):
        abort(404, ...)
    ```

2.  **Consistencia de Hashing:** Asegurar que `seed_initial_data.py` y todas las rutas de registro usen `generate_password_hash` de Werkzeug para crear contraseñas. Esto es mandatorio para que el login funcione.

3.  **Auditoría de Plantillas:** Auditar y unificar **todas** las plantillas (`.html`) para que las llamadas `url_for()` apunten a los nuevos endpoints del blueprint `auth` (ej. `auth.login`, `auth.logout`). Esto previene errores de `BuildError`.