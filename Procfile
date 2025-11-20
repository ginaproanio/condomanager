# La fase 'release' ejecuta este comando antes de lanzar la nueva versión.
# 'flask db upgrade' aplica cualquier nueva migración a la base de datos.
release: flask db upgrade
web: gunicorn "app:create_app()" --bind 0.0.0.0:$PORT