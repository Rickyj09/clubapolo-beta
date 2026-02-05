from flask import Blueprint, render_template, request, send_file
from flask_login import login_required, current_user
from app.extensions import db
from app.models.alumno import Alumno
from app.models.sucursal import Sucursal
from app.models.Grado import Grado
from datetime import datetime
import io
import pandas as pd
from datetime import date, timedelta


def _get_fecha_base() -> date:
    """
    Devuelve la fecha base para calcular edad:
    - Si viene ?fecha_base=YYYY-MM-DD en querystring, la usa.
    - Si no viene, usa hoy.
    """
    fecha_base_str = request.args.get("fecha_base")
    if fecha_base_str:
        try:
            return datetime.strptime(fecha_base_str, "%Y-%m-%d").date()
        except ValueError:
            # Si viene mal, caemos a hoy (y opcionalmente podrías hacer flash)
            return date.today()
    return date.today()

def _rango_fechas_por_edad(edad_min, edad_max, fecha_base: date):
    """
    Filtra por edad al día 'fecha_base' transformando edad -> rango de fecha_nacimiento.
    Devuelve (fnac_desde, fnac_hasta) para:
      Alumno.fecha_nacimiento BETWEEN fnac_desde AND fnac_hasta
    """
    if not fecha_base:
        fecha_base = date.today()

    fnac_hasta = None  # más viejo (edad_min)
    fnac_desde = None  # más joven (edad_max)

    # Para tener al menos edad_min: nacido <= fecha_base - edad_min años
    if edad_min is not None:
        fnac_hasta = date(fecha_base.year - edad_min, fecha_base.month, fecha_base.day)

    # Para tener como máximo edad_max: nacido >= fecha_base - edad_max años
    if edad_max is not None:
        fnac_desde = date(fecha_base.year - edad_max, fecha_base.month, fecha_base.day)

    return fnac_desde, fnac_hasta


reportes_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


def _aplicar_seguridad_por_rol(query):
    """PROFESOR ve solo su sucursal; ADMIN ve todo."""
    if current_user.has_role("PROFESOR"):
        query = query.filter(Alumno.sucursal_id == current_user.sucursal_id)
    return query


@reportes_bp.route("/", methods=["GET"])
@login_required
def index():
    # filtros
    sucursal_id = request.args.get("sucursal_id", type=int)
    genero = request.args.get("genero")  # 'M'/'F' o como manejes
    grado_id = request.args.get("grado_id", type=int)
    peso_min = request.args.get("peso_min", type=float)
    peso_max = request.args.get("peso_max", type=float)

    q = (
        db.session.query(Alumno, Sucursal, Grado)
        .join(Sucursal, Sucursal.id == Alumno.sucursal_id)
        .outerjoin(Grado, Grado.id == Alumno.grado_id)
    )
    q = _aplicar_seguridad_por_rol(q)

    if sucursal_id:
        q = q.filter(Alumno.sucursal_id == sucursal_id)
    if genero:
        q = q.filter(Alumno.genero == genero)
    if grado_id:
        q = q.filter(Alumno.grado_id == grado_id)
    if peso_min is not None:
        q = q.filter(Alumno.peso >= peso_min)
    if peso_max is not None:
        q = q.filter(Alumno.peso <= peso_max)

    q = q.order_by(Sucursal.nombre.asc(), Alumno.apellidos.asc(), Alumno.nombres.asc())

    # IMPORTANTE: usamos .all() para que en Jinja sea fácil (no Row suelto)
    filas = q.all()

    # combos
    if current_user.has_role("PROFESOR"):
        sucursales = Sucursal.query.filter_by(id=current_user.sucursal_id).all()
    else:
        sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()

    grados = Grado.query.filter_by(activo=True).order_by(Grado.orden).all()

    # Para pintar la tabla: convertimos a dicts
    resultados = []
    for alumno, sucursal, grado in filas:
        resultados.append({
            "id": alumno.numero_identidad,
            "nombres": alumno.nombres,
            "apellidos": alumno.apellidos,
            "genero": alumno.genero,
            "peso": alumno.peso,
            "sucursal": sucursal.nombre if sucursal else "",
            "grado": grado.nombre if grado else "",
        })

    return render_template(
        "reportes/index.html",
        resultados=resultados,
        total=len(resultados),
        sucursales=sucursales,
        grados=grados,
        filtros={
            "sucursal_id": sucursal_id,
            "genero": genero,
            "grado_id": grado_id,
            "peso_min": peso_min,
            "peso_max": peso_max,
        },
    )


