from app.extensions import db

class Academia(db.Model):
    __tablename__ = "academias"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    sucursales = db.relationship(
        "Sucursal",
        back_populates="academia",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Academia {self.nombre}>"
