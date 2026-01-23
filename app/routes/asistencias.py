# app/routes/asistencias.py
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from app.extensions import db
from app.models import Alumno, Asistencia

asistencias_bp = Blueprint("asistencias", __name__, url_prefix="/asistencias")

def puede_gestionar_alumno(alumno: Alumno) -> bool:
    if current_user.has_role("ADMIN"):
        return True
    if current_user.has_role("PROFESOR") and alumno.sucursal_id == current_user.sucursal_id:
        return True
    return False

@asistencias_bp.route("/guardar/<int:alumno_id>", methods=["POST"])
@login_required
def guardar(alumno_id):
    alumno = Alumno.query.get_or_404(alumno_id)

    if not puede_gestionar_alumno(alumno):
        abort(403)

    if not alumno.sucursal_id:
        flash("El alumno no tiene sucursal asignada", "danger")
        return redirect(url_for("alumnos.editar", id=alumno.id) + "#asistencia")

    fecha_str = request.form.get("fecha")
    if not fecha_str:
        flash("Debe seleccionar una fecha", "danger")
        return redirect(url_for("alumnos.editar", id=alumno.id) + "#asistencia")

    # 1) Parse seguro (HTML date manda YYYY-MM-DD)
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Formato de fecha inválido", "danger")
        return redirect(url_for("alumnos.editar", id=alumno.id) + "#asistencia")

    # 2) Checkbox: si viene en el form => checked
    is_presente = "presente" in request.form

    # 3) Mapear a estado del modelo
    estado = "P" if is_presente else "A"

    sucursal_id = alumno.sucursal_id

    existente = Asistencia.query.filter_by(
        fecha=fecha,
        sucursal_id=sucursal_id,
        alumno_id=alumno.id
    ).first()

    if existente:
        existente.estado = estado
        existente.registrado_por_id = current_user.id
    else:
        nuevo = Asistencia(
            fecha=fecha,
            sucursal_id=sucursal_id,
            alumno_id=alumno.id,
            registrado_por_id=current_user.id,
            estado=estado
        )
        db.session.add(nuevo)

    db.session.commit()
    flash("Asistencia guardada correctamente", "success")
    return redirect(url_for("alumnos.editar", id=alumno.id) + "#asistencia")