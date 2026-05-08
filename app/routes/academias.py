# app/routes/academias.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from sqlalchemy import func

from app.extensions import db
from app.models.academia import Academia

academias_bp = Blueprint("academias", __name__, url_prefix="/academias")


@academias_bp.route("/", methods=["GET"])
@login_required
def index():
    academias = Academia.query.order_by(Academia.nombre.asc()).all()
    return render_template("academias/index.html", academias=academias)


@academias_bp.route("/nueva", methods=["GET", "POST"])
@login_required
def nueva():
    """
    Crea academia (incluye externas) sin JavaScript.
    - Evita duplicados por nombre (case-insensitive)
    """
    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()

        if not nombre:
            flash("Nombre requerido.", "danger")
            return redirect(request.url)

        existente = Academia.query.filter(func.lower(Academia.nombre) == nombre.lower()).first()
        if existente:
            flash("La academia ya existe.", "info")
            return redirect(url_for("academias.index"))

        a = Academia(nombre=nombre, activo=True)
        db.session.add(a)
        db.session.commit()

        flash("Academia creada correctamente.", "success")
        return redirect(url_for("academias.index"))

    return render_template("academias/nueva.html")


@academias_bp.route("/<int:academia_id>/editar", methods=["GET", "POST"])
@login_required
def editar(academia_id):
    a = Academia.query.get_or_404(academia_id)

    if request.method == "POST":
        nombre = (request.form.get("nombre") or "").strip()
        activo = request.form.get("activo") == "1"

        if not nombre:
            flash("Nombre requerido.", "danger")
            return redirect(request.url)

        # evitar duplicado con otra academia
        existe_otro = (
            Academia.query
            .filter(func.lower(Academia.nombre) == nombre.lower(), Academia.id != a.id)
            .first()
        )
        if existe_otro:
            flash("Ya existe otra academia con ese nombre.", "danger")
            return redirect(request.url)

        a.nombre = nombre
        a.activo = activo
        db.session.commit()

        flash("Academia actualizada.", "success")
        return redirect(url_for("academias.index"))

    return render_template("academias/editar.html", academia=a)


@academias_bp.route("/<int:academia_id>/toggle", methods=["POST"])
@login_required
def toggle(academia_id):
    """
    Activar/Desactivar rápido.
    """
    a = Academia.query.get_or_404(academia_id)
    a.activo = not bool(a.activo)
    db.session.commit()
    flash("Estado actualizado.", "success")
    return redirect(url_for("academias.index"))


@academias_bp.route("/<int:academia_id>/eliminar", methods=["POST"])
@login_required
def eliminar(academia_id):
    """
    Eliminación física (úsala solo si estás seguro).
    Si hay FK en resultados/usuarios/etc. fallará por integridad.
    """
    a = Academia.query.get_or_404(academia_id)
    try:
        db.session.delete(a)
        db.session.commit()
        flash("Academia eliminada.", "success")
    except Exception:
        db.session.rollback()
        flash("No se pudo eliminar: está siendo usada por otros registros. Desactívala mejor.", "danger")

    return redirect(url_for("academias.index"))