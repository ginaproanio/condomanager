from flask import Blueprint, request, render_template
from app.models import User, db
import hashlib

main = Blueprint('main', __name__)

# ✅ AGREGA ESTA RUTA RAÍZ
@main.route('/')
def home():
    return """
    <h1>¡CondoManager SaaS - Funcionando!</h1>
    <p><a href='/registro'>Registrarse</a></p>
    <p>Sistema de gestión multi-condominios</p>
    """

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        pwd = hashlib.sha256(request.form['password'].encode()).hexdigest()
        tenant = 'puntablanca'  # Temporalmente fijo
        user = User(email=email, name=name, password_hash=pwd, tenant=tenant)
        db.session.add(user)
        db.session.commit()
        return f"Registrado: {email} en {tenant}"
    
    return """
    <form method="post">
        Email: <input type="email" name="email" required><br>
        Nombre: <input type="text" name="name" required><br>
        Contraseña: <input type="password" name="password" required><br>
        <button>Registrarse</button>
    </form>
    """

@main.route('/health')
def health():
    return "OK", 200