from flask import request

def get_tenant():
    host = request.host.lower()
    if 'puntablancaecuador.com' in host:
        return 'puntablanca'
    if 'lascolinas.com' in host:
        return 'lascolinas'
    return 'puntablanca'