@reportes_bp.route("/export/excel", methods=["GET"])
@login_required
def export_excel():
    # reutilizamos EXACTAMENTE los mismos filtros del preview
    sucursal_id = request.args.get("sucursal_id", type=int)
    genero = request.args.get("genero")
    grado_id = request.args.get("grado_id", type=int)
    peso_min = request.args.get("peso_min", type=float)
    peso_max = request.args.get("peso_max", type=float)

    q = (
        db.session.query(Alumno, Sucursal, Grado)
        .join(Sucursal, Sucursal.id == Alumno.sucursal_id)
        .outerjoin(Grado, Grado.id == Alumno.grado_id)
    )
    q = _aplicar_seguridad_por_rol(q)

    if sucursal_id:
        q = q.filter(Alumno.sucursal_id == sucursal_id)
    if genero:
        q = q.filter(Alumno.genero == genero)
    if grado_id:
        q = q.filter(Alumno.grado_id == grado_id)
    if peso_min is not None:
        q = q.filter(Alumno.peso >= peso_min)
    if peso_max is not None:
        q = q.filter(Alumno.peso <= peso_max)

    q = q.order_by(Sucursal.nombre.asc(), Alumno.apellidos.asc(), Alumno.nombres.asc())

    filas = q.all()

    data = []
    for alumno, sucursal, grado in filas:
        data.append({
            "ID": alumno.id,
            "Apellidos": alumno.apellidos,
            "Nombres": alumno.nombres,
            "Género": alumno.genero,
            "Peso": alumno.peso,
            "Sucursal": sucursal.nombre if sucursal else "",
            "Grado": grado.nombre if grado else "",
        })

    df = pd.DataFrame(data)

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Alumnos")
    output.seek(0)

    nombre = f"reporte_alumnos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(
        output,
        as_attachment=True,
        download_name=nombre,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


@reportes_bp.route("/combate", methods=["GET"])
@login_required
def combate():
    sucursal_id = request.args.get("sucursal_id", type=int)
    genero = request.args.get("genero")
    edad_min = request.args.get("edad_min", type=int)
    edad_max = request.args.get("edad_max", type=int)
    peso_min = request.args.get("peso_min", type=float)
    peso_max = request.args.get("peso_max", type=float)

    # 1) definir fecha_base ANTES de usarla
    fecha_base = _get_fecha_base()

    q = (
        db.session.query(Alumno, Sucursal, Grado)
        .join(Sucursal, Sucursal.id == Alumno.sucursal_id)
        .outerjoin(Grado, Grado.id == Alumno.grado_id)
    )
    q = _aplicar_seguridad_por_rol(q)

    if sucursal_id:
        q = q.filter(Alumno.sucursal_id == sucursal_id)
    if genero:
        q = q.filter(Alumno.genero == genero)
    if peso_min is not None:
        q = q.filter(Alumno.peso >= peso_min)
    if peso_max is not None:
        q = q.filter(Alumno.peso <= peso_max)

    # 2) edad (fecha_nacimiento) usando fecha_base ya definida
    fnac_desde, fnac_hasta = _rango_fechas_por_edad(edad_min, edad_max, fecha_base)
    if fnac_desde and fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento.between(fnac_desde, fnac_hasta))
    elif fnac_desde:
        q = q.filter(Alumno.fecha_nacimiento >= fnac_desde)
    elif fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento <= fnac_hasta)

    q = q.order_by(Sucursal.nombre.asc(), Alumno.apellidos.asc(), Alumno.nombres.asc())
    filas = q.all()

    if current_user.has_role("PROFESOR"):
        sucursales = Sucursal.query.filter_by(id=current_user.sucursal_id).all()
    else:
        sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()

    resultados = []
    for alumno, sucursal, grado in filas:
        resultados.append({
            "id": alumno.numero_identidad,
            "apellidos": alumno.apellidos,
            "nombres": alumno.nombres,
            "genero": alumno.genero,
            "fecha_nacimiento": alumno.fecha_nacimiento,
            "peso": alumno.peso,
            "sucursal": sucursal.nombre if sucursal else "",
            "grado": grado.nombre if grado else "",
        })

    return render_template(
        "reportes/combate.html",
        resultados=resultados,
        total=len(resultados),
        sucursales=sucursales,
        filtros={
            "fecha_base": fecha_base.isoformat(),
            "sucursal_id": sucursal_id,
            "genero": genero,
            "edad_min": edad_min,
            "edad_max": edad_max,
            "peso_min": peso_min,
            "peso_max": peso_max,
        },
    )

