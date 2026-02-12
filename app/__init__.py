import os
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, migrate,csrf



# Blueprints
from app.routes.public import public_bp
from app.routes.alumnos import alumnos_bp
from app.routes.sucursales import sucursales_bp
from app.routes.admin import admin_bp
from app.auth.routes import auth_bp
from app.routes.profile import profile_bp
from app.routes.app_menu import app_menu_bp
from app.models import User
from app.routes.pagos import pagos_bp
from app.routes.participaciones import participaciones_bp
from app.routes.torneos import torneos_bp
from app.routes.ranking import ranking_bp
from app.routes.asistencias import asistencias_bp
from app.routes.kiosk import kiosk_bp
from app.routes.reportes import reportes_bp


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")
     # 📁 CONFIGURACIÓN DE SUBIDA DE FOTOS
    app.config["UPLOAD_FOLDER"] = os.path.join(
        app.root_path,
        "static",
        "uploads",
        "alumnos"
    )

    # (opcional pero recomendado)
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    #app.config.from_object(Config)
    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

     # init extensions...
    
    @app.after_request
    def security_headers(response):
    # No bloquees iframes (Google Maps)
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "form-action 'self'; "

        "script-src 'self' https://cdn.jsdelivr.net; "
        "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
        "font-src 'self' https://cdn.jsdelivr.net data:; "
        "img-src 'self' data: https:; "

        "connect-src 'self' https://cdn.jsdelivr.net; "

        # Google Maps embed
        "frame-src https://www.google.com https://maps.google.com; "
    )
        return response
    # Registrar blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(alumnos_bp)
    app.register_blueprint(sucursales_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(app_menu_bp)
    app.register_blueprint(pagos_bp)
    app.register_blueprint(participaciones_bp)
    app.register_blueprint(torneos_bp)
    app.register_blueprint(ranking_bp)
    app.register_blueprint(asistencias_bp)
    app.register_blueprint(kiosk_bp)
    app.register_blueprint(reportes_bp)
    
      # 🔹 CONTEXTO GLOBAL (AQUÍ)
    @app.context_processor
    def inject_academia():
        return {
            "academia": {
                "nombre": "Academia APOLO",
                "email": "contacto@apolotkd.com",
                "telefono": "+593 99 999 9999",
                "logo": "img/logo_apolo.jpg"
            }
        }

    return app
