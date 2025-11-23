from flask import (
    Blueprint, render_template, redirect, url_for,
    current_app, flash, request, session
)
from flask_jwt_extended import jwt_required
from app import db
from app.models import User, Condominium, Unit
from app.auth import get_current_user

admin_bp = Blueprint('admin', __name__)

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
        admin_condo = Condominium.query.filter_by(subdomain=user.tenant).first()
        if admin_condo:
            return redirect(url_for('admin.admin_condominio_panel', condominium_id=admin_condo.id))

    # Si es un MASTER suplantando, redirigir al panel del condominio suplantado.
    if user.role == 'MASTER' and session.get('impersonating_condominium_id'):
        impersonated_condo_id = session.get('impersonating_condominium_id')
        return redirect(url_for('admin.admin_condominio_panel', condominium_id=impersonated_condo_id))

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

@admin_bp.route('/admin/condominio/<int:condominium_id>')
@jwt_required()
def admin_condominio_panel(condominium_id):
    """
    Panel de gestión específico para un condominio.
    Muestra las unidades y opciones de gestión.
    """
    user = get_current_user()
    condominium = Condominium.query.get_or_404(condominium_id)

    # Verificación de seguridad: El ADMIN debe pertenecer al tenant del condominio
    # O debe ser un MASTER suplantando a ese condominio.
    is_impersonating = user.role == 'MASTER' and session.get('impersonating_condominium_id') == condominium_id
    is_correct_admin = user.role == 'ADMIN' and user.tenant == condominium.subdomain

    if not (is_impersonating or is_correct_admin):
        flash("No tienes acceso a este panel de administración de condominio o no estás asignado a este condominio. Por favor, inicia sesión como un Administrador autorizado.", "error")
        return redirect(url_for('user.dashboard'))

    unidades = Unit.query.filter_by(condominium_id=condominium_id).order_by(Unit.name).all()
    return render_template('admin/condominio_panel.html', user=user, condominium=condominium, unidades=unidades)

@admin_bp.route('/admin/condominio/<int:condominium_id>/unidad/nueva', methods=['GET', 'POST'])
@jwt_required()
def crear_unidad(condominium_id):
    user = get_current_user()
    condominium = Condominium.query.get_or_404(condominium_id)

    if user.role != 'ADMIN' or user.tenant != condominium.subdomain:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        new_unit = Unit(
            condominium_id=condominium.id,
            property_number=request.form.get('property_number'),
            name=request.form.get('name'),
            property_type=request.form.get('property_type'),
            building=request.form.get('building'),
            floor=request.form.get('floor'),
            area_m2=float(request.form.get('area_m2')) if request.form.get('area_m2') else None,
            sector=request.form.get('sector'),
            bedrooms=int(request.form.get('bedrooms')) if request.form.get('bedrooms') else None,
            bathrooms=int(request.form.get('bathrooms')) if request.form.get('bathrooms') else None,
            created_by=user.id
        )
        db.session.add(new_unit)
        db.session.commit()
        flash(f'Unidad "{new_unit.name}" creada exitosamente.', 'success')
        return redirect(url_for('admin.admin_condominio_panel', condominium_id=condominium.id))

    return render_template('admin/crear_editar_unidad.html', user=user, condominium=condominium)

@admin_bp.route('/admin/condominio/unidad/editar/<int:unit_id>', methods=['GET', 'POST'])
@jwt_required()
def editar_unidad(unit_id):
    user = get_current_user()
    unit_to_edit = Unit.query.get_or_404(unit_id)
    condominium = unit_to_edit.condominium

    if user.role != 'ADMIN' or user.tenant != condominium.subdomain:
        flash("Acceso no autorizado.", "error")
        return redirect(url_for('user.dashboard'))

    if request.method == 'POST':
        unit_to_edit.property_number = request.form.get('property_number')
        unit_to_edit.name = request.form.get('name')
        unit_to_edit.property_type = request.form.get('property_type')
        unit_to_edit.building = request.form.get('building')
        unit_to_edit.floor = request.form.get('floor')
        unit_to_edit.area_m2 = float(request.form.get('area_m2')) if request.form.get('area_m2') else None
        unit_to_edit.sector = request.form.get('sector')
        unit_to_edit.bedrooms = int(request.form.get('bedrooms')) if request.form.get('bedrooms') else None
        unit_to_edit.bathrooms = int(request.form.get('bathrooms')) if request.form.get('bathrooms') else None
        db.session.commit()
        flash(f'Unidad "{unit_to_edit.name}" actualizada exitosamente.', 'success')
        return redirect(url_for('admin.admin_condominio_panel', condominium_id=condominium.id))

    return render_template('admin/crear_editar_unidad.html', user=user, condominium=condominium, unit=unit_to_edit)

@admin_bp.route('/admin/condominio/unidad/eliminar/<int:unit_id>', methods=['POST'])
@jwt_required()
def eliminar_unidad(unit_id):
    # Placeholder para la lógica de eliminación
    flash(f"Funcionalidad para eliminar unidad {unit_id} no implementada.", "info")
    unit = Unit.query.get_or_404(unit_id)
    return redirect(url_for('admin.admin_condominio_panel', condominium_id=unit.condominium_id))
