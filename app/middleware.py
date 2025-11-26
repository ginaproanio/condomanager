from flask import request, g, abort, current_app
from app.models import Condominium

def init_tenant_middleware(app):
    @app.before_request
    def resolve_tenant():
        # 0. Excepciones para rutas públicas/estáticas que no requieren contexto de tenant
        if request.endpoint in ['static', 'public.home', 'public.login', 'public.register', 'public.demo_request', 'public.logout']:
            return

        host = request.headers.get('Host', '')
        
        # 1. Detectar Subdominio
        subdomain = None
        
        # Soporte para desarrollo local o Railway (dominio principal)
        if 'localhost' in host or 'railway.app' in host:
            # En desarrollo, permitimos anular el tenant vía query param
            # Esto facilita probar diferentes tenants sin configurar DNS local
            tenant_param = request.args.get('tenant')
            if tenant_param:
                subdomain = tenant_param
        else:
            # En producción, extraemos el subdominio real
            parts = host.split('.')
            if len(parts) > 2: # ej: demo.condomanager.com -> parts=['demo', 'condomanager', 'com']
                subdomain = parts[0]

        # 2. Cargar Condominio (Tenant)
        g.condominium = None
        g.environment = 'production' # Default seguro

        if subdomain:
            # BÚSQUEDA (Aquí se podría agregar caché Redis en el futuro)
            tenant = Condominium.query.filter_by(subdomain=subdomain).first()
            
            if not tenant:
                # Si hay subdominio pero no existe el tenant, es un 404
                abort(404, description="Condominio no encontrado")
            
            g.condominium = tenant
            g.environment = tenant.environment # 'production', 'demo', 'internal'

            # 3. LÓGICA DE AISLAMIENTO DE ENTORNOS
            # Si es un entorno 'demo' o 'internal', se pueden aplicar reglas extra aquí
            if tenant.environment == 'internal':
                # Podríamos restringir acceso por IP aquí
                pass

        else:
            # Estamos en el dominio raíz (www o landing page)
            # No hay g.condominium
            pass

    @app.before_request
    def bridge_csrf_form_to_header():
        """
        Puente para formularios HTML estándar (POST).
        Toma el 'csrf_token' del body y lo inyecta en el header X-CSRF-TOKEN
        para que Flask-JWT-Extended lo valide.
        """
        # Solo interceptamos métodos que modifican estado
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            # Si Flask-JWT-Extended busca el header X-CSRF-TOKEN y no está...
            if "X-CSRF-TOKEN" not in request.headers:
                # Buscamos si viene en el formulario
                token = request.form.get("csrf_token")
                if token:
                    # INYECCIÓN: Simulamos que el navegador envió el header
                    # Flask construye request.headers a partir de request.environ
                    request.environ["HTTP_X_CSRF_TOKEN"] = token

    @app.context_processor
    def inject_tenant_context():
        # Inyectar el token CSRF desde la cookie para usarlo en formularios
        csrf_token = request.cookies.get('csrf_access_token')
        return dict(
            current_condominium=getattr(g, 'condominium', None),
            csrf_token=csrf_token
        )
