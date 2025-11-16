from flask import request, current_app

def get_tenant():
    # Verificar si estamos en contexto de request
    if not request or not hasattr(request, 'host'):
        return 'puntablanca'  # Default seguro
    
    host = request.host.lower()
    if 'puntablancaecuador.com' in host:
        return 'puntablanca'
    if 'lascolinas.com' in host:
        return 'lascolinas'
    return 'puntablanca'