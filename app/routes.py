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

# Agregar a routes.py
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        pwd_hash = hashlib.sha256(password.encode()).hexdigest()
        
        user = User.query.filter_by(email=email, password_hash=pwd_hash).first()
        
        if user:
            return f"Bienvenido {user.name}!"
        else:
            return "Credenciales incorrectas"
    
    return """
    <form method="post">
        <h2>Login</h2>
        Email: <input type="email" name="email" required><br>
        Contraseña: <input type="password" name="password" required><br>
        <button>Ingresar</button>
    </form>
    <p><a href='/registro'>¿No tienes cuenta? Regístrate</a></p>
    """
    
    # Agregar a routes.py
@main.route('/admin')
def admin_panel():
    # Listar usuarios pendientes de aprobación
    pending_users = User.query.filter_by(status='pending').all()
    
    users_html = ""
    for user in pending_users:
        users_html += f"""
        <div>
            <strong>{user.name}</strong> ({user.email})
            <a href='/aprobar/{user.id}'>Aprobar</a>
            <a href='/rechazar/{user.id}'>Rechazar</a>
        </div>
        """
    
    return f"""
    <h1>Panel de Administración - Punta Blanca</h1>
    <h2>Usuarios Pendientes:</h2>
    {users_html if users_html else "<p>No hay usuarios pendientes</p>"}
    """
    
    
    # Agregar a routes.py
@main.route('/aprobar/<int:user_id>')
def aprobar_usuario(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = 'active'
        db.session.commit()
        return f"Usuario {user.email} APROBADO"
    return "Usuario no encontrado"

@main.route('/rechazar/<int:user_id>')
def rechazar_usuario(user_id):
    user = User.query.get(user_id)
    if user:
        user.status = 'rejected' 
        db.session.commit()
        return f"Usuario {user.email} RECHAZADO"
    return "Usuario no encontrado"