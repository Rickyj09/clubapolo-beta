from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.extensions import db
from app.models.sucursal import Sucursal
from app.models.academia import Academia

sucursales_bp = Blueprint(
    "sucursales",
    __name__,
    url_prefix="/sucursales"
)

# ===============================
# LISTAR SUCURSALES
# ===============================
@sucursales_bp.route("/")
def index():
    sucursales = Sucursal.query.all()
    return render_template(
        "sucursales/index.html",
        sucursales=sucursales
    )

# ===============================
# CREAR SUCURSAL
# ===============================
@sucursales_bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    academias = Academia.query.all()

    if request.method == "POST":
        sucursal = Sucursal(
            nombre=request.form["nombre"],
            direccion=request.form["direccion"],
            academia_id=request.form["academia_id"],
            activo="activo" in request.form
        )
        db.session.add(sucursal)
        db.session.commit()
        flash("Sucursal creada correctamente", "success")
        return redirect(url_for("sucursales.index"))

    return render_template(
        "sucursales/form.html",
        sucursal=None,
        academias=academias
    )

# ===============================
# EDITAR SUCURSAL
# ===============================
@sucursales_bp.route("/<int:id>/editar", methods=["GET", "POST"])
def editar(id):
    sucursal = Sucursal.query.get_or_404(id)
    academias = Academia.query.all()

    if request.method == "POST":
        sucursal.nombre = request.form["nombre"]
        sucursal.direccion = request.form["direccion"]
        sucursal.academia_id = request.form["academia_id"]
        sucursal.activo = "activo" in request.form

        db.session.commit()
        flash("Sucursal actualizada", "success")
        return redirect(url_for("sucursales.index"))

    return render_template(
        "sucursales/form.html",
        sucursal=sucursal,
        academias=academias
    )

# ===============================
# ELIMINAR SUCURSAL
# ===============================
@sucursales_bp.route("/<int:id>/eliminar", methods=["POST"])
def eliminar(id):
    sucursal = Sucursal.query.get_or_404(id)
    db.session.delete(sucursal)
    db.session.commit()
    flash("Sucursal eliminada", "success")
    return redirect(url_for("sucursales.index"))
