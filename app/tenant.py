from flask import request, current_app

def get_tenant():
    """Obtiene el tenant del subdominio o usa uno por defecto"""
    try:
        # Si hay contexto de request (durante peticiones web)
        if request:
            host = request.host
            # Forzar 'puntablanca' en desarrollo local y en el entorno de pruebas de Railway
            if 'localhost' in host or 'railway.app' in host:
                return 'puntablanca'
            # Extraer subdominio: admin.condomanager.com → admin
            parts = host.split('.') 
            if len(parts) > 2:
                return parts[0]
            return 'puntablanca'
    except RuntimeError:
        # No hay contexto de request (durante inicialización)
        # Esto es normal al inicio de la aplicación o en tareas en segundo plano
        pass
    except Exception as e:
        # Captura cualquier otra excepción inesperada durante la obtención del tenant
        if request:
            current_app.logger.error(f"Error inesperado al obtener el tenant del host {request.host}: {e}")
        else:
            current_app.logger.error(f"Error inesperado al obtener el tenant (sin contexto de request): {e}")

    return 'puntablanca'  # Valor por defecto