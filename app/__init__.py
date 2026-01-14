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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def create_app():
    app = Flask(__name__)
    app.config.from_object("app.config.Config")

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

     # init extensions...
    
    @app.after_request
    def security_headers(response):
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' https://cdn.jsdelivr.net; "
            "img-src 'self' data:;"
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
