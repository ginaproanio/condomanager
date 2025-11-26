import os
from flask import abort

def validate_file(file, allowed_extensions=None, allowed_mimetypes=None):
    """
    Valida un archivo subido por extensión y tipo MIME.
    Lanza abort(400) si falla la validación.
    """
    if not file:
        return
        
    filename = file.filename.lower()
    
    # 1. Validar Extensión
    if allowed_extensions:
        if not '.' in filename or \
           filename.rsplit('.', 1)[1] not in allowed_extensions:
            abort(400, description=f"Tipo de archivo no permitido. Extensiones válidas: {', '.join(allowed_extensions)}")

    # 2. Validar MIME Type (Content-Type header sent by browser)
    # Nota: Para mayor seguridad, se debería usar python-magic para inspeccionar el contenido real del archivo
    if allowed_mimetypes:
        if file.mimetype not in allowed_mimetypes:
            abort(400, description=f"Formato de archivo inválido ({file.mimetype}).")

def validate_amount(amount):
    """
    Valida que un monto sea un número positivo.
    """
    try:
        val = float(amount)
        if val <= 0:
            abort(400, description="El monto debe ser mayor a 0.")
        return val
    except (ValueError, TypeError):
        abort(400, description="Monto inválido.")

