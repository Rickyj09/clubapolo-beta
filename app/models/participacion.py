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
    # NUEVO: pago por evento (NO pensión)
    valor_evento = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    pagado_evento = db.Column(db.Boolean, nullable=False, default=False)
    fecha_pago_evento = db.Column(db.Date, nullable=True)
    metodo_pago_evento = db.Column(db.String(30), nullable=True)

    alumno = db.relationship("Alumno", backref="participaciones")
    torneo = db.relationship("Torneo")
    medalla = db.relationship("Medalla")
    categoria = db.relationship("CategoriaCompetencia")

__table_args__ = (
    db.UniqueConstraint("torneo_id", "alumno_id", "modalidad",
                        name="uq_participaciones_torneo_alumno_modalidad"),
)
