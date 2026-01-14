from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_required

from app.extensions import db
from app.models.alumno import Alumno
from app.models.categoria import Categoria
from app.models.sucursal import Sucursal   # 🔹 NUEVO

# Blueprint
alumnos_bp = Blueprint(
    "alumnos",
    __name__,
    url_prefix="/alumnos"
)

# =========================
# LISTADO DE ALUMNOS
# =========================
@alumnos_bp.route("/", methods=["GET"])
@login_required
def index():
    alumnos = Alumno.query.order_by(Alumno.id).all()
    total = len(alumnos)

    return render_template(
        "alumnos/index.html",
        alumnos=alumnos,
        total=total
    )

# =========================
# NUEVO ALUMNO
# =========================
@alumnos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()

    if request.method == "POST":
        categoria_id = request.form.get("categoria_id")
        sucursal_id = request.form.get("sucursal_id")

        if not categoria_id:
            flash("Debe seleccionar una categoría", "danger")
            return render_template(
                "alumnos/nuevo.html",
                categorias=categorias,
                sucursales=sucursales
            )

        if not sucursal_id:
            flash("Debe seleccionar una sucursal", "danger")
            return render_template(
                "alumnos/nuevo.html",
                categorias=categorias,
                sucursales=sucursales
            )

        alumno = Alumno(
            nombres=request.form["nombres"],
            apellidos=request.form["apellidos"],
            fecha_nacimiento=request.form["fecha_nacimiento"],
            genero=request.form["genero"],
            categoria_id=int(categoria_id),
            sucursal_id=int(sucursal_id),   # 🔹 CLAVE
            activo=True
        )

        db.session.add(alumno)
        db.session.commit()

        flash("Alumno creado correctamente", "success")
        return redirect(url_for("alumnos.index"))

    return render_template(
        "alumnos/nuevo.html",
        categorias=categorias,
        sucursales=sucursales
    )

# =========================
# EDITAR ALUMNO
# =========================
@alumnos_bp.route("/<int:id>/editar", methods=["GET", "POST"])
@login_required
def editar(id):
    alumno = Alumno.query.get_or_404(id)
    categorias = Categoria.query.order_by(Categoria.nombre).all()
    sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()

    if request.method == "POST":
        alumno.nombres = request.form["nombres"]
        alumno.apellidos = request.form["apellidos"]
        alumno.fecha_nacimiento = request.form["fecha_nacimiento"]
        alumno.genero = request.form["genero"]
        alumno.categoria_id = int(request.form["categoria_id"])
        alumno.sucursal_id = int(request.form["sucursal_id"])  # 🔹 CLAVE
        alumno.activo = "activo" in request.form

        db.session.commit()

        flash("Alumno actualizado correctamente", "success")
        return redirect(url_for("alumnos.index"))

    return render_template(
        "alumnos/editar.html",
        alumno=alumno,
        categorias=categorias,
        sucursales=sucursales
    )

# =========================
# ELIMINAR ALUMNO
# =========================
@alumnos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):
    alumno = Alumno.query.get_or_404(id)
    db.session.delete(alumno)
    db.session.commit()

    flash("Alumno eliminado correctamente", "success")
    return redirect(url_for("alumnos.index"))
