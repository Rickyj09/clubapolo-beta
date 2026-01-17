from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from app.extensions import db
from app.models import Alumno, Torneo, Medalla
from app.models.participacion import Participacion

participaciones_bp = Blueprint(
    "participaciones",
    __name__,
    url_prefix="/participaciones"
)


@participaciones_bp.route("/nuevo/<int:alumno_id>", methods=["GET", "POST"])
@login_required
def nuevo(alumno_id):

    alumno = Alumno.query.get_or_404(alumno_id)
    torneos = Torneo.query.order_by(Torneo.fecha.desc()).all()
    medallas = Medalla.query.order_by(Medalla.orden).all()

    if request.method == "POST":
        torneo_id = request.form.get("torneo_id")
        medalla_id = request.form.get("medalla_id")
        observacion = request.form.get("observacion")

        if not torneo_id:
            flash("Debe seleccionar un torneo", "danger")
            return redirect(request.url)

        participacion = Participacion(
            alumno_id=alumno.id,
            torneo_id=torneo_id,
            medalla_id=medalla_id or None,
            observacion=observacion
        )

        db.session.add(participacion)
        db.session.commit()

        flash("Participación registrada correctamente", "success")
        return redirect(url_for("alumnos.editar", id=alumno.id))

    return render_template(
        "participaciones/nuevo.html",
        alumno=alumno,
        torneos=torneos,
        medallas=medallas
    )
