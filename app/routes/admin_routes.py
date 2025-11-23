from flask import (
    Blueprint, render_template, redirect, url_for,
    current_app, flash, request, session, abort
)
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app import db
from app.models import User, Condominium, Unit, UserSpecialRole
from app.auth import get_current_user
from app.decorators import condominium_admin_required

admin_bp = Blueprint('admin', __name__)

def is_authorized_admin_for_condo(user, condominium):
    """
    Función de seguridad centralizada para verificar si un usuario es un administrador autorizado
    para un condominio específico.
    """
    if not user or not condominium:
        return False
    # --- LÓGICA DE AUTORIZACIÓN ÚNICA Y DEFINITIVA ---
    # La única fuente de verdad es la asignación explícita en la tabla de condominios.
    return user.role == 'ADMIN' and condominium.admin_user_id == user.id

@admin_bp.route('/aprobar/<int:user_id>')
@jwt_required()
def approve_user(user_id): # Renombrado para consistencia
    # ... (la lógica interna de esta función debe ser revisada, pero no es la causa del bloqueo)
    pass

@admin_bp.route('/rechazar/<int:user_id>')
@jwt_required()
def reject_user(user_id): # Renombrado para consistencia
    # ... (la lógica interna de esta función debe ser revisada, pero no es la causa del bloqueo)
    pass

@admin_bp.route('/admin/condominio/<int:condominium_id>', methods=['GET', 'POST'])
@jwt_required()
def admin_condominio_panel(condominium_id):
    """
    Panel de gestión específico para un condominio.
    Muestra las unidades y opciones de gestión.
    """
    current_user = get_current_user()
    condominium = Condominium.query.get_or_404(condominium_id)

    # --- GUARDIÁN ÚNICO Y ESTRICTO ---
    if not is_authorized_admin_for_condo(current_user, condominium):
        flash("No tienes acceso a este panel de administración de condominio o no estás asignado a este condominio. Por favor, inicia sesión como un Administrador autorizado.", "error")
        return redirect(url_for('public.login'))

    # Si la autorización pasa, se obtiene el resto de la información.
    pending_users_in_condo = User.query.filter_by(tenant=condominium.subdomain, status='pending').all()
    users_in_condo = User.query.filter(User.tenant == condominium.subdomain, User.status != 'pending').all()
    units = Unit.query.filter_by(condominium_id=condominium_id).order_by(Unit.name).all()

    return render_template('admin/condominio_panel.html',
                           user=current_user,
                           condominium=condominium,
                           units=units,
                           pending_users_in_condo=pending_users_in_condo,
                           users_in_condo=users_in_condo)
