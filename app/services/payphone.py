import requests
from flask import current_app

class PayPhoneService:
    """
    Servicio para interactuar con la API de Botones de Pagos de PayPhone v2.
    """
    
    # URL Base para la API de Botones
    BASE_URL = "https://pay.payphonetodoesposible.com/api"
    
    def __init__(self, condominium):
        self.condo = condominium
        self.config = condominium.payment_config or {}
        self.token = self.config.get('token')
        
        # Validar configuración mínima
        if not self.token:
             # Si no hay token, no podemos operar.
             # No lanzamos error aquí para permitir instanciar y verificar estado,
             # pero los métodos fallarán.
             pass

    def _get_headers(self):
        if not self.token:
            raise ValueError("El condominio no tiene configurado el Token de PayPhone.")
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def prepare_payment(self, amount, client_tx_id, reference, email, document_id):
        """
        Prepara la transacción y obtiene el link de pago.
        
        Args:
            amount (float): Monto en DÓLARES (ej: 10.50). Se convertirá a centavos.
            client_tx_id (str): ID único de transacción generado por nosotros.
            reference (str): Descripción del pago.
            email (str): Email del pagador.
            document_id (str): Cédula del pagador.
        """
        url = f"{self.BASE_URL}/button/Prepare"
        
        # Conversión a centavos (Enteros)
        # PayPhone: amount = total a pagar
        # amountWithoutTax = base 0% (alícuotas no suelen tener IVA)
        amount_cents = int(round(amount * 100))
        
        # Callback URL: Donde PayPhone redirige al usuario tras pagar
        # En desarrollo local sin dominio público, esto fallará si PayPhone intenta validar.
        # Usamos la URL configurada en la app.
        base_url = current_app.config.get('BASE_URL', 'http://localhost:5000')
        response_url = f"{base_url}/pagos/callback"
        
        payload = {
            "responseUrl": response_url,
            "amount": amount_cents,
            "amountWithoutTax": amount_cents,
            "amountWithTax": 0,
            "tax": 0,
            "service": 0,
            "tip": 0,
            "currency": "USD",
            "clientTransactionId": client_tx_id,
            "reference": reference[:100], # PayPhone tiene límite de caracteres
            "email": email,
            "documentId": document_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json() # Retorna { "paymentId": 123, "payWithCard": "https://..." }
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"PayPhone Prepare Error: {str(e)}")
            if hasattr(e, 'response') and e.response:
                 current_app.logger.error(f"PayPhone Response Body: {e.response.text}")
            raise e

    def confirm_payment(self, payment_id, client_tx_id):
        """
        Verifica el estado final del pago usando el ID devuelto por PayPhone.
        """
        url = f"{self.BASE_URL}/button/Confirm"
        
        payload = {
            "id": int(payment_id),
            "clientTxId": client_tx_id
        }
        
        try:
            response = requests.post(url, json=payload, headers=self._get_headers(), timeout=10)
            response.raise_for_status()
            return response.json() # Retorna estado de la transacción
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"PayPhone Confirm Error: {str(e)}")
            raise e

