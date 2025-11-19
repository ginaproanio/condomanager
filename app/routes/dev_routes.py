from flask import Blueprint, current_app, jsonify
from app.extensions import db

# Este blueprint es SOLO para desarrollo y diagnóstico.
# DEBE ser eliminado o deshabilitado en producción.
dev_bp = Blueprint('dev', __name__, url_prefix='/dev')

@dev_bp.route("/force-init-db")
def force_init_db():
    """
    Endpoint temporal para forzar la creación de todas las tablas de la base de datos.
    """
    try:
        with current_app.app_context():
            print("AUDIT: Forzando la creación de tablas desde el endpoint /dev/force-init-db")
            db.create_all()
            print("✅ AUDIT: db.create_all() ejecutado con éxito.")
        return jsonify({"status": "success", "message": "Tablas creadas exitosamente."}), 200
    except Exception as e:
        print(f"❌ ERROR al forzar la creación de tablas: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500