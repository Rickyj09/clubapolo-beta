from app.extensions import db

class CategoriaCompetencia(db.Model):
    __tablename__ = "categorias_competencia"

    id = db.Column(db.Integer, primary_key=True)

    modalidad = db.Column(db.String(10), nullable=False)  # POOMSAE / COMBATE
    sexo = db.Column(db.String(1), nullable=False)        # M / F

    edad_min = db.Column(db.Integer, nullable=False)
    edad_max = db.Column(db.Integer, nullable=False)

    peso_min = db.Column(db.Float)   # NULL para POOMSAE
    peso_max = db.Column(db.Float)   # NULL para POOMSAE

    # puede ser NULL si quieres "aplica a todos los grados"
    grado_id = db.Column(db.Integer, nullable=True)

    nombre = db.Column(db.String(100), nullable=False)
    activo = db.Column(db.Boolean, default=True)