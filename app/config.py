import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#class Config:
 #   SECRET_KEY = "dojo-secret-key"

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "alumnos")
ACTAS_UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "actas")
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB (opcional)


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://dojo_user:dojo1234@localhost:3306/dojo_manager"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
      # 🔐 Seguridad de sesión
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # TRUE en HTTPS
    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # TRUE en HTTPS
    REMEMBER_COOKIE_DURATION = 86400

    