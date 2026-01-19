from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required

from app.extensions import db
from app.models.alumno import Alumno
from app.models.torneo import Torneo
from app.models.medalla import Medalla
from app.models.participacion import Participacion
from app.utils.categorias import obtener_categoria_competencia


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
        modalidad = (request.form.get("modalidad") or "").strip().upper()  # POOMSAE / COMBATE / AMBAS
        medalla_id = request.form.get("medalla_id")
        observacion = request.form.get("observacion")
        print("POST/participaciones/nuevo")
        print("FROM:", dict(request.form))
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

        creadas = 0
        for mod in modalidades_a_registrar:
            categoria = obtener_categoria_competencia(alumno=alumno, torneo=torneo, modalidad=mod)
            print("DEBUG CATEGORIA")
            print("Alumno:", alumno.id, alumno.genero, alumno.grado_id, alumno.fecha_nacimiento)
            print("Torneo:", torneo.id, torneo.fecha)
            print("Modalidad:", mod)
            print("Categoria encontrada:", categoria)

            if categoria:
                print("Categoria ID:", categoria.id, categoria.nombre)
            if not categoria:
                flash(f"No se encontró categoría válida para {mod}. Revise datos del alumno (edad/peso/grado/sexo).", "danger")
                return redirect(request.url)

            p = Participacion(
                alumno_id=alumno.id,
                torneo_id=torneo.id,
                modalidad=mod,
                categoria_id=categoria.id,
                medalla_id=medalla_fk,
                observacion=observacion
            )
            db.session.add(p)
            creadas += 1

        db.session.commit()
        flash(f"Participación registrada correctamente ({creadas})", "success")
        return redirect(url_for("alumnos.perfil", id=alumno.id))

    return render_template(
        "participaciones/nuevo.html",
        alumno=alumno,
        torneos=torneos,
        medallas=medallas
        
    )
