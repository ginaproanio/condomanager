class BusinessError(Exception):
    """
    Error de negocio base con mensaje amigable para el usuario.
    """
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ValidationError(BusinessError):
    """
    Error de validación de datos de entrada.
    """
    def __init__(self, message, status_code=400):
        super().__init__(message, status_code)

class PaymentError(BusinessError):
    """
    Error específico para procesamiento de pagos.
    """
    def __init__(self, message, status_code=400):
        super().__init__(message, status_code)

class AuthorizationError(BusinessError):
    """
    Error de permisos o autorización.
    """
    def __init__(self, message, status_code=403):
        super().__init__(message, status_code)

class ResourceNotFoundError(BusinessError):
    """
    Error cuando un recurso no existe.
    """
    def __init__(self, message, status_code=404):
        super().__init__(message, status_code)

