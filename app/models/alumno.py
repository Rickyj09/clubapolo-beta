from app.extensions import db

class Alumno(db.Model):
    __tablename__ = "alumnos"

    id = db.Column(db.Integer, primary_key=True)
    nombres = db.Column(db.String(100), nullable=False)
    apellidos = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    genero = db.Column(db.String(1), nullable=False)
    activo = db.Column(db.Boolean, default=True)

    categoria_id = db.Column(
        db.Integer,
        db.ForeignKey("categorias.id"),
        nullable=False
    )

    # =========================
    # SUCURSAL
    # =========================
    sucursal_id = db.Column(
        db.Integer,
        db.ForeignKey("sucursales.id"),
        nullable=False
    )

    sucursal = db.relationship(
        "Sucursal",
        back_populates="alumnos"
    )

    # =========================
    # PROFESOR (USER)
    # =========================
    profesor_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=True  # para permitir alumnos sin profesor (si lo deseas)
    )

  