from flask import Blueprint, request, render_template
from app.models import User, db
import hashlib

main = Blueprint('main', __name__)

# ✅ AGREGA ESTA RUTA
@main.route('/')
def home():
    return """
    <h1>¡CondoManager Funcionando!</h1>
    <p><a href='/registro'>Ir al Registro</a></p>
    <p><a href='/health'>Health Check</a></p>
    """

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        pwd = hashlib.sha256(request.form['password'].encode()).hexdigest()
        # ... resto de tu código ...
        return f"Registrado: {email}"
    
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