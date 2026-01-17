from app.extensions import db

class Participacion(db.Model):
    __tablename__ = "participaciones"

    id = db.Column(db.Integer, primary_key=True)

    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)
    torneo_id = db.Column(db.Integer, db.ForeignKey("torneos.id"), nullable=False)
    medalla_id = db.Column(db.Integer, db.ForeignKey("medallas.id"))

    categoria = db.Column(db.String(50))  # poomsae, combate, exhibición
    observacion = db.Column(db.String(200))

    alumno = db.relationship("Alumno", backref="participaciones")
    torneo = db.relationship("Torneo")
    medalla = db.relationship("Medalla")
