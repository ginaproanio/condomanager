# Plan de Trabajo: Implementación de Lógica de Login

**Versión:** 1.1
**Fecha:** 2025-11-29

## 1. Objetivo

Implementar la lógica de backend para el inicio de sesión de usuarios, utilizando el template existente `app/templates/auth/login.html`. El objetivo es crear una ruta de login segura, robusta y que cumpla con todas las reglas de la Constitución Técnica (00_CONVENCIONES.md), especialmente en lo referente a seguridad multi-tenant y protección contra ataques.

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

## 3. Plan de Trabajo Detallado

### Paso 1: Crear la Clase `LoginForm` en Python

Crearemos la clase que procesará los datos del login.

**Archivo:** `app/forms.py` (o crear `app/auth/forms.py` si se prefiere mayor modularidad).

```python
# app/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class LoginForm(FlaskForm):
    # Los nombres 'email' y 'password' deben coincidir con los atributos 'name' de los inputs en login.html
    email = StringField('Correo Electrónico', validators=[
        DataRequired(message='El correo es obligatorio.'),
        Email(message='Por favor, ingrese un correo válido.')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria.')
    ])
    submit = SubmitField('Iniciar Sesión')
```

### Paso 2: Modificar `login.html` para Añadir Seguridad CSRF

El formulario actual en `login.html` carece de protección CSRF, lo cual es una violación a las reglas de seguridad del proyecto. Se debe añadir una línea.

**Archivo:** `app/templates/auth/login.html`

**Cambio:** Dentro de la etiqueta `<form>`, justo después de abrirla, añade `{{ form.hidden_tag() }}`. Esto inyectará un campo oculto con el token CSRF.

```html
<!-- Formulario JWT -->
<form id="login-form" method="POST" action="{{ url_for('auth.login') }}">
    {{ form.hidden_tag() }} <!-- ✅ LÍNEA AÑADIDA: Protección CSRF obligatoria -->

    <div class="mb-3">
        <label for="email" class="form-label">Email</label>
        <!-- ... resto del input ... -->
```
*Nota: También se añade `method="POST"` y la acción que apunta a la ruta de login del backend.*

### Paso 3: Implementar la Lógica en la Ruta (Backend)

Aquí se conectará todo: se procesará el formulario, se validará al usuario contra la base de datos (respetando el tenant) y se gestionará la sesión.

**Archivo:** `app/auth.py` (o donde se defina la ruta `/ingresar`).

```python
from flask import render_template, flash, redirect, url_for, g, current_app, make_response
from flask_jwt_extended import create_access_token, set_access_cookies
from werkzeug.security import check_password_hash
from .forms import LoginForm  # Importar la clase del paso 1
from .models import User
from .extensions import limiter

@auth_bp.route('/ingresar', methods=['GET', 'POST'])
@limiter.limit("5 per minute") # ✅ REGLA: Previene ataques de fuerza bruta
def login():
    form = LoginForm()
    if form.validate_on_submit(): # Esto se activa en el POST y valida los datos
        email_lower = form.email.data.lower()
        
        try:
            # ✅ LÓGICA ANTI-PARALELISMO:
            # Si no hay subdominio (g.condominium es None), es un login "global" (MASTER en Railway/localhost).
            # Si hay subdominio, la query se filtra ESTRICTAMENTE por el condominium_id.
            user = User.query.filter_by(email=email_lower).first() if not g.condominium else \
                   User.query.filter_by(email=email_lower, condominium_id=g.condominium.id).first()
        except Exception as e:
            current_app.logger.error(f"Error DB durante login: {str(e)}")
            flash('Error interno del servidor.', 'danger')
            return render_template('auth/login.html', form=form)

        if user and check_password_hash(user.password_hash, form.password.data):
            # ✅ REGLA DE ROLES: Verificar que la cuenta esté activa antes de crear la sesión.
            if user.status != 'active':
                flash('Tu cuenta se encuentra pendiente de aprobación o ha sido desactivada.', 'warning')
                current_app.logger.warning(f"Login denegado para usuario inactivo/pendiente: {email_lower}")
                return render_template('auth/login.html', form=form, error='Acceso denegado.')

            # Lógica de creación de sesión con JWT en cookies
            access_token = create_access_token(identity=str(user.id))
            response = make_response(redirect(url_for('user.dashboard')))
            set_access_cookies(response, access_token)
            
            # Log informativo que diferencia el contexto
            log_context = f"en subdominio {g.condominium.subdomain}" if g.condominium else "en dominio global"
            current_app.logger.info(f"Login exitoso para user {user.id} {log_context}.")
            if g.condominium and g.condominium.environment == 'sandbox':
                current_app.logger.info(f"Login detectado en entorno SANDBOX para user {user.id}.")

            return response
        else:
            current_app.logger.warning(f"Intento de login fallido para {email_lower}.")
            # Usamos la variable 'error' que ya espera el template login.html
            return render_template('auth/login.html', form=form, error='Usuario o contraseña incorrectos.')

    # Renderiza el formulario existente en la petición GET
    return render_template('auth/login.html', form=form)
```

---

## 4. Resumen de Tareas

1.  **Crear `LoginForm` en `app/forms.py`**: Define la estructura de datos y validaciones del backend.
2.  **Añadir `{{ form.hidden_tag() }}` a `login.html`**: Parchea el hueco de seguridad CSRF.
3.  **Implementar la función `login()` en el backend**: Conecta todo, aplicando la lógica de negocio, seguridad y las reglas anti-paralelismo.
4.  **Verificar**: Probar que un login exitoso redirige al dashboard y uno fallido muestra el mensaje de error en la misma página `login.html`.