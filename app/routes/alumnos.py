from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash
)
from flask_login import login_required, current_user

from app.extensions import db
from app.models.alumno import Alumno
from app.models.categoria import Categoria
from app.models.sucursal import Sucursal

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

    # ADMIN: ve todos
    if current_user.has_role("ADMIN"):
        alumnos = Alumno.query.order_by(Alumno.id).all()

    # PROFESOR: solo su sucursal
    elif current_user.has_role("PROFESOR"):
        alumnos = Alumno.query.filter_by(
            sucursal_id=current_user.sucursal_id
        ).order_by(Alumno.id).all()

    else:
        alumnos = []

    total = len(alumnos)

    return render_template(
        "alumnos/index.html",
        alumnos=alumnos,
        total=len(alumnos)
    )

# =========================
# NUEVO ALUMNO
# =========================
@alumnos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    categorias = Categoria.query.order_by(Categoria.nombre).all()

    # ADMIN puede elegir sucursal
    if current_user.has_role("ADMIN"):
        sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()

    # PROFESOR solo su sucursal
    elif current_user.has_role("PROFESOR"):
        sucursales = Sucursal.query.filter_by(
            id=current_user.sucursal_id,
            activo=True
        ).all()

    else:
        flash("No tiene permisos para crear alumnos", "danger")
        return redirect(url_for("alumnos.index"))

    if request.method == "POST":
        categoria_id = request.form.get("categoria_id")

        # ADMIN envía sucursal desde el formulario
        if current_user.has_role("ADMIN"):
            sucursal_id = request.form.get("sucursal_id")
        else:
            # PROFESOR → sucursal fija
            sucursal_id = current_user.sucursal_id

        if not categoria_id:
            flash("Debe seleccionar una categoría", "danger")
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
            sucursal_id=int(sucursal_id),
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

    # PROFESOR no puede editar alumnos de otra sucursal
    if current_user.has_role("PROFESOR") and alumno.sucursal_id != current_user.sucursal_id:
        flash("No tiene permisos para editar este alumno", "danger")
        return redirect(url_for("alumnos.index"))

    categorias = Categoria.query.order_by(Categoria.nombre).all()

    # ADMIN puede cambiar sucursal
    if current_user.has_role("ADMIN"):
        sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()
    else:
        sucursales = None  # PROFESOR no ve selector

    if request.method == "POST":
        alumno.nombres = request.form["nombres"]
        alumno.apellidos = request.form["apellidos"]
        alumno.fecha_nacimiento = request.form["fecha_nacimiento"]
        alumno.genero = request.form["genero"]
        alumno.categoria_id = int(request.form["categoria_id"])

        if current_user.has_role("ADMIN"):
            alumno.sucursal_id = int(request.form["sucursal_id"])

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

    # PROFESOR no puede eliminar alumnos de otra sucursal
    if current_user.has_role("PROFESOR") and alumno.sucursal_id != current_user.sucursal_id:
        flash("No tiene permisos para eliminar este alumno", "danger")
        return redirect(url_for("alumnos.index"))

    db.session.delete(alumno)
    db.session.commit()

    flash("Alumno eliminado correctamente", "success")
    return redirect(url_for("alumnos.index"))
