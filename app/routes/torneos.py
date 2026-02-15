from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.extensions import db
from app.models.torneo import Torneo

torneos_bp = Blueprint("torneos", __name__, url_prefix="/torneos")


def _to_decimal(s, default="0.00"):
    try:
        if s is None or str(s).strip() == "":
            return Decimal(default)
        return Decimal(str(s).replace(",", "."))
    except (InvalidOperation, ValueError):
        return Decimal(default)


def _get_academia_id():
    # evita AttributeError si User aún no tiene academia_id
    return getattr(current_user, "academia_id", 1)


# =========================
# LISTADO DE TORNEOS
# =========================
@torneos_bp.route("/", methods=["GET"])
@login_required
def index():
    academia_id = _get_academia_id()
    torneos = Torneo.query.filter_by(academia_id=academia_id).order_by(Torneo.fecha.desc()).all()
    return render_template("torneos/index.html", torneos=torneos)


# =========================
# NUEVO TORNEO
# =========================
@torneos_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    if request.method == "POST":
        # Fecha
        try:
            fecha = datetime.strptime(request.form["fecha"], "%Y-%m-%d").date()
        except ValueError:
            flash("Fecha inválida", "danger")
            return redirect(request.url)

        # Precios
        precio_poomsae = _to_decimal(request.form.get("precio_poomsae"), "0.00")
        precio_combate = _to_decimal(request.form.get("precio_combate"), "0.00")

        # Si precio_ambas viene vacío -> calcular
        precio_ambas_raw = (request.form.get("precio_ambas") or "").strip()
        if precio_ambas_raw == "":
            precio_ambas = precio_poomsae + precio_combate
        else:
            precio_ambas = _to_decimal(precio_ambas_raw, "0.00")

        torneo = Torneo(
            nombre=request.form["nombre"].strip(),
            ciudad=(request.form.get("ciudad") or "").strip() or None,
            fecha=fecha,
            organizador=(request.form.get("organizador") or "").strip() or None,
            activo=True,
            precio_poomsae=precio_poomsae,
            precio_combate=precio_combate,
            precio_ambas=precio_ambas,
            academia_id=_get_academia_id()
        )

        db.session.add(torneo)
        db.session.commit()

        flash("Torneo registrado correctamente", "success")
        return redirect(url_for("torneos.index"))

    return render_template("torneos/nuevo.html")