from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.alumno import Alumno
from app.models.torneo import Torneo
from app.models.medalla import Medalla
from app.models.participacion import Participacion
from app.utils.categorias import obtener_categoria_competencia

participaciones_bp = Blueprint("participaciones", __name__, url_prefix="/participaciones")

def _to_decimal(s, default="0.00"):
    try:
        if s is None or str(s).strip() == "":
            return Decimal(default)
        return Decimal(str(s).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal(default)

def _get_academia_id():
    # ✅ evita el AttributeError si User aún no tiene academia_id
    return getattr(current_user, "academia_id", 1)

@participaciones_bp.route("/nuevo/<int:alumno_id>", methods=["GET", "POST"])
@login_required
def nuevo(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)
    torneos = Torneo.query.order_by(Torneo.fecha.desc()).all()
    medallas = Medalla.query.order_by(Medalla.orden).all()

    if request.method == "POST":
        torneo_id = request.form.get("torneo_id")
        modalidad = (request.form.get("modalidad") or "").strip().upper()
        medalla_id = request.form.get("medalla_id")
        observacion = (request.form.get("observacion") or "").strip()

        tipo_participacion = (request.form.get("tipo_participacion") or "INDIVIDUAL").strip().upper()
        valor_evento = _to_decimal(request.form.get("valor_evento"), "0.00")

        if not torneo_id or not modalidad:
            flash("Debe seleccionar torneo y modalidad", "danger")
            return redirect(request.url)

        if modalidad not in ("POOMSAE", "COMBATE", "AMBAS"):
            flash("Modalidad inválida", "danger")
            return redirect(request.url)

        if tipo_participacion not in ("INDIVIDUAL", "EQUIPO", "PAREJAS"):
            flash("Tipo de participación inválido", "danger")
            return redirect(request.url)

        torneo = Torneo.query.get_or_404(int(torneo_id))
        medalla_fk = int(medalla_id) if medalla_id else None

        modalidades_a_registrar = ["POOMSAE", "COMBATE"] if modalidad == "AMBAS" else [modalidad]

        academia_id = _get_academia_id()

        creadas = 0
        for mod in modalidades_a_registrar:
            categoria = obtener_categoria_competencia(alumno=alumno, torneo=torneo, modalidad=mod)
            if not categoria:
                flash(f"No se encontró categoría válida para {mod}. Revise datos del alumno (edad/peso/grado/sexo).", "danger")
                return redirect(request.url)

            p = Participacion(
                alumno_id=alumno.id,
                torneo_id=torneo.id,
                modalidad=mod,
                tipo_participacion=tipo_participacion,
                categoria_id=categoria.id,
                medalla_id=medalla_fk,
                observacion=observacion,
                valor_evento=valor_evento,
                academia_id=academia_id
            )
            db.session.add(p)
            creadas += 1

        db.session.commit()
        flash(f"Participación registrada correctamente ({creadas})", "success")
        return redirect(url_for("alumnos.perfil", id=alumno.id))

    return render_template("participaciones/nuevo.html", alumno=alumno, torneos=torneos, medallas=medallas)