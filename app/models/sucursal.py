from app.extensions import db

class Sucursal(db.Model):
    __tablename__ = "sucursales"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)

    academia_id = db.Column(
        db.Integer,
        db.ForeignKey("academias.id"),
        nullable=False
    )

    # 🔹 RELACIÓN INVERSA
    alumnos = db.relationship(
        "Alumno",
        back_populates="sucursal",
        cascade="all, delete-orphan"
    )

    academia = db.relationship(
        "Academia",
        back_populates="sucursales"
    )