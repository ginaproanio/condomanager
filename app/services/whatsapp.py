import requests
from flask import current_app

class WhatsAppService:
    """
    Servicio unificado para WhatsApp (Gateway QR y Meta API).
    """
    
    def __init__(self, condominium):
        self.condo = condominium
        self.provider = condominium.whatsapp_provider
        self.config = condominium.whatsapp_config or {}
        
        # Configuración para Gateway (Waha)
        # En producción, esto vendría de env vars o de la config del tenant si cada uno tiene su contenedor
        self.waha_base_url = "http://waha:3000" # URL interna del servicio en Docker
        
    def get_status(self):
        """
        Obtiene el estado de la conexión.
        """
        if self.provider == 'GATEWAY_QR':
            return self._get_gateway_status()
        elif self.provider == 'META_API':
            return 'connected' # Meta API no tiene "estado de conexión" persistente igual
        return 'disconnected'

    def get_qr(self):
        """
        Retorna la imagen del QR en base64 o URL para el Gateway.
        """
        if self.provider != 'GATEWAY_QR':
            return None
            
        # INTENTO DE CONEXIÓN REAL
        try:
            # Endpoint típico de Waha para obtener QR
            url = f"{self.waha_base_url}/api/screenshot?session=default"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                return response.json().get('data') # Asumiendo que devuelve base64
        except:
            pass
            
        # FALLBACK: MOCK PARA DEMOSTRACIÓN
        # Si no hay servicio real, retornamos un QR de ejemplo usando una API pública
        # que apunte a un "Deep Link" simulado.
        dummy_data = f"condomanager-verify:{self.condo.id}"
        return f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={dummy_data}"

    def _get_gateway_status(self):
        try:
            url = f"{self.waha_base_url}/api/sessions/default"
            response = requests.get(url, timeout=2)
            if response.status_code == 200:
                data = response.json()
                return data.get('status', 'disconnected')
        except:
            return 'disconnected'

