from flask import (
    Blueprint, render_template, redirect,
    current_app, flash, Response, jsonify, request
)
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import Condominium, User, db
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
