import os

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app
)
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models.alumno import Alumno
from app.models.categoria import Categoria
from app.models.sucursal import Sucursal
from app.models.Grado import Grado
from app.models.participacion import Participacion
from app.models.torneo import Torneo
from app.models.medalla import Medalla
from datetime import date
from app.models.asistencia import Asistencia

# 🔍 Auditoría
from app.utils.auditoria import registrar_auditoria


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

    if current_user.has_role("ADMIN"):
        alumnos = Alumno.query.order_by(Alumno.id).all()

    elif current_user.has_role("PROFESOR"):
        alumnos = (
            Alumno.query
            .filter_by(sucursal_id=current_user.sucursal_id)
            .order_by(Alumno.id)
            .all()
        )
    else:
        alumnos = []

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

    if current_user.has_role("ADMIN"):
        sucursales = Sucursal.query.filter_by(activo=True).order_by(Sucursal.nombre).all()

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
        if not categoria_id:
            flash("Debe seleccionar una categoría", "danger")
            return redirect(request.url)

        if current_user.has_role("ADMIN"):
            sucursal_id = request.form.get("sucursal_id")
        else:
            sucursal_id = current_user.sucursal_id

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

        # 🔍 AUDITORÍA - CREACIÓN
        registrar_auditoria(
            accion="CREATE",
            entidad="ALUMNO",
            entidad_id=alumno.id,
            descripcion="Creación de alumno",
            datos_despues={
                "nombres": alumno.nombres,
                "apellidos": alumno.apellidos,
                "fecha_nacimiento": str(alumno.fecha_nacimiento),
                "genero": alumno.genero,
                "categoria_id": alumno.categoria_id,
                "sucursal_id": alumno.sucursal_id
            }
        )

        # 📸 FOTO
        archivo = request.files.get("foto")
        if archivo and archivo.filename:
            nombre_archivo = secure_filename(archivo.filename)
            ruta = os.path.join(
                current_app.config["UPLOAD_FOLDER"],
                nombre_archivo
            )
            archivo.save(ruta)
            alumno.foto = nombre_archivo
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

    # Seguridad por sucursal
    if current_user.has_role("PROFESOR"):
        if alumno.sucursal_id != current_user.sucursal_id:
            flash("No tiene permisos para editar este alumno", "danger")
            return redirect(url_for("alumnos.index"))

    grados = Grado.query.filter_by(activo=True).order_by(Grado.orden).all()

    if request.method == "POST":

        # 🔍 DATOS ANTES
        datos_antes = {
            "nombres": alumno.nombres,
            "apellidos": alumno.apellidos,
            "peso": alumno.peso,
            "flexibilidad": alumno.flexibilidad,
            "grado_id": alumno.grado_id,
            "foto": alumno.foto
        }

        alumno.nombres = request.form["nombres"]
        alumno.apellidos = request.form["apellidos"]
        alumno.peso = request.form.get("peso") or None
        alumno.flexibilidad = request.form.get("flexibilidad")
        alumno.grado_id = request.form.get("grado_id") or None

        # 📸 FOTO
        archivo = request.files.get("foto")
        if archivo and archivo.filename:
            nombre_archivo = secure_filename(archivo.filename)
            ruta = os.path.join(current_app.config["UPLOAD_FOLDER"], nombre_archivo)
            archivo.save(ruta)
            alumno.foto = nombre_archivo

        db.session.commit()

        # 🔍 AUDITORÍA - EDICIÓN
        registrar_auditoria(
            accion="UPDATE",
            entidad="ALUMNO",
            entidad_id=alumno.id,
            descripcion="Edición de alumno",
            datos_antes=datos_antes,
            datos_despues={
                "nombres": alumno.nombres,
                "apellidos": alumno.apellidos,
                "peso": alumno.peso,
                "flexibilidad": alumno.flexibilidad,
                "grado_id": alumno.grado_id,
                "foto": alumno.foto
            }
        )

        flash("Alumno actualizado correctamente", "success")
        return redirect(url_for("alumnos.index"))

    # =========================
    # PARTICIPACIONES (ya lo tenías)
    # =========================
    participaciones = (
        db.session.query(Participacion)
        .join(Torneo, Torneo.id == Participacion.torneo_id)
        .outerjoin(Medalla, Medalla.id == Participacion.medalla_id)
        .filter(Participacion.alumno_id == alumno.id)
        .order_by(Torneo.fecha.desc())
        .all()
    )

    # =========================
    # ASISTENCIAS (NUEVO)
    # =========================
    hoy = date.today()

    asistencia_hoy = None
    historial_asistencias = []

    if alumno.sucursal_id:
        asistencia_hoy = Asistencia.query.filter_by(
            fecha=hoy,
            sucursal_id=alumno.sucursal_id,
            alumno_id=alumno.id
        ).first()

        hoy = date.today()

        asistencia_hoy = Asistencia.query.filter_by(
                alumno_id=alumno.id,
                sucursal_id=alumno.sucursal_id,
                fecha=hoy
            ).first()

        historial_asistencias = (
            Asistencia.query
            .join(Sucursal, Sucursal.id == Asistencia.sucursal_id)
            .filter(
                Asistencia.alumno_id == alumno.id,
                Asistencia.sucursal_id == alumno.sucursal_id
            )
            .order_by(Asistencia.fecha.desc())
            .limit(10)
            .all()
)

    return render_template(
        "alumnos/editar.html",
        alumno=alumno,
        grados=grados,
        participaciones=participaciones,
        # variables para el bloque asistencia
        fecha_asistencia=hoy.isoformat(),
        asistencia=asistencia_hoy,
        historial_asistencias=historial_asistencias
    )

# =========================
# ELIMINAR ALUMNO
# =========================
@alumnos_bp.route("/<int:id>/eliminar", methods=["POST"])
@login_required
def eliminar(id):

    alumno = Alumno.query.get_or_404(id)

    if current_user.has_role("PROFESOR"):
        if alumno.sucursal_id != current_user.sucursal_id:
            flash("No tiene permisos para eliminar este alumno", "danger")
            return redirect(url_for("alumnos.index"))

    # 🔍 AUDITORÍA - ELIMINACIÓN (ANTES)
    registrar_auditoria(
        accion="DELETE",
        entidad="ALUMNO",
        entidad_id=alumno.id,
        descripcion=f"Eliminación de alumno {alumno.nombres} {alumno.apellidos}",
        datos_antes={
            "nombres": alumno.nombres,
            "apellidos": alumno.apellidos,
            "sucursal_id": alumno.sucursal_id
        }
    )

    db.session.delete(alumno)
    db.session.commit()

    flash("Alumno eliminado correctamente", "success")
    return redirect(url_for("alumnos.index"))

# =========================
# PERFIL / HISTORIAL
# =========================
@alumnos_bp.route("/<int:id>/perfil")
@login_required
def perfil(id):

    alumno = Alumno.query.get_or_404(id)

    if current_user.has_role("PROFESOR"):
        if alumno.sucursal_id != current_user.sucursal_id:
            flash("No tiene acceso a este alumno", "danger")
            return redirect(url_for("alumnos.index"))

    participaciones = (
        db.session.query(Participacion)
        .join(Torneo, Torneo.id == Participacion.torneo_id)
        .outerjoin(Medalla, Medalla.id == Participacion.medalla_id)
        .filter(Participacion.alumno_id == alumno.id)
        .order_by(Torneo.fecha.desc())
        .all()
    )

    return render_template(
        "alumnos/perfil.html",
        alumno=alumno,
        participaciones=participaciones
    )
