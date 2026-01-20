from flask import Blueprint, render_template
from flask_login import login_required
from sqlalchemy import func, case

from app.extensions import db
from app.models.alumno import Alumno
from app.models.participacion import Participacion
from app.models.medalla import Medalla

ranking_bp = Blueprint("ranking", __name__, url_prefix="/ranking")


@ranking_bp.route("/")
@login_required
def index():

    ranking = (
        db.session.query(
            Alumno,
            func.sum(case((Medalla.nombre == "Oro", 1), else_=0)).label("oros"),
            func.sum(case((Medalla.nombre == "Plata", 1), else_=0)).label("platas"),
            func.sum(case((Medalla.nombre == "Bronce", 1), else_=0)).label("bronces"),
            func.count(Medalla.id).label("total"),
        )
        .outerjoin(Participacion, Participacion.alumno_id == Alumno.id)
        .outerjoin(Medalla, Medalla.id == Participacion.medalla_id)
        .group_by(Alumno.id)
        .order_by(
            func.sum(case((Medalla.nombre == "Oro", 1), else_=0)).desc(),
            func.sum(case((Medalla.nombre == "Plata", 1), else_=0)).desc(),
            func.sum(case((Medalla.nombre == "Bronce", 1), else_=0)).desc(),
            func.count(Medalla.id).desc(),
        )
        .all()
    )

    return render_template(
        "alumnos/ranking.html",
        ranking=ranking
    )
