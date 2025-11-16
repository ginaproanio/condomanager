from flask import request

def get_tenant():
    """Obtiene el tenant del subdominio o usa uno por defecto"""
    try:
        # Si hay contexto de request (durante peticiones web)
        if request and hasattr(request, 'host'):
            host = request.host
            if 'localhost' in host or 'railway' in host:
                return 'puntablanca'
            # Extraer subdominio: admin.condomanager.com → admin
            parts = host.split('.')
            if len(parts) > 2:
                return parts[0]
            return 'puntablanca'
    except RuntimeError:
        # No hay contexto de request (durante inicialización)
        pass
    
    return 'puntablanca'  # Valor por defecto