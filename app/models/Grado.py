from app.extensions import db

class Grado(db.Model):
    __tablename__ = "grados"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)   # Ej: Blanco, Amarillo
    tipo = db.Column(db.String(10), nullable=False)     # KUP | DAN
    orden = db.Column(db.Integer, nullable=False)       # Para ordenar
    color = db.Column(db.String(20))                    # white, yellow, black
    activo = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<Grado {self.nombre}>"
