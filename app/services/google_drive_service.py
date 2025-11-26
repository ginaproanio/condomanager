import os
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from flask import current_app, url_for

class GoogleDriveService:
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    
    # Estructura de carpetas definida por negocio
    REQUIRED_FOLDERS = [
        "Actas", "Convocatorias", "Circulares", "Oficios", "Memos",
        "Reglamento", "Gastos", "Contratos", "Planos", "Fotos", "Otros"
    ]

    def __init__(self, condominium=None):
        self.condominium = condominium
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.environ.get('GOOGLE_REDIRECT_URI') # Debe ser HTTPS en prod

    def get_auth_flow(self):
        """Inicia el flujo OAuth para obtener la URL de autorización."""
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES
        )
        # En local puede ser http, en prod https. Forzar redirect_uri correcta.
        flow.redirect_uri = self.redirect_uri
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent' # Importante para obtener refresh_token
        )
        return authorization_url, state

    def connect_and_setup(self, auth_code):
        """
        Canjea el código por tokens y crea la estructura inicial.
        Retorna un dict con los datos para actualizar el modelo Condominium.
        """
        flow = Flow.from_client_config(
            {
                "web": {
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                }
            },
            scopes=self.SCOPES
        )
        flow.redirect_uri = self.redirect_uri
        
        # Canjear código
        flow.fetch_token(code=auth_code)
        creds = flow.credentials
        
        # Servicio de Drive
        service = build('drive', 'v3', credentials=creds)
        
        # 1. Crear Carpeta Raíz
        folder_name = f"{self.condominium.document_code_prefix or 'CONDO'} - {self.condominium.name}"
        root_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        root_file = service.files().create(body=root_metadata, fields='id').execute()
        root_id = root_file.get('id')
        
        # 2. Crear Subcarpetas
        folders_map = {}
        for subfolder_name in self.REQUIRED_FOLDERS:
            file_metadata = {
                'name': subfolder_name,
                'mimeType': 'application/vnd.google-apps.folder',
                'parents': [root_id]
            }
            file = service.files().create(body=file_metadata, fields='id').execute()
            folders_map[subfolder_name] = file.get('id')
            
        # 3. Obtener email (opcional, para registro)
        # Necesitaríamos scope userinfo.email, pero asumimos éxito con drive
        
        return {
            'refresh_token': creds.refresh_token,
            'root_id': root_id,
            'folders_map': folders_map
        }

    def get_service_instance(self):
        """Reconstruye el servicio usando el refresh token del condominio."""
        if not self.condominium or not self.condominium.drive_refresh_token:
            raise ValueError("Condominio no tiene credenciales de Drive configuradas.")
            
        creds = Credentials(
            None, # access_token (se regenera)
            refresh_token=self.condominium.drive_refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=self.client_id,
            client_secret=self.client_secret
        )
        return build('drive', 'v3', credentials=creds)

    def upload_file(self, file_stream, filename, folder_category="Otros", mime_type='application/pdf'):
        """Sube un archivo a la categoría especificada."""
        service = self.get_service_instance()
        
        # Determinar ID de carpeta destino
        folders_map = self.condominium.drive_folders_map or {}
        parent_id = folders_map.get(folder_category)
        
        if not parent_id:
            # Fallback: usar root o carpeta 'Otros' si existe, sino Root
            parent_id = folders_map.get("Otros") or self.condominium.drive_root_folder_id
            
        if not parent_id:
            raise ValueError("No se encontró carpeta destino válida en Drive.")

        file_metadata = {
            'name': filename,
            'parents': [parent_id]
        }
        
        media = MediaIoBaseUpload(file_stream, mimetype=mime_type, resumable=True)
        
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink, webContentLink'
        ).execute()
        
        return file

    def list_files_in_folder(self, folder_category):
        """Lista archivos en una categoría."""
        service = self.get_service_instance()
        folders_map = self.condominium.drive_folders_map or {}
        folder_id = folders_map.get(folder_category)
        
        if not folder_id:
            return []
            
        query = f"'{folder_id}' in parents and trashed = false"
        results = service.files().list(
            q=query,
            pageSize=50,
            fields="nextPageToken, files(id, name, webViewLink, thumbnailLink)"
        ).execute()
        
        return results.get('files', [])



