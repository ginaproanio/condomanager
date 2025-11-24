from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_jwt_extended import jwt_required
from app.models import db, Condominium, PettyCashTransaction
from app.auth import get_current_user
from app.decorators import condominium_admin_required
from datetime import datetime
import os
from werkzeug.utils import secure_filename

petty_cash_bp = Blueprint('petty_cash', __name__)

@petty_cash_bp.route('/admin/condominio/<int:condominium_id>/caja-chica', methods=['GET'])
@condominium_admin_required
def index(condominium_id):
    """
    Panel principal de Caja Chica.
    Muestra el saldo actual y el historial de movimientos.
    """
    condo = Condominium.query.get_or_404(condominium_id)
    
    transactions = PettyCashTransaction.query.filter_by(condominium_id=condominium_id).order_by(PettyCashTransaction.transaction_date.desc()).all()
    
    # Calcular saldo
    balance = sum(t.amount for t in transactions)
    
    return render_template('admin/petty_cash.html', 
                           condominium=condo, 
                           transactions=transactions, 
                           balance=balance)

@petty_cash_bp.route('/admin/condominio/<int:condominium_id>/caja-chica/nuevo', methods=['POST'])
@condominium_admin_required
def nuevo_movimiento(condominium_id):
    """
    Registra un nuevo movimiento (ingreso o egreso).
    """
    condo = Condominium.query.get_or_404(condominium_id)
    user = get_current_user()
    
    description = request.form.get('description')
    amount_str = request.form.get('amount')
    type_tx = request.form.get('type') # 'INCOME' o 'EXPENSE'
    category = request.form.get('category')
    date_str = request.form.get('date')
    
    if not all([description, amount_str, type_tx, category]):
        flash("Faltan campos obligatorios.", "error")
        return redirect(url_for('petty_cash.index', condominium_id=condominium_id))
    
    try:
        amount = float(amount_str)
        if type_tx == 'EXPENSE':
            amount = -abs(amount) # Asegurar negativo
        else:
            amount = abs(amount) # Asegurar positivo
            
        tx_date = datetime.utcnow()
        if date_str:
            tx_date = datetime.strptime(date_str, '%Y-%m-%d')
            
        # Procesar archivo
        receipt_url = None
        if 'receipt_file' in request.files:
            file = request.files['receipt_file']
            if file.filename != '':
                filename = secure_filename(f"petty_{condominium_id}_{int(datetime.utcnow().timestamp())}_{file.filename}")
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
            condominium_id=condominium_id
        )
        
        db.session.add(tx)
        db.session.commit()
        flash("Movimiento registrado correctamente.", "success")
        
    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar: {str(e)}", "error")
        
    return redirect(url_for('petty_cash.index', condominium_id=condominium_id))

