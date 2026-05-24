from flask import Blueprint, render_template, request
from sqlalchemy import case, func

from app.extensions import db
from app.models.alumno import Alumno
from app.models.categoriascompetencia import CategoriaCompetencia
from app.models.grado import Grado
from app.models.medalla import Medalla
from app.models.participacion import Participacion
from app.models.sucursal import Sucursal


public_bp = Blueprint("public", __name__)


def _get_academia_id_publica():
    """
    Opciones típicas:
    - Header: X-Academia-Id
    - Querystring: ?academia_id=1
    - Cookie / sesión (si ya lo manejas)
    Por ahora dejo 3 alternativas. Usa la que ya tengas.
    """
    q = request.args.get("academia_id", type=int)
    if q:
        return q

    h = request.headers.get("X-Academia-Id")
    if h and h.isdigit():
        return int(h)

    return 1


def _query_ranking_publico(academia_id: int):
    oro_expr = func.coalesce(
        func.sum(case((func.upper(Medalla.nombre) == "ORO", 1), else_=0)),
        0,
    )
    plata_expr = func.coalesce(
        func.sum(case((func.upper(Medalla.nombre) == "PLATA", 1), else_=0)),
        0,
    )
    bronce_expr = func.coalesce(
        func.sum(case((func.upper(Medalla.nombre) == "BRONCE", 1), else_=0)),
        0,
    )
    puntos_expr = (oro_expr * 5) + (plata_expr * 3) + bronce_expr

    return (
        db.session.query(
            Alumno.id.label("alumno_id"),
            Alumno.nombres,
            Alumno.apellidos,
            Grado.nombre.label("grado_nombre"),
            Sucursal.nombre.label("sucursal_nombre"),
            func.group_concat(func.distinct(Participacion.modalidad)).label("modalidades"),
            func.group_concat(func.distinct(CategoriaCompetencia.nombre)).label("categorias"),
            oro_expr.label("oros"),
            plata_expr.label("platas"),
            bronce_expr.label("bronces"),
            puntos_expr.label("puntos"),
        )
        .join(Participacion, Participacion.alumno_id == Alumno.id)
        .outerjoin(Medalla, Medalla.id == Participacion.medalla_id)
        .outerjoin(Grado, Grado.id == Alumno.grado_id)
        .outerjoin(Sucursal, Sucursal.id == Alumno.sucursal_id)
        .outerjoin(CategoriaCompetencia, CategoriaCompetencia.id == Participacion.categoria_id)
        .filter(
            Alumno.activo.is_(True),
            Alumno.academia_id == academia_id,
            Participacion.academia_id == academia_id,
        )
        .group_by(
            Alumno.id,
            Alumno.nombres,
            Alumno.apellidos,
            Grado.nombre,
            Sucursal.nombre,
        )
        .order_by(
            puntos_expr.desc(),
            oro_expr.desc(),
            plata_expr.desc(),
            bronce_expr.desc(),
            Alumno.apellidos.asc(),
            Alumno.nombres.asc(),
        )
    )


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
        total_alumnos=total_alumnos,
    )


@public_bp.route("/ranking-publico")
def ranking_publico():
    academia_id = _get_academia_id_publica()
    rows = _query_ranking_publico(academia_id).all()

    ranking = [
        {
            "posicion": index,
            "nombre": f"{row.nombres} {row.apellidos}".strip(),
            "grado": row.grado_nombre,
            "categorias": row.categorias,
            "modalidades": row.modalidades,
            "sucursal": row.sucursal_nombre,
            "oros": int(row.oros or 0),
            "platas": int(row.platas or 0),
            "bronces": int(row.bronces or 0),
            "puntos": int(row.puntos or 0),
        }
        for index, row in enumerate(rows, start=1)
    ]

    return render_template(
        "public/ranking_publico.html",
        ranking=ranking,
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
