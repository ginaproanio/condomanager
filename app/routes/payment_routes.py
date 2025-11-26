from flask import Blueprint, render_template, redirect, request, flash, current_app, url_for
from flask_jwt_extended import jwt_required
from app.auth import get_current_user
from app.models import db, Payment, Condominium, User
from app.services.payment_service import PaymentService
from app.exceptions import BusinessError
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

    try:
        redirect_url = PaymentService.initiate_payphone_payment(
            user, 
            condominium_id, 
            request.form
        )
        return redirect(redirect_url)
    except BusinessError as e:
        flash(e.message, "error")
        return redirect(url_for('user.dashboard'))
    except Exception as e:
        current_app.logger.error(f"Error iniciando pago: {e}")
        flash("Hubo un error al conectar con la pasarela de pagos. Intenta más tarde.", "error")
        return redirect(url_for('user.dashboard'))

@payment_bp.route('/pagos/callback', methods=['GET'])
def callback_pago():
    """
    Ruta de retorno donde PayPhone redirige al usuario después de pagar (o cancelar).
    """
    payment_id = request.args.get('id')
    client_tx_id = request.args.get('clientTransactionId')
    
    if not payment_id or not client_tx_id:
        flash("Respuesta de pago inválida.", "error")
        return redirect(url_for('user.dashboard'))
        
    try:
        payment = PaymentService.process_payphone_callback(payment_id, client_tx_id)
        
        if payment.status == 'APPROVED':
            flash(f"✅ Pago de ${payment.amount} realizado con ÉXITO. Referencia: {payment.id}", "success")
        elif payment.status == 'CANCELED':
            flash("El pago fue cancelado.", "warning")
        else:
            flash("El pago no pudo ser procesado o fue rechazado.", "error")
            
    except BusinessError as e:
        flash(e.message, "error")
    except Exception as e:
        current_app.logger.error(f"Error verificando pago: {e}")
        flash("Error al verificar el estado del pago. Por favor revisa tu historial.", "warning")
        
    return redirect(url_for('user.dashboard'))
