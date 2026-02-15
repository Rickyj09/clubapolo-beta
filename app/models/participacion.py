from app.extensions import db

class Participacion(db.Model):
    __tablename__ = "participaciones"

    id = db.Column(db.Integer, primary_key=True)

    alumno_id = db.Column(db.Integer, db.ForeignKey("alumnos.id"), nullable=False)
    torneo_id = db.Column(db.Integer, db.ForeignKey("torneos.id"), nullable=False)
    medalla_id = db.Column(db.Integer, db.ForeignKey("medallas.id"), nullable=True)
    categoria_id = db.Column(db.Integer, db.ForeignKey("categorias_competencia.id"), nullable=False)

    observacion = db.Column(db.String(255))
    modalidad = db.Column(db.String(10), nullable=False)

    tipo_participacion = db.Column(db.String(20), nullable=False, default="INDIVIDUAL")

    valor_evento = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    pagado_evento = db.Column(db.Boolean, default=False)
    fecha_pago_evento = db.Column(db.Date)
    metodo_pago_evento = db.Column(db.String(30))

    puesto = db.Column(db.Integer)
    puntaje = db.Column(db.Numeric(6, 2))

    academia_id = db.Column(db.Integer, nullable=False)

    # =========================
    # RELATIONSHIPS (para Jinja)
    # =========================
    alumno = db.relationship("Alumno", backref=db.backref("participaciones", lazy=True))
    torneo = db.relationship("Torneo", backref=db.backref("participaciones", lazy=True))
    medalla = db.relationship("Medalla", backref=db.backref("participaciones", lazy=True))
    categoria = db.relationship("CategoriaCompetencia", backref=db.backref("participaciones", lazy=True))