@reportes_bp.route("/poomsae", methods=["GET"])
@login_required
def poomsae():
    sucursal_id = request.args.get("sucursal_id", type=int)
    genero = request.args.get("genero")
    edad_min = request.args.get("edad_min", type=int)
    edad_max = request.args.get("edad_max", type=int)
    grado_id = request.args.get("grado_id", type=int)
    tipo_grado = request.args.get("tipo_grado")  # 'KUP' o 'DAN'

    fecha_base = _get_fecha_base()

    q = (
        db.session.query(Alumno, Sucursal, Grado)
        .join(Sucursal, Sucursal.id == Alumno.sucursal_id)
        .outerjoin(Grado, Grado.id == Alumno.grado_id)
    )
    q = _aplicar_seguridad_por_rol(q)

    if sucursal_id:
        q = q.filter(Alumno.sucursal_id == sucursal_id)
    if genero:
        q = q.filter(Alumno.genero == genero)
    if grado_id:
        q = q.filter(Alumno.grado_id == grado_id)
    if tipo_grado:
        q = q.filter(Grado.tipo == tipo_grado)

    fnac_desde, fnac_hasta = _rango_fechas_por_edad(edad_min, edad_max, fecha_base)
    if fnac_desde and fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento.between(fnac_desde, fnac_hasta))
    elif fnac_desde:
        q = q.filter(Alumno.fecha_nacimiento >= fnac_desde)
    elif fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento <= fnac_hasta)

    q = q.order_by(Sucursal.nombre.asc(), Alumno.apellidos.asc(), Alumno.nombres.asc())
    filas = q.all()

    if current_user.has_role("PROFESOR"):
        sucursales = Sucursal.query.filter_by(id=current_user.sucursal_id).all()
    else:
        sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()

    grados = Grado.query.filter_by(activo=True).order_by(Grado.orden).all()

    resultados = []
    for alumno, sucursal, grado in filas:
        resultados.append({
            "id": alumno.numero_identidad,
            "apellidos": alumno.apellidos,
            "nombres": alumno.nombres,
            "genero": alumno.genero,
            "fecha_nacimiento": alumno.fecha_nacimiento,
            "sucursal": sucursal.nombre if sucursal else "",
            "grado": grado.nombre if grado else "",
            "grado_tipo": grado.tipo if grado else "",
        })

    return render_template(
        "reportes/poomsae.html",
        resultados=resultados,
        total=len(resultados),
        sucursales=sucursales,
        grados=grados,
        filtros={
            "fecha_base": fecha_base.isoformat(),
            "sucursal_id": sucursal_id,
            "genero": genero,
            "edad_min": edad_min,
            "edad_max": edad_max,
            "grado_id": grado_id,
            "tipo_grado": tipo_grado,
        },
    )


