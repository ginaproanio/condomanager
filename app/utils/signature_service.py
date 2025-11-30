from abc import ABC, abstractmethod
import requests
import base64
import json
import os
from flask import current_app
import hashlib

# --- ABSTRACT STRATEGY ---
class SignatureProvider(ABC):
    @abstractmethod
    def create_flow(self, pdf_path, user, document_title):
        """Inicia un flujo de firma y retorna el ID del flujo (externo)."""
        pass

    @abstractmethod
    def get_flow_details(self, flow_id):
        """Consulta los detalles de un flujo dado su ID."""
        pass

    @abstractmethod
    def download_file(self, remote_path):
        """Descarga el archivo firmado."""
        pass

# --- CONCRETE STRATEGY: NEXXIT / UANATACA / ONESHOT ---
class NexxitOneshotProvider(SignatureProvider):
    BASE_URL = "https://wfdev.nexxit.dev"
    DEFAULT_FLOW_TYPE = "-NXk9JhsCP7KvP9eQa_4_pb" # Default template

    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "x-nexxit-key": self.api_key,
            "Content-Type": "application/json"
        }

    def create_flow(self, pdf_path, user, document_title, flow_type=None):
        if not flow_type:
            flow_type = self.DEFAULT_FLOW_TYPE

        try:
            with open(pdf_path, "rb") as pdf_file:
                pdf_base64 = base64.b64encode(pdf_file.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error leyendo el PDF: {str(e)}")

        # Payload específico de Nexxit/Oneshot
        payload = {
            "flowType": flow_type,
            "userData": {
                "cedula": user.cedula,
                "email": user.email,
                "nombres": user.first_name,
                "apellido": user.last_name,
                "apellido2": "",
                "telef": user.cellphone or "0999999999",
                "dirDom": f"{user.city or 'Ecuador'}",
                "ciudad": user.city or "Quito",
                "prov": "Pichincha",
                "pais": "EC"
            },
            "customData": {
                "subject": f"Firma Documento: {document_title}",
                "msg": f"Estimado(a) {user.first_name}, se requiere su firma electrónica en el documento: {document_title}",
                "channel": "ninguno",
                "channelNotify": "no",
                "endpointNotify": "si",
                "enforceDNI": "si",
                "qrString": f"CondoManager - {document_title}",
                "transactionId": f"DOC-{document_title[:20].replace(' ', '_')}",
                "files": [{
                    "base64": pdf_base64,
                    "filename": f"{document_title[:20].replace(' ', '_')}.pdf",
                    "markQR": False,
                    "page": 0,
                    "posX": 50,
                    "posY": 50
                }]
            }
        }

        try:
            response = requests.post(f"{self.BASE_URL}/wf/flow", json=payload, headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Nexxit API Error (Create Flow): {str(e)}")
            if e.response:
                current_app.logger.error(f"Response Body: {e.response.text}")
            raise

    def get_flow_details(self, flow_id):
        try:
            response = requests.get(f"{self.BASE_URL}/wf/flow-files/{flow_id}", headers=self.headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Nexxit API Error (Get Details): {str(e)}")
            raise

    def download_file(self, remote_path):
        payload = {"path": remote_path}
        try:
            response = requests.post(f"{self.BASE_URL}/wf/file", json=payload, headers=self.headers, timeout=60)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Nexxit API Error (Download File): {str(e)}")
            raise

# --- FACTORY ---
class SignatureServiceFactory:
    @staticmethod
    def get_provider(condominium) -> SignatureProvider:
        """
        Retorna la instancia del proveedor configurado.
        Soporta Nexxit (externo) y Local (interno).
        """
        if not condominium:
            return None
            
        # La configuración del proveedor se toma de los settings del condominio
        provider_type = 'local' # Default a 'local' si no hay nada configurado
        if condominium.signature_provider_config:
            provider_type = condominium.signature_provider_config.get('type', 'local')

        if provider_type == 'NEXXIT':
            api_key = None
            if condominium.signature_provider_config:
                api_key = condominium.signature_provider_config.get('api_key')
            
            # Fallback seguro para Punta Blanca usando una Variable de Entorno
            if not api_key and condominium.subdomain == 'puntablanca':
                api_key = os.environ.get('PUNTABLANCA_NEXXIT_KEY')
            
            if api_key:
                return NexxitOneshotProvider(api_key)
        
        elif provider_type == 'local':
            return LocalSignatureProvider()
                
        return None
