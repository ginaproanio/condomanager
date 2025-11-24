from flask import Blueprint, render_template, redirect, request, flash, current_app, url_for
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import db, Payment, Condominium, User
from app.services.payphone import PayPhoneService
import uuid

payment_bp = Blueprint('payment', __name__)

@payment_bp.route('/pagos/iniciar', methods=['POST'])
@jwt_required()
def iniciar_pago():
    user = get_current_user()
    if not user:
        flash("Debes iniciar sesión para realizar pagos.", "error")
        return redirect(url_for('public.login'))

    # Obtener condominio del usuario (asumimos que está en uno)
    # Prioridad: Unidad asignada -> Tenant del usuario
    condominium_id = None
    if user.unit and user.unit.condominium_id:
        condominium_id = user.unit.condominium_id
    elif user.tenant:
        condo = Condominium.query.filter_by(subdomain=user.tenant).first()
        if condo:
            condominium_id = condo.id
            
    if not condominium_id:
        flash("No estás asignado a ningún condominio válido para realizar pagos.", "error")
        return redirect(url_for('user.dashboard'))

    condominium = Condominium.query.get(condominium_id)
    
    if not condominium:
        flash("Condominio no encontrado.", "error")
        return redirect(url_for('user.dashboard'))
    
    # Verificar si el condominio tiene configurado PayPhone
    if not condominium.payment_config or not condominium.payment_config.get('token'):
        flash("Este condominio no tiene configurada la pasarela de pagos. Contacta a la administración.", "warning")
        return redirect(url_for('user.dashboard'))

    # Datos del formulario
    try:
        amount = float(request.form.get('amount', 0))
        description = request.form.get('description', 'Pago de Alícuota')
        
        if amount <= 0:
            flash("El monto debe ser mayor a 0.", "warning")
            return redirect(url_for('user.pagos')) # Asumiendo que existe esta vista
            
    except ValueError:
        flash("Monto inválido.", "error")
        return redirect(url_for('user.dashboard'))

    # Generar ID único de transacción para nosotros
    client_tx_id = str(uuid.uuid4())

    # Crear registro preliminar en BD
    payment = Payment(
        amount=amount,
        amount_with_tax=amount, # Asumimos 0 impuestos por ahora para alícuotas
        tax=0,
        description=description,
        client_transaction_id=client_tx_id,
        user_id=user.id,
        unit_id=user.unit_id if user.unit else None,
        condominium_id=condominium.id,
        status='PENDING'
    )
    db.session.add(payment)
    db.session.commit()

    # Llamar a PayPhone
    payphone = PayPhoneService(condominium)
    try:
        # email y cedula del usuario para la factura/recibo de PayPhone
        user_email = user.email
        user_cedula = user.cedula
        
        response = payphone.prepare_payment(
            amount=amount,
            client_tx_id=client_tx_id,
            reference=description,
            email=user_email,
            document_id=user_cedula
        )
        
        # Guardar el ID de PayPhone
        payment.payphone_transaction_id = str(response.get('paymentId'))
        db.session.commit()
        
        # Redirigir a la pasarela
        redirect_url = response.get('payWithCard')
        return redirect(redirect_url)
        
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error iniciando pago: {e}")
        flash("Hubo un error al conectar con la pasarela de pagos. Intenta más tarde.", "error")
        return redirect(url_for('user.dashboard'))

@payment_bp.route('/pagos/callback', methods=['GET'])
def callback_pago():
    """
    Ruta de retorno donde PayPhone redirige al usuario después de pagar (o cancelar).
    Aquí verificamos el estado final de la transacción.
    Parámetros que envía PayPhone: id (paymentId), clientTransactionId
    """
    payment_id = request.args.get('id')
    client_tx_id = request.args.get('clientTransactionId')
    
    if not payment_id or not client_tx_id:
        flash("Respuesta de pago inválida.", "error")
        return redirect(url_for('user.dashboard'))
        
    # Buscar el pago en nuestra BD
    payment = Payment.query.filter_by(client_transaction_id=client_tx_id).first()
    if not payment:
        flash("Transacción no encontrada.", "error")
        return redirect(url_for('user.dashboard'))
        
    # Si ya estaba aprobado, no hacemos nada
    if payment.status == 'APPROVED':
        flash("Este pago ya fue procesado exitosamente.", "info")
        return redirect(url_for('user.dashboard'))

    condominium = Condominium.query.get(payment.condominium_id)
    payphone = PayPhoneService(condominium)
    
    try:
        # Verificar estado con la API (Server-to-Server check)
        # Esto es más seguro que confiar solo en el redirect
        verification = payphone.confirm_payment(payment_id, client_tx_id)
        
        status = verification.get('transactionStatus')
        payment.response_json = verification # Guardar toda la data para auditoría
        
        if status == 'Approved':
            payment.status = 'APPROVED'
            db.session.commit()
            flash(f"✅ Pago de ${payment.amount} realizado con ÉXITO. Referencia: {payment.id}", "success")
        elif status == 'Canceled':
            payment.status = 'CANCELED'
            db.session.commit()
            flash("El pago fue cancelado.", "warning")
        else:
            payment.status = 'REJECTED'
            db.session.commit()
            flash("El pago no pudo ser procesado o fue rechazado.", "error")
            
    except Exception as e:
        current_app.logger.error(f"Error verificando pago {payment.id}: {e}")
        flash("Error al verificar el estado del pago. Por favor revisa tu historial.", "warning")
        
    return redirect(url_for('user.dashboard'))

