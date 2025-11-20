# c:\condomanager-saas\migrations\env.py
from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import os
import sys

# Añadir la raíz del proyecto al path para que pueda encontrar 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db

config = context.config

# La siguiente línea intenta configurar los logs de Python usando alembic.ini.
# Como nuestro alembic.ini es minimalista y no tiene configuración de logs,
# esta línea causa un error. La comentamos para desactivar esta función que no necesitamos.
# fileConfig(config.config_file_name)

target_metadata = db.metadata

def run_migrations_online() -> None:
    """
    Ejecuta las migraciones en modo 'online'.
    Crea un contexto de aplicación para que Alembic pueda encontrar la configuración
    de la base de datos desde la aplicación Flask.
    """
    app = create_app()
    with app.app_context():
        connectable = db.engine
        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )
            with context.begin_transaction():
                context.run_migrations()

# Solo necesitamos el modo online porque Railway siempre tendrá conexión a la DB.
run_migrations_online()