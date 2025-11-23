from flask import (
    Blueprint, render_template, redirect, url_for,
    current_app, flash, request, session
)
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app import db
from app.models import User, Condominium, Unit
from app.auth import get_current_user

admin_bp = Blueprint('admin', __name__)

def is_authorized_admin_for_condo(user, condominium):
    """
    Función de seguridad centralizada para verificar si un usuario es un administrador autorizado
    para un condominio específico.
    """
    if not user or not condominium:
        return False

    # CORRECCIÓN: Un ADMIN tiene acceso si su ID está en el campo `admin_user_id` del condominio.
    # Esta es la relación directa y correcta.
    return user.role == 'ADMIN' and condominium.admin_user_id == user.id

@admin_bp.route('/admin')
@jwt_required()
def admin_panel(): # Esta función ahora es solo un despachador (dispatcher)
    user = get_current_user()
    if not user or user.role not in ['ADMIN', 'MASTER']:
        flash("Acceso denegado", "error")
        return redirect('/dashboard')

    # --- LÓGICA DE REDIRECCIÓN INTELIGENTE ---
    # Si es un ADMIN, siempre debe ir a su propio panel de condominio.
    if user.role == 'ADMIN':
        admin_condo = Condominium.query.filter(func.lower(Condominium.subdomain) == func.lower(user.tenant)).first()
        if admin_condo:
            return redirect(url_for('admin.admin_condominio_panel', condominium_id=admin_condo.id))

    # Si un MASTER llega aquí sin suplantar, no tiene un panel de admin al que ir.
    # Lo enviamos a su propio panel maestro.
    flash("Panel de administración no especificado.", "info")
    return redirect(url_for('master.master_panel'))

@admin_bp.route('/aprobar/<int:user_id>')
@jwt_required()
def aprobar_usuario(user_id):
    current_user = get_current_user()
    if not current_user or current_user.role not in ['ADMIN', 'MASTER']:
        flash("Acceso denegado.", "error")
        return redirect('/dashboard')

    user_to_approve = User.query.get_or_404(user_id)

    # --- LÓGICA DE SEGURIDAD UNIFICADA ---
    # Un ADMIN solo puede aprobar usuarios de su propio tenant.
    if current_user.role == 'ADMIN' and (not user_to_approve.tenant or user_to_approve.tenant.strip().lower() != current_user.tenant.strip().lower()):
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

    # --- LÓGICA DE SEGURIDAD UNIFICADA ---
    # Un ADMIN solo puede rechazar usuarios de su propio tenant.
    if current_user.role == 'ADMIN' and (not user_to_reject.tenant or user_to_reject.tenant.strip().lower() != current_user.tenant.strip().lower()):
        flash("No tiene permiso para rechazar a este usuario.", "error")
        return redirect('/admin')

    user_to_reject.status = 'rejected'
    db.session.commit()
    flash(f"Usuario {user_to_reject.email} rechazado.", "info")
    return redirect('/admin')

@admin_bp.route('/admin/condominio/<int:condominium_id>', methods=['GET', 'POST'])
@jwt_required()
def admin_condominio_panel(condominium_id):
    """
    Panel de gestión específico para un condominio.
    Muestra las unidades y opciones de gestión.
    """
    current_user = get_current_user()
    condominium = Condominium.query.get_or_404(condominium_id)

    # --- LÓGICA DE SEGURIDAD REFORZADA ---
    if not is_authorized_admin_for_condo(current_user, condominium):
        flash("No tienes acceso a este panel de administración de condominio o no estás asignado a este condominio. Por favor, inicia sesión como un Administrador autorizado.", "error")
        return redirect(url_for('public.login'))

    # Lógica para obtener usuarios pendientes solo de este condominio
    pending_users_in_condo = User.query.filter_by(tenant=condominium.subdomain, status='pending').all()
    users_in_condo = User.query.filter(User.tenant == condominium.subdomain, User.status != 'pending').all()
    units = Unit.query.filter_by(condominium_id=condominium_id).order_by(Unit.name).all()

    return render_template('admin/condominio_panel.html', 
                           user=current_user, 
                           condominium=condominium, 
                           units=units,
                           pending_users_in_condo=pending_users_in_condo,
                           users_in_condo=users_in_condo)
