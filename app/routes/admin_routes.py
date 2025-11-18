from flask import (
    Blueprint, render_template, redirect,
    current_app, flash
)
from flask_jwt_extended import jwt_required
from app import db
from app.models import User
from app.auth import get_current_user

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin')
@jwt_required()
def admin_panel():
    user = get_current_user()
    if not user or user.role not in ['ADMIN', 'MASTER']:
        flash("Acceso denegado", "error")
        return redirect('/dashboard')

    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)

    # MASTER ve todos los tenants, ADMIN solo el suyo
    query_filter = {'status': 'pending'}
    if user.role == 'ADMIN':
        query_filter['tenant'] = user.tenant

    pending = User.query.filter_by(**query_filter).all()
    
    # Para los conteos, también filtrar por tenant si es ADMIN
    count_filter = {}
    if user.role == 'ADMIN':
        count_filter['tenant'] = user.tenant
    
    active_query = {'status': 'active', **count_filter}
    rejected_query = {'status': 'rejected', **count_filter}

    active = User.query.filter_by(**active_query).count()
    rejected = User.query.filter_by(**rejected_query).count()


    return render_template('admin/panel.html',
                           pending_users=pending,
                           active_count=active,
                           rejected_count=rejected,
                           user=user,
                           config=config)

@admin_bp.route('/aprobar/<int:user_id>')
@jwt_required()
def aprobar_usuario(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role not in ['ADMIN', 'MASTER']:
        flash("Acceso denegado.", "error")
        return redirect('/dashboard')

    user_to_approve = User.query.get_or_404(user_id)

    # Security Check: MASTER can approve anyone. ADMIN can only approve users from their own tenant.
    if current_user.role == 'ADMIN' and current_user.tenant != user_to_approve.tenant:
        flash("No tiene permiso para aprobar a este usuario.", "error")
        return redirect('/admin')

    user_to_approve.status = 'active'
    db.session.commit()
    flash(f"Usuario {user_to_approve.email} aprobado.", "success")
    return redirect('/admin')

@admin_bp.route('/rechazar/<int:user_id>')
@jwt_required()
def rechazar_usuario(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role not in ['ADMIN', 'MASTER']:
        flash("Acceso denegado.", "error")
        return redirect('/dashboard')

    user_to_reject = User.query.get_or_404(user_id)

    # Security Check: MASTER can reject anyone. ADMIN can only reject users from their own tenant.
    if current_user.role == 'ADMIN' and current_user.tenant != user_to_reject.tenant:
        flash("No tiene permiso para rechazar a este usuario.", "error")
        return redirect('/admin')

    user_to_reject.status = 'rejected'
    db.session.commit()
    flash(f"Usuario {user_to_reject.email} rechazado.", "info")
    return redirect('/admin')
