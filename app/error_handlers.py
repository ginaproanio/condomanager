from flask import jsonify, render_template, request, current_app
from app.exceptions import BusinessError
import structlog

logger = structlog.get_logger()

def register_error_handlers(app):
    
    @app.errorhandler(BusinessError)
    def handle_business_error(error):
        """Maneja errores de negocio conocidos."""
        if request.is_json:
            return jsonify({
                'error': error.message,
                'status': 'error',
                'type': error.__class__.__name__
            }), error.status_code
        
        # Para vistas HTML, renderizar plantilla o usar flash si fuera posible
        # Aquí optamos por una plantilla genérica de error o específica según el código
        if error.status_code == 403:
            return render_template('errors/403.html', error=error.message), 403
        elif error.status_code == 404:
            return render_template('errors/404.html', error=error.message), 404
            
        return render_template('errors/400.html', error=error.message), error.status_code

    @app.errorhandler(400)
    def bad_request_error(error):
        if request.is_json:
            return jsonify({'error': 'Solicitud incorrecta', 'status': 'error'}), 400
        return render_template('errors/400.html', error="Solicitud incorrecta"), 400

    @app.errorhandler(403)
    def forbidden_error(error):
        if request.is_json:
            return jsonify({'error': 'Acceso denegado', 'status': 'error'}), 403
        return render_template('errors/403.html', error="No tienes permisos para realizar esta acción."), 403

    @app.errorhandler(404)
    def not_found_error(error):
        if request.is_json:
            return jsonify({'error': 'Recurso no encontrado', 'status': 'error'}), 404
        return render_template('errors/404.html', error="La página o recurso que buscas no existe."), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Internal Server Error", exc_info=error, path=request.path)
        if request.is_json:
            return jsonify({'error': 'Error interno del servidor', 'status': 'error'}), 500
        return render_template('errors/500.html', error="Ha ocurrido un error inesperado en el servidor."), 500

