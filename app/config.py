import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#class Config:
 #   SECRET_KEY = "dojo-secret-key"

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "alumnos")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SQLALCHEMY_TRACK_MODIFICATIONS = False
      # 🔐 Seguridad de sesión
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # TRUE en HTTPS
    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # TRUE en HTTPS
    REMEMBER_COOKIE_DURATION = 86400

