from flask import Blueprint

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return "¡CondoManager FUNCIONANDO!"

@main.route('/health')
def health():
    return "OK", 200

@main.route('/registro')
def registro():
    return "Página de registro - FUNCIONANDO"