from flask import Blueprint, request, render_template
from app import db
from app.models import User
import hashlib
import traceback

main = Blueprint('main', __name__)

@main.route('/')
def home():
    return """
    <h1>¡CondoManager SaaS - Funcionando!</h1>
    <p><a href='/registro'>Registrarse</a></p>
    <p>Sistema de gestión multi-condominios</p>
    """

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    try:
        if request.method == 'POST':
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            tenant = 'puntablanca'
            
            # ✅ VERIFICAR SI LA TABLA EXISTE
            print(f"🔧 Intentando crear usuario: {email}")
            
            user = User(
                email=email, 
                name=name, 
                password_hash=pwd_hash, 
                tenant=tenant,
                status='pending'  # ✅ AGREGAR ESTE CAMPO
            )
            
            db.session.add(user)
            db.session.commit()
            
            return f"✅ Registrado: {email} en {tenant}. Espera aprobación."
        
        return """
        <form method="post">
            <h2>Registro - CondoManager</h2>
            Email: <input type="email" name="email" required><br><br>
            Nombre: <input type="text" name="name" required><br><br>
            Contraseña: <input type="password" name="password" required><br><br>
            <button>Registrarse</button>
        </form>
        """
    
    except Exception as e:
        error_msg = f"❌ Error en registro: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        return error_msg

@main.route('/health')
def health():
    return "OK", 200