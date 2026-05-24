from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models.banco_preguntas import BancoPregunta
from app.models.grado import Grado
from app.models.plantillas_examen import PlantillaExamen, PlantillaPregunta


plantillas_examen_bp = Blueprint(
    "plantillas_examen",
    __name__,
    url_prefix="/plantillas-examen",
)


def _academia_id_or_redirect():
    academia_id = getattr(g, "academia_id", None) or getattr(current_user, "academia_id", None)
    if not academia_id:
        flash("No hay academia seleccionada.", "warning")
        return None
    return academia_id


def _can_manage_templates() -> bool:
    if not getattr(current_user, "is_authenticated", False):
        return False
    return current_user.has_role("ADMIN") or current_user.has_role("SUPERADMIN")


def _require_admin():
    if _can_manage_templates():
        return None
    flash("No tienes permisos para gestionar plantillas de examen.", "danger")
    return redirect(url_for("public.home"))


def _load_grados(academia_id: int):
    return (
        Grado.query
        .filter_by(academia_id=academia_id, activo=True)
        .order_by(Grado.orden.asc(), Grado.nombre.asc())
        .all()
    )


def _recount_template_questions(item: PlantillaExamen):
    total = (
        PlantillaPregunta.query
        .filter_by(plantilla_id=item.id, activo=True)
        .count()
    )
    if item.modo_seleccion == "FIJA":
        item.num_preguntas = total
    return total


@plantillas_examen_bp.route("/", methods=["GET"])
@login_required
def index():
    denied = _require_admin()
    if denied:
        return denied

    academia_id = _academia_id_or_redirect()
    if not academia_id:
        return redirect(url_for("public.home"))

    items = (
        PlantillaExamen.query
        .filter_by(academia_id=academia_id)
        .order_by(PlantillaExamen.activo.desc(), PlantillaExamen.nombre.asc())
        .all()
    )
    grados = _load_grados(academia_id)
    grados_map = {grado.id: grado for grado in grados}
    preguntas_counts = {
        item.id: sum(1 for pregunta in item.preguntas if pregunta.activo)
        for item in items
    }

    return render_template(
        "plantillas_examen/index.html",
        items=items,
        grados_map=grados_map,
        preguntas_counts=preguntas_counts,
    )


@plantillas_examen_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    denied = _require_admin()
    if denied:
        return denied

    academia_id = _academia_id_or_redirect()
    if not academia_id:
        return redirect(url_for("public.home"))

    grados = _load_grados(academia_id)

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip() or None
        grado_id = request.form.get("grado_id", type=int)
        disciplina = (request.form.get("disciplina") or "").strip().upper()
        modo_seleccion = (request.form.get("modo_seleccion") or "FIJA").strip().upper()
        num_preguntas = request.form.get("num_preguntas", type=int)
        puntaje_minimo = request.form.get("puntaje_minimo", type=float)
        activo = request.form.get("activo") == "1"

        if not nombre:
            flash("El nombre de la plantilla es obligatorio.", "danger")
            return render_template("plantillas_examen/form.html", item=None, grados=grados)

        if not grado_id:
            flash("Selecciona el grado de la plantilla.", "danger")
            return render_template("plantillas_examen/form.html", item=None, grados=grados)

        if not disciplina:
            flash("La disciplina es obligatoria.", "danger")
            return render_template("plantillas_examen/form.html", item=None, grados=grados)

        if modo_seleccion not in ("FIJA", "ALEATORIA"):
            flash("El modo de selección es inválido.", "danger")
            return render_template("plantillas_examen/form.html", item=None, grados=grados)

        item = PlantillaExamen(
            academia_id=academia_id,
            nombre=nombre,
            descripcion=descripcion,
            grado_id=grado_id,
            disciplina=disciplina,
            modo_seleccion=modo_seleccion,
            num_preguntas=num_preguntas if num_preguntas is not None else 0,
            puntaje_minimo=puntaje_minimo if puntaje_minimo is not None else 70.0,
            activo=activo,
        )
        db.session.add(item)
        db.session.commit()

        flash("Plantilla creada correctamente.", "success")
        return redirect(url_for("plantillas_examen.preguntas", plantilla_id=item.id))

    return render_template("plantillas_examen/form.html", item=None, grados=grados)


