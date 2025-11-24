def test_home_page(client):
    """
    Prueba Básica 1: Verificar que la página de inicio carga correctamente.
    """
    response = client.get('/')
    assert response.status_code == 200
    # Verificamos que el título o algo del contenido esté presente
    assert b"CondoManager" in response.data

def test_login_page_loads(client):
    """
    Prueba Básica 2: Verificar que la página de login carga.
    """
    response = client.get('/login')
    assert response.status_code == 200
    assert b"Iniciar Sesi" in response.data # Buscamos parte del texto "Iniciar Sesión"

def test_demo_page_loads(client):
    """
    Prueba Básica 3: Verificar que la página de solicitud de demo carga.
    """
    response = client.get('/solicitar-demo')
    assert response.status_code == 200
    assert b"Solicita una Demo" in response.data

