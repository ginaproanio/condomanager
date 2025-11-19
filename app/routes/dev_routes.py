from flask import Blueprint, current_app, jsonify
from app.extensions import db
from app import models
import os
import hashlib

# Este blueprint es SOLO para desarrollo y diagnóstico.
# DEBE ser eliminado o deshabilitado en producción.
dev_bp = Blueprint('dev', __name__, url_prefix='/dev')

@dev_bp.route("/force-init-db")
def force_init_db():
    """
    Endpoint temporal para forzar la creación de tablas y la inserción de datos iniciales.
    """
    try:
        with current_app.app_context():
            print("AUDIT: Forzando la creación de tablas desde el endpoint /dev/force-init-db")
            db.create_all()
            print("✅ AUDIT: db.create_all() ejecutado con éxito.")

            # Crear usuario maestro
            master_email = os.environ.get('MASTER_EMAIL', 'maestro@condomanager.com')
            if not models.User.query.filter_by(email=master_email).first():
                print(f"AUDIT: Creando usuario maestro para {master_email}...")
                master_password = os.environ.get('MASTER_PASSWORD', 'Master2025!')
                pwd_hash = hashlib.sha256(master_password.encode()).hexdigest()
                master = models.User(
                    email=master_email, name='Administrador Maestro', password_hash=pwd_hash,
                    tenant=None, role='MASTER', status='active'
                )
                db.session.add(master)
                print("AUDIT: Usuario maestro añadido a la sesión.")

            # Crear configuración de tenant por defecto
            default_tenant = 'puntablanca'
            if not models.CondominiumConfig.query.get(default_tenant):
                print(f"AUDIT: Creando configuración para el tenant por defecto '{default_tenant}'...")
                config = models.CondominiumConfig(tenant=default_tenant, commercial_name='Punta Blanca')
                db.session.add(config)
                print("AUDIT: Configuración de tenant añadida a la sesión.")

            # ¡EL PASO CRUCIAL QUE FALTABA!
            db.session.commit()
            print("✅ AUDIT: db.session.commit() ejecutado. Cambios guardados permanentemente.")

        return jsonify({
            "status": "success", 
            "message": "Proceso de inicialización forzada completado. Las tablas y datos iniciales deberían existir."
        }), 200

    except Exception as e:
        print(f"❌ ERROR al forzar la creación de tablas: {e}")
        db.session.rollback() # Revertir cambios si algo falla
        return jsonify({"status": "error", "message": str(e)}), 500