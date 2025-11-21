from flask import (
    Blueprint, render_template, redirect,
    current_app, flash, Response, jsonify, request, url_for
)
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import Condominium, User
from app import db
import io
import csv

master_bp = Blueprint('master', __name__)

@master_bp.route('/master')
@jwt_required()
def master_panel():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    
    from app.tenant import get_tenant
    tenant = get_tenant()
    config = current_app.get_tenant_config(tenant)
    all_users = User.query.all()
    return render_template('master/panel.html', user=user, config=config, all_users=all_users)

@master_bp.route('/master/condominios', methods=['GET'])
@jwt_required()
def master_condominios():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    all_condominiums = Condominium.query.order_by(Condominium.created_at.desc()).all()
    return render_template('master/condominios.html', user=user, all_condominiums=all_condominiums)

@master_bp.route('/master/usuarios', methods=['GET', 'POST'])
@jwt_required()
def master_usuarios():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')
    
    if request.method == 'POST' and request.form.get('action') == 'create_user':
        # Lógica para crear un nuevo usuario desde el panel maestro
        try:
            from app.routes.public_routes import register_user # Reutilizar lógica de registro
            register_user(is_master_creation=True)
            flash('Usuario creado exitosamente.', 'success')
        except Exception as e:
            flash(f'Error al crear el usuario: {e}', 'error')
        return redirect(url_for('master.master_usuarios'))

    # Lógica para GET
    pending_users = User.query.filter_by(status='pending').order_by(User.created_at.desc()).all()
    active_users = User.query.filter_by(status='active').order_by(User.created_at.desc()).all()
    rejected_users = User.query.filter_by(status='rejected').order_by(User.created_at.desc()).all()
    all_users = User.query.order_by(User.created_at.desc()).all()
    all_condominiums = Condominium.query.order_by(Condominium.name).all()

    return render_template(
        'master/usuarios.html',
        user=user,
        pending_users=pending_users,
        active_users=active_users,
        rejected_users=rejected_users,
        all_users=all_users,
        all_condominiums=all_condominiums
    )

@master_bp.route('/master/usuarios/editar/<int:user_id>', methods=['GET', 'POST'])
@jwt_required()
def master_usuarios_editar(user_id):
    # Placeholder para la lógica de edición
    flash(f"Funcionalidad para editar usuario {user_id} no implementada.", "info")
    return redirect(url_for('master.master_usuarios'))

@master_bp.route('/master/usuarios/eliminar/<int:user_id>', methods=['POST'])
@jwt_required()
def master_usuarios_eliminar(user_id):
    # Placeholder para la lógica de eliminación
    flash(f"Funcionalidad para eliminar usuario {user_id} no implementada.", "info")
    return redirect(url_for('master.master_usuarios'))

@master_bp.route('/master/configuracion', methods=['GET'])
@jwt_required()
def master_configuracion():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    # Aquí puedes agregar la lógica para cargar la configuración global
    return render_template('master/configuracion.html', user=user)

@master_bp.route('/master/usuarios/reaprobar/<int:user_id>', methods=['POST'])
@jwt_required()
def master_usuarios_reaprobar(user_id):
    # Placeholder para la lógica de reaprobación
    flash(f"Funcionalidad para reaprobar usuario {user_id} no implementada.", "info")
    return redirect(url_for('master.master_usuarios'))


@master_bp.route('/master/crear_condominio', methods=['GET', 'POST'])
@jwt_required()
def crear_condominio():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        flash("Acceso denegado – Se requiere rol MASTER", "error")
        return redirect('/dashboard')

    if request.method == 'POST':
        try:
            # Asegurarse de que el admin_user_id es un entero
            admin_id = request.form.get('admin_user_id')
            if not admin_id:
                flash('Debe seleccionar un administrador.', 'error')
                return redirect('/master/crear_condominio')

            new_condo = Condominium(
                name=request.form.get('name'),
                legal_name=request.form.get('legal_name'),
                ruc=request.form.get('ruc'),
                main_street=request.form.get('main_street'),
                cross_street=request.form.get('cross_street'),
                house_number=request.form.get('house_number'),
                city=request.form.get('city'),
                country=request.form.get('country'),
                subdomain=request.form.get('subdomain'),
                status='PENDIENTE_APROBACION',
                admin_user_id=int(admin_id),
                created_by=user.id
            )
            db.session.add(new_condo)
            db.session.commit()
            flash('Condominio creado exitosamente.', 'success')
            return redirect('/master/condominios')
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Error al crear el condominio: {e}")
            flash(f'Error al crear el condominio: {e}', 'error')
            # Volver a cargar los administradores para renderizar el formulario de nuevo
            administradores = User.query.filter(User.role.in_(['ADMIN', 'MASTER'])).all()
            return render_template('master/crear_condominio.html', user=user, administradores=administradores)

    # GET request
    administradores = User.query.filter(User.role.in_(['ADMIN', 'MASTER'])).all()
    return render_template('master/crear_condominio.html', user=user, administradores=administradores)


@master_bp.route('/master/descargar-plantilla-unidades')
@jwt_required()
def descargar_plantilla_unidades():
    user = get_current_user()
    if not user or user.role != 'MASTER':
        return jsonify({"error": "Acceso denegado"}), 403

    output = io.StringIO()
    writer = csv.writer(output)
    
    headers = ['property_number', 'name', 'property_type', 'main_street', 'cross_street', 
               'house_number', 'address_reference', 'latitude', 'longitude', 'building', 
               'floor', 'sector', 'area_m2', 'area_construction_m2', 'bedrooms', 'bathrooms', 
               'parking_spaces', 'front_meters', 'depth_meters', 'topography', 'land_use', 'notes']
    writer.writerow(headers)
    
    examples = [
        ['A-101', 'Apartamento 101', 'apartamento', 'Av. Principal', 'Calle 2', '101', '', '-2.123', '-79.123', 'Torre A', '10', '', '85.5', '75.0', '2', '2', '1', '', '', '', '', ''],
        ['C-25', 'Casa 25', 'casa', 'Av. Las Palmeras', 'Calle Los Pinos', '25', '', '-2.124', '-79.124', '', '', 'Manzana B', '120.0', '100.0', '3', '2', '2', '', '', '', '', '']
    ]
    for row in examples:
        writer.writerow(row)
    
    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=plantilla_unidades.csv"}
    )
