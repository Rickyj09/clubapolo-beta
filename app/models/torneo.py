from app.extensions import db

class Torneo(db.Model):
    __tablename__ = "torneos"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    ciudad = db.Column(db.String(100))
    fecha = db.Column(db.Date, nullable=False)
    organizador = db.Column(db.String(100))
    activo = db.Column(db.Boolean, default=True)

    precio_poomsae = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")
    precio_combate = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")
    precio_ambas   = db.Column(db.Numeric(10, 2), nullable=False, server_default="0.00")

    academia_id = db.Column(db.Integer, nullable=False)  # ✅ AGREGAR