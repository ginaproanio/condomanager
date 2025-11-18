from flask import (
    Blueprint, render_template, redirect,
    current_app, flash
)
from flask_jwt_extended import jwt_required
from app.auth import get_current_user

user_bp = Blueprint('user', __name__)

@user_bp.route('/dashboard')
@jwt_required()
def dashboard():
    user = get_current_user()
    if not user:
        flash("Sesión inválida", "error")
        return redirect('/login')
    
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('user/dashboard.html', user=user, config=config)

@user_bp.route('/unidades')
@jwt_required()
def unidades():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/unidades.html', mensaje="Gestión de Unidades", config=config)

@user_bp.route('/pagos')
@jwt_required()
def pagos():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/pagos.html', mensaje="Sistema de Pagos", config=config)

@user_bp.route('/reportes')
@jwt_required()
def reportes():
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    return render_template('services/reportes.html', mensaje="Reportes", config=config)
