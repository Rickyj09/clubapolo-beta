from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
from datetime import datetime

from app.extensions import db
from app.models.torneo import Torneo

torneos_bp = Blueprint(
    "torneos",
    __name__,
    url_prefix="/torneos"
)

# =========================
# LISTADO DE TORNEOS
# =========================
@torneos_bp.route("/")
@login_required
def index():
    torneos = Torneo.query.order_by(Torneo.fecha.desc()).all()
    return render_template("torneos/index.html", torneos=torneos)

# =========================
# NUEVO TORNEO
# =========================
@torneos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():

    if request.method == "POST":
        try:
            fecha = datetime.strptime(
                request.form["fecha"], "%Y-%m-%d"
            ).date()
        except ValueError:
            flash("Fecha inválida", "danger")
            return redirect(request.url)

        torneo = Torneo(
            nombre=request.form["nombre"],
            ciudad=request.form.get("ciudad"),
            fecha=fecha,
            organizador=request.form.get("organizador"),
            activo=True
        )

        db.session.add(torneo)
        db.session.commit()

        flash("Torneo registrado correctamente", "success")
        return redirect(url_for("torneos.index"))

    return render_template("torneos/nuevo.html")
