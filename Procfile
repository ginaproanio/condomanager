release: flask db upgrade && python seed_initial_data.py
web: gunicorn "app:create_app()" --bind 0.0.0.0:$PORT