from flask import Blueprint, request, render_template, redirect, url_for
from app import db
from app.models import User
import hashlib
import traceback

main = Blueprint('main', __name__)

@main.route('/')
def home():
    """Página principal del sistema"""
    return render_template('home.html')

@main.route('/registro', methods=['GET', 'POST'])
def registro():
    """Registro de nuevos usuarios"""
    try:
        if request.method == 'POST':
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # USAR TENANT DINÁMICO
            from app.tenant import get_tenant
            tenant = get_tenant()
            
            # Verificar si el usuario ya existe
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                return render_template('auth/registro.html', 
                                    error="❌ Este email ya está registrado")
            
            user = User(
                email=email, 
                name=name, 
                password_hash=pwd_hash, 
                tenant=tenant,
                status='pending'
            )
            
            db.session.add(user)
            db.session.commit()
            
            return render_template('auth/registro.html', 
                                mensaje=f"✅ Registrado exitosamente. Tu email {email} está pendiente de aprobación en {tenant}.")
        
        return render_template('auth/registro.html')
    
    except Exception as e:
        return render_template('auth/registro.html', 
                             error=f"❌ Error en registro: {str(e)}")

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login de usuarios"""
    try:
        if request.method == 'POST':
            email = request.form['email']
            password = request.form['password']
            pwd_hash = hashlib.sha256(password.encode()).hexdigest()
            
            user = User.query.filter_by(email=email, password_hash=pwd_hash).first()
            
            if user:
                if user.status == 'pending':
                    return render_template('auth/login.html',
                                        error="⏳ Tu cuenta está pendiente de aprobación")
                elif user.status == 'rejected':
                    return render_template('auth/login.html',
                                        error="❌ Tu cuenta fue rechazada. Contacta al administrador")
                
                return render_template('auth/login.html', 
                                    mensaje=f"🎉 Bienvenido {user.name}!")
            else:
                return render_template('auth/login.html',
                                    error="❌ Credenciales incorrectas")
        
        return render_template('auth/login.html')
    
    except Exception as e:
        return render_template('auth/login.html', 
                             error=f"❌ Error en login: {str(e)}")

@main.route('/admin')
def admin_panel():
    """Panel de administración para aprobar usuarios"""
    try:
        # Listar usuarios pendientes de aprobación
        pending_users = User.query.filter_by(status='pending').all()
        active_users = User.query.filter_by(status='active').all()  # ✅ NUEVO
        rejected_users = User.query.filter_by(status='rejected').all()  # ✅ NUEVO
        
        return render_template('admin/panel.html', 
                             pending_users=pending_users,
                             active_count=len(active_users),  # ✅ Pasar contadores
                             rejected_count=len(rejected_users))  # ✅ Pasar contadores
    
    except Exception as e:
        return render_template('admin/panel.html',
                             error=f"Error cargando panel: {str(e)}")

@main.route('/aprobar/<int:user_id>')
def aprobar_usuario(user_id):
    """Aprobar usuario pendiente"""
    try:
        user = User.query.get(user_id)
        if user:
            user.status = 'active'
            db.session.commit()
            return redirect('/admin')
        return redirect('/admin')
    except Exception as e:
        return redirect('/admin')

@main.route('/rechazar/<int:user_id>')
def rechazar_usuario(user_id):
    """Rechazar usuario pendiente"""
    try:
        user = User.query.get(user_id)
        if user:
            user.status = 'rejected' 
            db.session.commit()
            return redirect('/admin')
        return redirect('/admin')
    except Exception as e:
        return redirect('/admin')

@main.route('/dashboard')
def dashboard():
    """Dashboard para usuarios aprobados"""
    return render_template('user/dashboard.html', 
                         mensaje="🏠 Panel de usuario - Próximamente")

@main.route('/usuarios')
def listar_usuarios():
    """Listar todos los usuarios (solo admin)"""
    try:
        users = User.query.all()
        return render_template('admin/usuarios.html',
                             users=users)
    except Exception as e:
        return f"Error listando usuarios: {str(e)}"

@main.route('/health')
def health():
    """Health check para monitoreo"""
    return "OK", 200

# ✅ RUTAS DE SERVICIOS FUTUROS
@main.route('/unidades')
def unidades():
    """Gestión de unidades (próximamente)"""
    return render_template('services/unidades.html',
                         mensaje="🏢 Gestión de Unidades - Próximamente")

@main.route('/pagos')
def pagos():
    """Sistema de pagos (próximamente)"""
    return render_template('services/pagos.html',
                         mensaje="💳 Sistema de Pagos - Próximamente")

@main.route('/reportes')
def reportes():
    """Reportes del sistema (próximamente)"""
    return render_template('services/reportes.html',
                         mensaje="📊 Reportes - Próximamente")