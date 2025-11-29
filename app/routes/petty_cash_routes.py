from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, g
from flask_jwt_extended import jwt_required
from app.models import db, PettyCashTransaction
from app.auth import get_current_user
from app.decorators import admin_tenant_required
from app.utils.validation import validate_file, validate_amount
import datetime
import os
from werkzeug.utils import secure_filename

petty_cash_bp = Blueprint('petty_cash', __name__)

@petty_cash_bp.route('/admin/caja-chica', methods=['GET'])
@admin_tenant_required
def index():
    """
    Panel principal de Caja Chica.
    Muestra el saldo actual y el historial de movimientos.
    """
    condo = g.condominium
    
    transactions = PettyCashTransaction.query.filter_by(condominium_id=condo.id)\
        .order_by(PettyCashTransaction.transaction_date.desc()).all()
    
    # Calcular saldo
    balance = sum(t.amount for t in transactions)
    
    # Fecha actual para el input date
    now_date = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    
    return render_template('admin/petty_cash.html', 
                           condominium=condo, 
                           transactions=transactions, 
                           balance=balance, 
                           now_date=now_date)

@petty_cash_bp.route('/admin/caja-chica/nuevo', methods=['POST'])
@admin_tenant_required
def nuevo_movimiento():
    """
    Registra un nuevo movimiento (ingreso o egreso).
    """
    condo = g.condominium
    user = get_current_user()
    
    description = request.form.get('description')
    amount_str = request.form.get('amount')
    type_tx = request.form.get('type') # 'INCOME' o 'EXPENSE'
    category = request.form.get('category')
    date_str = request.form.get('date')
    
    if not all([description, amount_str, type_tx, category]):
        flash("Faltan campos obligatorios.", "error")
        return redirect(url_for('petty_cash.index'))
    
    try:
        # VALIDACIÓN BACKEND: Monto Positivo
        base_amount = validate_amount(amount_str)
        
        if type_tx == 'EXPENSE':
            amount = -abs(base_amount) # Asegurar negativo
        else:
            amount = abs(base_amount) # Asegurar positivo
            
        tx_date = datetime.datetime.utcnow()
        if date_str:
            try:
                tx_date = datetime.datetime.strptime(date_str, '%Y-%m-%d')
            except ValueError:
                flash("Formato de fecha inválido", "error")
                return redirect(url_for('petty_cash.index'))
            
        # Procesar archivo
        receipt_url = None
        if 'receipt_file' in request.files:
            file = request.files['receipt_file']
            if file.filename != '':
                # VALIDACIÓN BACKEND: Extensión y MIME Type
                try:
                    validate_file(
                        file, 
                        allowed_extensions=['jpg', 'jpeg', 'png', 'pdf'],
                        allowed_mimetypes=['image/jpeg', 'image/png', 'application/pdf']
                    )
                except Exception as e:
                    flash(f"Archivo inválido: {e.description if hasattr(e, 'description') else str(e)}", "error")
                    return redirect(url_for('petty_cash.index'))

                filename = secure_filename(f"petty_{condo.id}_{int(datetime.datetime.utcnow().timestamp())}_{file.filename}")
                upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'petty_cash')
                os.makedirs(upload_folder, exist_ok=True)
                file.save(os.path.join(upload_folder, filename))
                receipt_url = f"uploads/petty_cash/{filename}"

        tx = PettyCashTransaction(
            description=description,
            amount=amount,
            category=category,
            transaction_date=tx_date,
            receipt_url=receipt_url,
            created_by=user.id,
            condominium_id=condo.id
        )
        
        db.session.add(tx)
        db.session.commit()
        flash("Movimiento registrado correctamente.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar: {e.description if hasattr(e, 'description') else str(e)}", "error")
        
    return redirect(url_for('petty_cash.index'))
