from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from decimal import Decimal

from app.extensions import db
from app.models.alumno import Alumno
from app.models.torneo import Torneo
from app.models.medalla import Medalla
from app.models.participacion import Participacion
from app.utils.categorias import obtener_categoria_competencia

participaciones_bp = Blueprint("participaciones", __name__, url_prefix="/participaciones")


@participaciones_bp.route("/nuevo/<int:alumno_id>", methods=["GET", "POST"])
@login_required
def nuevo(alumno_id):

    alumno = Alumno.query.get_or_404(alumno_id)
    torneos = Torneo.query.order_by(Torneo.fecha.desc()).all()
    medallas = Medalla.query.order_by(Medalla.orden).all()

    if request.method == "POST":
        torneo_id = request.form.get("torneo_id")
        modalidad = (request.form.get("modalidad") or "").strip().upper()  # POOMSAE / COMBATE / AMBAS
        medalla_id = request.form.get("medalla_id")
        observacion = request.form.get("observacion")

        if not torneo_id or not modalidad:
            flash("Debe seleccionar torneo y modalidad", "danger")
            return redirect(request.url)

        if modalidad not in ("POOMSAE", "COMBATE", "AMBAS"):
            flash("Modalidad inválida", "danger")
            return redirect(request.url)

        torneo = Torneo.query.get_or_404(int(torneo_id))

        # medalla opcional
        medalla_fk = int(medalla_id) if medalla_id else None

        # si es AMBAS, se crean dos participaciones (una por modalidad)
        modalidades_a_registrar = ["POOMSAE", "COMBATE"] if modalidad == "AMBAS" else [modalidad]

        # ===== Calcular valor_evento =====
        if modalidad == "AMBAS":
            total = Decimal(str(torneo.precio_ambas or 0))
            valor_por_modalidad = (total / Decimal("2")).quantize(Decimal("0.01"))
            valores = {"POOMSAE": valor_por_modalidad, "COMBATE": valor_por_modalidad}
        else:
            if modalidad == "POOMSAE":
                valores = {"POOMSAE": Decimal(str(torneo.precio_poomsae or 0))}
            else:
                valores = {"COMBATE": Decimal(str(torneo.precio_combate or 0))}

        creadas = 0
        actualizadas = 0

        for mod in modalidades_a_registrar:
            categoria = obtener_categoria_competencia(alumno=alumno, torneo=torneo, modalidad=mod)

            if not categoria:
                flash(
                    f"No se encontró categoría válida para {mod}. Revise datos del alumno (edad/peso/grado/sexo).",
                    "danger"
                )
                return redirect(request.url)

            # si ya existe por unique (torneo, alumno, modalidad) -> actualiza
            p = Participacion.query.filter_by(
                alumno_id=alumno.id,
                torneo_id=torneo.id,
                modalidad=mod
            ).first()

            if p:
                p.categoria_id = categoria.id
                p.medalla_id = medalla_fk
                p.observacion = observacion
                p.valor_evento = valores.get(mod, Decimal("0.00"))
                actualizadas += 1
            else:
                p = Participacion(
                    alumno_id=alumno.id,
                    torneo_id=torneo.id,
                    modalidad=mod,
                    categoria_id=categoria.id,
                    medalla_id=medalla_fk,
                    observacion=observacion,
                    valor_evento=valores.get(mod, Decimal("0.00")),
                    pagado_evento=False
                )
                db.session.add(p)
                creadas += 1

        db.session.commit()

        flash(f"Participación guardada. Nuevas: {creadas} | Actualizadas: {actualizadas}", "success")
        return redirect(url_for("alumnos.perfil", id=alumno.id))

    return render_template(
        "participaciones/nuevo.html",
        alumno=alumno,
        torneos=torneos,
        medallas=medallas
    )