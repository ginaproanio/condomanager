from app import db
from app.models import Payment, Condominium
from app.utils.validation import validate_file, validate_amount
from werkzeug.utils import secure_filename
import os
from datetime import datetime
from flask import current_app
import uuid
from app.services.payphone import PayPhoneService
from app.exceptions import PaymentError, ValidationError, ResourceNotFoundError, BusinessError
import structlog

logger = structlog.get_logger()

class PaymentService:
    @staticmethod
    def report_manual_payment(user_id, condo_id, form_data, file):
        """
        Registra un pago manual (transferencia) con comprobante.
        """
        if not condo_id:
            raise BusinessError("No tienes un condominio asignado para reportar pagos.")

        # Validar archivo
        if not file or file.filename == '':
            raise ValidationError("No seleccionaste ningún archivo.")
        
        try:
            validate_file(
                file, 
                allowed_extensions=['pdf', 'jpg', 'jpeg', 'png'],
                allowed_mimetypes=['application/pdf', 'image/jpeg', 'image/png']
            )
        except ValueError as e:
            raise ValidationError(str(e))

        amount_str = form_data.get('amount', '0').replace(',', '.')
        try:
            amount = validate_amount(amount_str)
        except ValueError as e:
             raise ValidationError(str(e))

        filename = secure_filename(f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{user_id}_{file.filename}")
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'payments')
        os.makedirs(upload_folder, exist_ok=True)
        
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)
        
        # Check if user has unit
        from app.models import User # Import locally to avoid circular dependency if any
        user = User.query.get(user_id)
        unit_id = user.unit_id if user.unit_id else None

        new_payment = Payment(
            amount=amount,
            amount_with_tax=amount, 
            currency='USD',
            description=form_data.get('description'),
            status='PENDING_REVIEW',
            payment_method='TRANSFER',
            proof_of_payment=filename,
            user_id=user_id,
            condominium_id=condo_id,
            unit_id=unit_id,
            created_at=datetime.utcnow()
        )
        
        try:
            db.session.add(new_payment)
            db.session.commit()
            logger.info("Pago manual reportado", user_id=user_id, amount=amount, condo_id=condo_id)
        except Exception as e:
             db.session.rollback()
             logger.error("Error DB al registrar pago manual", error=str(e), user_id=user_id)
             raise PaymentError("Error al guardar el reporte de pago.")

        return new_payment

    @staticmethod
    def initiate_payphone_payment(user, condominium_id, form_data):
        """
        Inicia un proceso de pago con PayPhone.
        """
        condominium = Condominium.query.get(condominium_id)
        if not condominium:
            raise ResourceNotFoundError("Condominio no encontrado.")
        
        if not condominium.payment_config or not condominium.payment_config.get('token'):
            raise BusinessError("Este condominio no tiene configurada la pasarela de pagos.")

        try:
             amount = validate_amount(form_data.get('amount', 0))
        except ValueError as e:
             raise ValidationError(str(e))

        description = form_data.get('description', 'Pago de Alícuota')
        client_tx_id = str(uuid.uuid4())

        payment = Payment(
            amount=amount,
            amount_with_tax=amount,
            tax=0,
            description=description,
            client_transaction_id=client_tx_id,
            user_id=user.id,
            unit_id=user.unit_id if user.unit_id else None,
            condominium_id=condominium.id,
            status='PENDING'
        )
        db.session.add(payment)
        db.session.commit()

        payphone = PayPhoneService(condominium)
        try:
            response = payphone.prepare_payment(
                amount=amount,
                client_tx_id=client_tx_id,
                reference=description,
                email=user.email,
                document_id=user.cedula
            )
        except Exception as e:
            # Logged inside PayPhoneService usually, but we catch here to raise custom error
            logger.error("PayPhone prepare_payment error", error=str(e), user_id=user.id)
            raise PaymentError("Error al conectar con la pasarela de pagos.")
        
        payment_id_api = response.get('paymentId')
        if not payment_id_api:
             raise PaymentError("La pasarela no devolvió un paymentId válido.")
             
        payment.payphone_transaction_id = str(payment_id_api)
        db.session.commit()
        
        return response.get('payWithCard')

    @staticmethod
    def process_payphone_callback(payment_id, client_tx_id):
        """
        Procesa la respuesta de PayPhone.
        """
        payment = Payment.query.filter_by(client_transaction_id=client_tx_id).first()
        if not payment:
            raise ResourceNotFoundError("Transacción no encontrada.")
            
        if payment.status == 'APPROVED':
            return payment # Ya procesado

        condominium = Condominium.query.get(payment.condominium_id)
        payphone = PayPhoneService(condominium)
        
        try:
            verification = payphone.confirm_payment(payment_id, client_tx_id)
        except Exception as e:
            logger.error("PayPhone confirm_payment error", error=str(e), payment_id=payment_id)
            raise PaymentError("Error al verificar el pago con la pasarela.")
        
        status = verification.get('transactionStatus')
        payment.response_json = verification
        
        if status == 'Approved':
            payment.status = 'APPROVED'
            logger.info("Pago PayPhone Aprobado", payment_id=payment.id, amount=payment.amount)
        elif status == 'Canceled':
            payment.status = 'CANCELED'
            logger.info("Pago PayPhone Cancelado", payment_id=payment.id)
        else:
            payment.status = 'REJECTED'
            logger.info("Pago PayPhone Rechazado", payment_id=payment.id, status=status)
            
        db.session.commit()
        return payment
