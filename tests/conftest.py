import pytest
from app import create_app, db
from app.models import User, Condominium

@pytest.fixture
def app():
    """
    Crea una instancia de la aplicación para pruebas.
    Configura la base de datos en memoria (SQLite) para velocidad y aislamiento.
    """
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:", # Base de datos volátil en RAM
        "WTF_CSRF_ENABLED": False, # Desactivar tokens CSRF para facilitar tests de formularios
        "JWT_COOKIE_CSRF_PROTECT": False # Desactivar CSRF de JWT en tests
    })

    # --- CORRECCIÓN: Registrar el blueprint de autenticación en el entorno de pruebas ---
    from app.auth import auth_bp
    app.register_blueprint(auth_bp)

    # Crear contexto de aplicación y base de datos
    with app.app_context():
        db.create_all()
        yield app # Aquí es donde se ejecutan las pruebas
        db.session.remove()
        db.drop_all() # Limpieza al final

@pytest.fixture
def client(app):
    """
    Un cliente de prueba que simula un navegador web.
    """
    return app.test_client()

@pytest.fixture
def runner(app):
    """
    Un runner para probar comandos de CLI si fuera necesario.
    """
    return app.test_cli_runner()
