from app import db
from app.models import User
from app.utils.validation import validate_file
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.backends import default_backend
from app.exceptions import ValidationError, ResourceNotFoundError, BusinessError
import hashlib
import structlog

logger = structlog.get_logger()

class UserService:
    @staticmethod
    def update_social_profiles(user_id, form_data):
        user = User.query.get(user_id)
        if not user:
            logger.error("Usuario no encontrado para update_social_profiles", user_id=user_id)
            raise ResourceNotFoundError("Usuario no encontrado")

        user.twitter_profile = form_data.get('twitter_profile', '').strip()
        user.facebook_profile = form_data.get('facebook_profile', '').strip()
        user.instagram_profile = form_data.get('instagram_profile', '').strip()
        user.linkedin_profile = form_data.get('linkedin_profile', '').strip()
        user.tiktok_profile = form_data.get('tiktok_profile', '').strip()
        
        try:
            db.session.commit()
            logger.info("Perfiles sociales actualizados", user_id=user_id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error DB al actualizar perfil social", error=str(e), user_id=user_id)
            raise BusinessError("Error al actualizar perfil social")
            
        return user

    @staticmethod
    def upload_certificate(user_id, file, password):
        user = User.query.get(user_id)
        if not user:
            raise ResourceNotFoundError("Usuario no encontrado")

        if not file:
            raise ValidationError("No se seleccionó ningún archivo")
            
        # Validar extensión
        try:
            validate_file(file, allowed_extensions=['p12', 'pfx'])
        except ValueError as e:
             raise ValidationError(str(e))

        if not password:
            raise ValidationError("Debes ingresar la contraseña del certificado para poder validarlo.")

        # Leer el contenido binario
        file.seek(0) # Asegurar inicio
        file_data = file.read()
        
        # --- VALIDACIÓN CRIPTOGRÁFICA REAL ---
        try:
            pkcs12.load_key_and_certificates(
                file_data,
                password.encode(),
                backend=default_backend()
            )
        except ValueError:
            logger.warning("Fallo validación contraseña certificado", user_id=user_id)
            raise ValidationError("Error de Validación: La contraseña ingresada es INCORRECTA para este certificado.")
        except Exception as e:
            logger.error("Fallo validación archivo certificado", error=str(e), user_id=user_id)
            raise ValidationError(f"Error de Validación: El archivo del certificado está dañado o no es válido. Detalle: {str(e)}")

        # Guardar en base de datos
        user.signature_certificate = file_data
        user.signature_cert_password_hash = hashlib.sha256(password.encode()).hexdigest()
        user.has_electronic_signature = True
        
        try:
            db.session.commit()
            logger.info("Certificado subido exitosamente", user_id=user_id)
        except Exception as e:
            db.session.rollback()
            logger.error("Error DB al guardar certificado", error=str(e), user_id=user_id)
            raise BusinessError("Error al guardar el certificado")
            
        return user
