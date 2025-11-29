from flask import request, g, abort, current_app
from app.models import Condominium

def init_tenant_middleware(app):
    @app.before_request
    def resolve_tenant():
        # --- ARQUITECTURA PATH-BASED PARA RAILWAY ---
        # Ya no se usa el subdominio, se usa el primer segmento de la ruta.
        # Ej: /algarrobos/admin/panel -> parts[1] es 'algarrobos'
        subdomain = None
        path_parts = request.path.split('/')
        if len(path_parts) > 1 and path_parts[1] not in ['static', 'api', 'master', 'auth', 'google_drive']:
            # Asumimos que el primer segmento es el slug del tenant
            # Se excluyen rutas globales para no confundirlas con un tenant.
            subdomain = path_parts[1]

        # Para desarrollo, mantenemos la capacidad de forzar un tenant con un query param.
        # Esto es útil para probar rutas sin tener que escribir el slug en la URL cada vez.
        tenant_param = request.args.get('tenant')
        if tenant_param and current_app.debug:
            subdomain = tenant_param
        # 2. Cargar Condominio (Tenant)
        g.condominium = None
        g.environment = 'production' # Default seguro

        if subdomain:
            tenant = Condominium.query.filter_by(subdomain=subdomain).first()
            
            if not tenant:
                abort(404, description="Condominio no encontrado con el slug proporcionado en la URL.")
            
            g.condominium = tenant
            g.environment = tenant.environment # 'production', 'demo', 'internal'

        else:
            # Si no se detecta un slug de tenant en la URL, estamos en el dominio raíz (ej. /login, /api/auth/login).
            # Las rutas públicas, de API, master, etc., deben funcionar aquí.
            if request.endpoint and not (
                request.endpoint.startswith('public.') or
                request.endpoint.startswith('auth.') or
                request.endpoint.startswith('api.') or
                request.endpoint.startswith('master.')
            ):
                 pass # Para otras rutas, dejamos que el decorador de la ruta decida si requiere un tenant.
            
            g.condominium = None

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

    @app.context_processor
    def inject_url_helpers():
        """
        Inyecta una función url_for inteligente en las plantillas.
        Añade automáticamente el 'tenant_slug' a las rutas que lo requieran.
        """
        def url_for_tenant(endpoint, **values):
            if g.condominium and 'tenant_slug' not in values:
                if endpoint.split('.')[0] in ['admin', 'petty_cash', 'google_drive']:
                    values['tenant_slug'] = g.condominium.subdomain
            return url_for(endpoint, **values)
        return dict(url_for_tenant=url_for_tenant)

    @app.context_processor
    def inject_url_helpers():
        """
        Inyecta una función url_for inteligente en las plantillas.
        Añade automáticamente el 'tenant_slug' a las rutas que lo requieran.
        """
        def url_for_tenant(endpoint, **values):
            if g.condominium and 'tenant_slug' not in values:
                if endpoint.split('.')[0] in ['admin', 'petty_cash', 'google_drive']:
                    values['tenant_slug'] = g.condominium.subdomain
            return url_for(endpoint, **values)
        return dict(url_for_tenant=url_for_tenant)
