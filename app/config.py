import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

#class Config:
 #   SECRET_KEY = "dojo-secret-key"

UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads", "alumnos")

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-cambiar-en-produccion")
    WTF_CSRF_ENABLED = True

    SQLALCHEMY_DATABASE_URI =  ('mysql+pymysql://root:1234@127.0.0.1:3306/dojo_manager?charset=utf8mb4')
    

    SQLALCHEMY_TRACK_MODIFICATIONS = False
      # 🔐 Seguridad de sesión
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # TRUE en HTTPS
    SESSION_COOKIE_SAMESITE = "Lax"

    REMEMBER_COOKIE_HTTPONLY = True
    REMEMBER_COOKIE_SECURE = False  # TRUE en HTTPS
    REMEMBER_COOKIE_DURATION = 86400

    