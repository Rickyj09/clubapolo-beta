from app.extensions import db

class Participacion(db.Model):
    __tablename__ = "participaciones"

    id = db.Column(db.Integer, primary_key=True)

    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)
    torneo_id = db.Column(db.Integer, db.ForeignKey("torneos.id"), nullable=False)
    medalla_id = db.Column(db.Integer, db.ForeignKey("medallas.id"), nullable=True)

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias_competencia.id"),
        nullable=False
    )

    modalidad = db.Column(db.String(10), nullable=False)  # POOMSAE / COMBATE
    observacion = db.Column(db.String(255))

    # Relaciones
    alumno = db.relationship("Alumno", backref="participaciones")
    torneo = db.relationship("Torneo")
    medalla = db.relationship("Medalla")
    categoria = db.relationship("CategoriaCompetencia")
