from flask import Blueprint, render_template
from app.models import Alumno, Sucursal

public_bp = Blueprint("public", __name__)

@public_bp.route("/")
def home():
    sucursales = Sucursal.query.filter_by(activo=True).all()
    total_sucursales = len(sucursales)
    total_alumnos = Alumno.query.filter_by(activo=True).count()

    return render_template(
        "public/home.html",
        sucursales=sucursales,
        total_sucursales=total_sucursales,
        total_alumnos=total_alumnos
    )
