import structlog
import logging
import sys

def setup_logging(app):
    """
    Configura structured logging para la aplicación.
    """
    # Configurar logging estándar de Python para redirigir a structlog
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=logging.INFO
    )

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        cache_logger_on_first_use=True,
    )
    
    # Reemplazar el logger de Flask con structlog (opcional o complementario)
    # app.logger = structlog.get_logger()