@plantillas_examen_bp.route("/<int:plantilla_id>/editar", methods=["GET", "POST"])
@login_required
def editar(plantilla_id: int):
    denied = _require_admin()
    if denied:
        return denied

    academia_id = _academia_id_or_redirect()
    if not academia_id:
        return redirect(url_for("public.home"))

    item = PlantillaExamen.query.filter_by(id=plantilla_id, academia_id=academia_id).first_or_404()
    grados = _load_grados(academia_id)

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        descripcion = (request.form.get("descripcion") or "").strip() or None
        grado_id = request.form.get("grado_id", type=int)
        disciplina = (request.form.get("disciplina") or "").strip().upper()
        modo_seleccion = (request.form.get("modo_seleccion") or "FIJA").strip().upper()
        num_preguntas = request.form.get("num_preguntas", type=int)
        puntaje_minimo = request.form.get("puntaje_minimo", type=float)

        if not nombre:
            flash("El nombre de la plantilla es obligatorio.", "danger")
            return render_template("plantillas_examen/form.html", item=item, grados=grados)

        if not grado_id:
            flash("Selecciona el grado de la plantilla.", "danger")
            return render_template("plantillas_examen/form.html", item=item, grados=grados)

        if not disciplina:
            flash("La disciplina es obligatoria.", "danger")
            return render_template("plantillas_examen/form.html", item=item, grados=grados)

        if modo_seleccion not in ("FIJA", "ALEATORIA"):
            flash("El modo de selección es inválido.", "danger")
            return render_template("plantillas_examen/form.html", item=item, grados=grados)

        item.nombre = nombre
        item.descripcion = descripcion
        item.grado_id = grado_id
        item.disciplina = disciplina
        item.modo_seleccion = modo_seleccion
        item.activo = request.form.get("activo") == "1"
        item.puntaje_minimo = puntaje_minimo if puntaje_minimo is not None else item.puntaje_minimo

        if item.modo_seleccion == "ALEATORIA":
            item.num_preguntas = num_preguntas if num_preguntas is not None else item.num_preguntas
        else:
            _recount_template_questions(item)

        db.session.commit()
        flash("Plantilla actualizada.", "success")
        return redirect(url_for("plantillas_examen.index"))

    return render_template("plantillas_examen/form.html", item=item, grados=grados)