@reportes_bp.route("/combate/export/excel", methods=["GET"])
@login_required
def combate_export_excel():
    # mismos args que combate()
    sucursal_id = request.args.get("sucursal_id", type=int)
    genero = request.args.get("genero")
    edad_min = request.args.get("edad_min", type=int)
    edad_max = request.args.get("edad_max", type=int)
    peso_min = request.args.get("peso_min", type=float)
    peso_max = request.args.get("peso_max", type=float)

    q = (
        db.session.query(Alumno, Sucursal, Grado)
        .join(Sucursal, Sucursal.id == Alumno.sucursal_id)
        .outerjoin(Grado, Grado.id == Alumno.grado_id)
    )
    q = _aplicar_seguridad_por_rol(q)

    if sucursal_id:
        q = q.filter(Alumno.sucursal_id == sucursal_id)
    if genero:
        q = q.filter(Alumno.genero == genero)
    if peso_min is not None:
        q = q.filter(Alumno.peso >= peso_min)
    if peso_max is not None:
        q = q.filter(Alumno.peso <= peso_max)

    fnac_desde, fnac_hasta = _rango_fechas_por_edad(edad_min, edad_max)
    if fnac_desde and fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento.between(fnac_desde, fnac_hasta))
    elif fnac_desde:
        q = q.filter(Alumno.fecha_nacimiento >= fnac_desde)
    elif fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento <= fnac_hasta)

    q = q.order_by(Sucursal.nombre.asc(), Alumno.apellidos.asc(), Alumno.nombres.asc())
    filas = q.all()

    data = []
    for alumno, sucursal, grado in filas:
        data.append({
            "ID": alumno.numero_identidad,
            "Apellidos": alumno.apellidos,
            "Nombres": alumno.nombres,
            "Género": alumno.genero,
            "Fecha nacimiento": alumno.fecha_nacimiento,
            "Peso": alumno.peso,
            "Sucursal": sucursal.nombre if sucursal else "",
            "Grado": grado.nombre if grado else "",
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Combate")
    output.seek(0)

    nombre = f"reporte_combate_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(output, as_attachment=True, download_name=nombre,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


@reportes_bp.route("/poomsae/export/excel", methods=["GET"])
@login_required
def poomsae_export_excel():
    sucursal_id = request.args.get("sucursal_id", type=int)
    genero = request.args.get("genero")
    edad_min = request.args.get("edad_min", type=int)
    edad_max = request.args.get("edad_max", type=int)
    grado_id = request.args.get("grado_id", type=int)
    tipo_grado = request.args.get("tipo_grado")

    q = (
        db.session.query(Alumno, Sucursal, Grado)
        .join(Sucursal, Sucursal.id == Alumno.sucursal_id)
        .outerjoin(Grado, Grado.id == Alumno.grado_id)
    )
    q = _aplicar_seguridad_por_rol(q)

    if sucursal_id:
        q = q.filter(Alumno.sucursal_id == sucursal_id)
    if genero:
        q = q.filter(Alumno.genero == genero)
    if grado_id:
        q = q.filter(Alumno.grado_id == grado_id)
    if tipo_grado:
        q = q.filter(Grado.tipo == tipo_grado)

    fecha_base = _get_fecha_base()
    fnac_desde, fnac_hasta = _rango_fechas_por_edad(edad_min, edad_max, fecha_base)
    if fnac_desde and fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento.between(fnac_desde, fnac_hasta))
    elif fnac_desde:
        q = q.filter(Alumno.fecha_nacimiento >= fnac_desde)
    elif fnac_hasta:
        q = q.filter(Alumno.fecha_nacimiento <= fnac_hasta)

    q = q.order_by(Sucursal.nombre.asc(), Alumno.apellidos.asc(), Alumno.nombres.asc())
    filas = q.all()

    data = []
    for alumno, sucursal, grado in filas:
        data.append({
            "ID": alumno.numero_identidad,
            "Apellidos": alumno.apellidos,
            "Nombres": alumno.nombres,
            "Género": alumno.genero,
            "Fecha nacimiento": alumno.fecha_nacimiento,
            "Sucursal": sucursal.nombre if sucursal else "",
            "Grado": grado.nombre if grado else "",
            "Tipo grado": grado.tipo if grado else "",
        })

    df = pd.DataFrame(data)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Poomsae")
    output.seek(0)

    nombre = f"reporte_poomsae_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
    return send_file(output, as_attachment=True, download_name=nombre,
                     mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    def _edad_en_fecha(fnac: date, fecha_base: date) -> int | None:
        if not fnac:
            return None
        years = fecha_base.year - fnac.year
        if (fecha_base.month, fecha_base.day) < (fnac.month, fnac.day):
            years -= 1
        return years