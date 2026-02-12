from flask import Blueprint, render_template, abort, request
from app.models import Alumno, Sucursal

public_bp = Blueprint("public", __name__)

def _get_academia_id_publica():
    """
    Opciones típicas:
    - Header: X-Academia-Id
    - Querystring: ?academia_id=1
    - Cookie / sesión (si ya lo manejas)
    Por ahora dejo 3 alternativas. Usa la que ya tengas.
    """
    # 1) Por querystring (útil local)
    q = request.args.get("academia_id", type=int)
    if q:
        return q

    # 2) Por header
    h = request.headers.get("X-Academia-Id")
    if h and h.isdigit():
        return int(h)

    # 3) Fallback: si Apolo es 1
    return 1


@public_bp.route("/")
def home():
    academia_id = _get_academia_id_publica()

    sucursales = (
        Sucursal.query
        .filter(Sucursal.activo.is_(True))
        .filter(Sucursal.academia_id == academia_id)
        .order_by(Sucursal.nombre.asc())
        .all()
    )

    total_sucursales = len(sucursales)

    total_alumnos = (
        Alumno.query
        .filter(Alumno.activo.is_(True))
        .filter(Alumno.academia_id == academia_id)
        .count()
    )

    return render_template(
        "public/home.html",
        sucursales=sucursales,
        total_sucursales=total_sucursales,
        total_alumnos=total_alumnos
    )


@public_bp.route("/sucursales")
def sucursales():
    academia_id = _get_academia_id_publica()

    sucursales = (
        Sucursal.query
        .filter(Sucursal.activo.is_(True))
        .filter(Sucursal.academia_id == academia_id)
        .order_by(Sucursal.nombre.asc())
        .all()
    )
    return render_template("public/sucursales.html", sucursales=sucursales)


@public_bp.route("/sucursales/<int:sucursal_id>")
def sucursal_detalle(sucursal_id):
    academia_id = _get_academia_id_publica()

    s = (
        Sucursal.query
        .filter(Sucursal.id == sucursal_id)
        .filter(Sucursal.activo.is_(True))
        .filter(Sucursal.academia_id == academia_id)
        .first_or_404()
    )

    return render_template("public/sucursal_detalle.html", s=s)