@plantillas_examen_bp.route("/<int:plantilla_id>/preguntas", methods=["GET", "POST"])
@login_required
def preguntas(plantilla_id: int):
    denied = _require_admin()
    if denied:
        return denied

    academia_id = _academia_id_or_redirect()
    if not academia_id:
        return redirect(url_for("public.home"))

    plantilla = PlantillaExamen.query.filter_by(id=plantilla_id, academia_id=academia_id).first_or_404()
    grados = _load_grados(academia_id)

    if request.method == "POST":
        action = (request.form.get("action") or "").strip()
        pregunta_id = request.form.get("pregunta_id", type=int)
        orden = request.form.get("orden", type=int) or 0
        puntaje = request.form.get("puntaje", type=float)
        obligatorio = request.form.get("obligatorio") == "1"

        if action == "add":
            if not pregunta_id:
                flash("Selecciona una pregunta para agregar.", "danger")
                return redirect(url_for("plantillas_examen.preguntas", plantilla_id=plantilla.id))

            pregunta = BancoPregunta.query.filter_by(
                id=pregunta_id,
                academia_id=academia_id,
                activo=True,
            ).first()
            if not pregunta:
                flash("La pregunta seleccionada no existe en esta academia.", "danger")
                return redirect(url_for("plantillas_examen.preguntas", plantilla_id=plantilla.id))

            link = PlantillaPregunta.query.filter_by(
                plantilla_id=plantilla.id,
                pregunta_id=pregunta_id,
            ).first()
            if link:
                link.activo = True
                link.orden = orden
                link.puntaje = puntaje if puntaje is not None else pregunta.puntaje_max
                link.obligatorio = obligatorio
            else:
                link = PlantillaPregunta(
                    plantilla_id=plantilla.id,
                    pregunta_id=pregunta_id,
                    orden=orden,
                    puntaje=puntaje if puntaje is not None else pregunta.puntaje_max,
                    obligatorio=obligatorio,
                    activo=True,
                )
                db.session.add(link)

            _recount_template_questions(plantilla)
            db.session.commit()
            flash("Pregunta asociada a la plantilla.", "success")

        elif action == "update":
            link_id = request.form.get("link_id", type=int)
            link = PlantillaPregunta.query.filter_by(id=link_id, plantilla_id=plantilla.id).first()
            if not link:
                flash("No se encontró la relación de plantilla y pregunta.", "warning")
                return redirect(url_for("plantillas_examen.preguntas", plantilla_id=plantilla.id))

            link.orden = orden
            link.puntaje = puntaje
            link.obligatorio = obligatorio
            link.activo = request.form.get("activo") == "1"
            _recount_template_questions(plantilla)
            db.session.commit()
            flash("Configuración de pregunta actualizada.", "success")

        elif action == "remove":
            link_id = request.form.get("link_id", type=int)
            link = PlantillaPregunta.query.filter_by(id=link_id, plantilla_id=plantilla.id).first()
            if link:
                db.session.delete(link)
                _recount_template_questions(plantilla)
                db.session.commit()
                flash("Pregunta quitada de la plantilla.", "success")
            else:
                flash("La relación ya no existe.", "warning")

        return redirect(url_for("plantillas_examen.preguntas", plantilla_id=plantilla.id))

    disciplina = (request.args.get("disciplina") or plantilla.disciplina or "").strip().upper()
    tipo = (request.args.get("tipo") or "").strip().upper()
    grado_id = request.args.get("grado_id", type=int)
    dificultad = request.args.get("dificultad", type=int)
    texto = (request.args.get("texto") or "").strip()

    asociados = (
        PlantillaPregunta.query
        .filter_by(plantilla_id=plantilla.id)
        .order_by(PlantillaPregunta.activo.desc(), PlantillaPregunta.orden.asc(), PlantillaPregunta.id.asc())
        .all()
    )
    asociados_ids = [link.pregunta_id for link in asociados]
    asociados_map = {link.pregunta_id: link for link in asociados}

    q = BancoPregunta.query.filter_by(academia_id=academia_id, activo=True)
    if disciplina:
        q = q.filter(BancoPregunta.disciplina == disciplina)
    if tipo:
        q = q.filter(BancoPregunta.tipo == tipo)
    if grado_id:
        q = q.filter(BancoPregunta.grado_id == grado_id)
    if dificultad:
        q = q.filter(BancoPregunta.dificultad == dificultad)
    if texto:
        q = q.filter(BancoPregunta.enunciado.ilike(f"%{texto}%"))

    disponibles = q.order_by(BancoPregunta.id.desc()).all()

    return render_template(
        "plantillas_examen/preguntas.html",
        plantilla=plantilla,
        asociados=asociados,
        asociados_map=asociados_map,
        asociados_ids=asociados_ids,
        disponibles=disponibles,
        grados=grados,
        grados_map={grado.id: grado for grado in grados},
        filtros={
            "disciplina": disciplina,
            "tipo": tipo,
            "grado_id": grado_id,
            "dificultad": dificultad,
            "texto": texto,
        },
    )


@plantillas_examen_bp.route("/<int:plantilla_id>/eliminar", methods=["POST"])
@login_required
def eliminar(plantilla_id: int):
    denied = _require_admin()
    if denied:
        return denied

    academia_id = _academia_id_or_redirect()
    if not academia_id:
        return redirect(url_for("public.home"))

    item = PlantillaExamen.query.filter_by(id=plantilla_id, academia_id=academia_id).first_or_404()
    item.activo = False
    db.session.commit()

    flash("Plantilla desactivada correctamente.", "success")
    return redirect(url_for("plantillas_examen.index"))
