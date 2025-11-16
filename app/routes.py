from flask import Blueprint, request, render_template
from app.models import User, db
import hashlib

main = Blueprint('main', __name__)

def get_tenant_safe():
    """Versión segura que no depende del contexto de request"""
    try:
        host = request.host
        if 'localhost' in host or 'railway' in host:
            return 'puntablanca'
        parts = host.split('.')
        if len(parts) > 2:
            return parts[0]
    except RuntimeError:
        pass
    return 'puntablanca'

@main.route('/')
def index():
    tenant = get_tenant_safe()
    return f"""
    <h1>CondoManager - {tenant.upper()}</h1>
    <p>Subdominio: <strong>{request.host}</strong></p>
    <a href="/registro">Registrarse</a>
    """

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        pwd = hashlib.sha256(request.form['password'].encode()).hexdigest()
        tenant = get_tenant_safe()
        user = User(email=email, name=name, password_hash=pwd, tenant=tenant)
        db.session.add(user)
        db.session.commit()
        return f"Registrado: {email} en {tenant}"
    
    return """
    <form method="post">
        Email: <input type="email" name="email" required><br><br>
        Nombre: <input type="text" name="name" required><br><br>
        Contraseña: <input type="password" name="password" required><br><br>
        <button>Registrarse</button>
    </form>
    """

@main.route('/health')
def health():
    return "OK", 200