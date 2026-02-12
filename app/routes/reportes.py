from flask import Blueprint, render_template, request, send_file, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import Alumno, Sucursal
import io
import pandas as pd

reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")

@reportes_bp.route("/lista-competencia", methods=["GET"])
@login_required
def lista_competencia():
    # Si tienes multi-tenant:
    # sucursales = Sucursal.query.filter_by(academia_id=current_user.academia_id).order_by(Sucursal.nombre.asc()).all()
    sucursales = Sucursal.query.order_by(Sucursal.nombre.asc()).all()

    sucursal_id = request.args.get("sucursal_id", type=int)
    alumnos = []
    sucursal = None

    if sucursal_id:
        # Si tienes multi-tenant, aquí también valida que la sucursal pertenezca a la academia
        sucursal = Sucursal.query.get_or_404(sucursal_id)

        alumnos = (
            Alumno.query
            .filter_by(activo=True, sucursal_id=sucursal_id)
            .order_by(Alumno.apellidos.asc(), Alumno.nombres.asc())
            .all()
        )

    return render_template(
        "reportes/lista_competencia.html",
        sucursales=sucursales,
        sucursal_id=sucursal_id,
        sucursal=sucursal,
        alumnos=alumnos
    )


@reportes_bp.route("/lista-competencia/export", methods=["POST"])
@login_required
def export_lista_competencia():
    sucursal_id = request.form.get("sucursal_id", type=int)
    if not sucursal_id:
        flash("Falta seleccionar la sucursal.", "warning")
        return redirect(url_for("reportes.lista_competencia"))

    sucursal = Sucursal.query.get_or_404(sucursal_id)

    ids = request.form.getlist("alumno_ids")
    ids = [int(x) for x in ids if str(x).isdigit()]

    if not ids:
        flash("No seleccionaste alumnos para exportar.", "warning")
        return redirect(url_for("reportes.lista_competencia", sucursal_id=sucursal_id))

    alumnos = (
        Alumno.query
        .filter(Alumno.id.in_(ids))
        .order_by(Alumno.apellidos.asc(), Alumno.nombres.asc())
        .all()
    )

    rows = []
    for a in alumnos:
        rows.append({
            "Sucursal": sucursal.nombre,
            "AlumnoID": a.id,
            "Nombres": getattr(a, "nombres", "") or "",
            "Apellidos": getattr(a, "apellidos", "") or "",
            "Identificación": getattr(a, "numero_identidad", "") or "",
            "Teléfono": getattr(a, "telefono", "") or "",
            "Categoría": "",
            "Modalidad": "",
            "Peso": "",
            "Observación": ""
        })

    df = pd.DataFrame(rows)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Lista_Competencia")

        ws = writer.sheets["Lista_Competencia"]
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

        for col in ws.columns:
            max_len = 10
            col_letter = col[0].column_letter
            for cell in col:
                if cell.value is not None:
                    max_len = max(max_len, len(str(cell.value)))
            ws.column_dimensions[col_letter].width = min(max_len + 2, 40)

    output.seek(0)

    filename = f"lista_competencia_{sucursal.nombre.replace(' ', '_')}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )