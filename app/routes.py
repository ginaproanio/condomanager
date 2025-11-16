from flask import Blueprint, request, render_template_string
from app.models import User, db
from app.tenant import get_tenant
import hashlib

main = Blueprint('main', __name__)

@main.route('/')
def index():
    tenant = get_tenant()
    return render_template_string(f"""
    <h1>CondoManager - {tenant.upper()}</h1>
    <p>Subdominio: <strong>{request.host}</strong></p>
    <a href="/registro">Registrarse</a>
    """)

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        pwd = hashlib.sha256(request.form['password'].encode()).hexdigest()
        tenant = get_tenant()  # ✅ Aquí SÍ hay contexto de request
        user = User(email=email, name=name, password_hash=pwd, tenant=tenant)  # ✅ Asignar manualmente
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

@main.route('/aprobar/<int:user_id>')
def aprobar(user_id):
    user = User.query.get(user_id)
    if user and user.tenant == get_tenant():
        user.status = 'active'
        user.role = 'admin'
        db.session.commit()
        return f"{user.email} es ADMIN"
    return "No autorizado"