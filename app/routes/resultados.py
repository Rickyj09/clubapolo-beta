from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required
from werkzeug.utils import secure_filename
import os, time
from sqlalchemy import func

from app.extensions import db
from app.models.torneo import Torneo
from app.models.medalla import Medalla
from app.models.alumno import Alumno
from app.models.participacion import Participacion
from app.models.academia import Academia
from app.models.categoriascompetencia import CategoriaCompetencia
from app.models.resultado_categoria import ResultadoCategoria
from app.models.resultado_detalle import ResultadoDetalle

resultados_bp = Blueprint("resultados", __name__, url_prefix="/resultados")

@resultados_bp.route("/academias/crear", methods=["POST"])
@login_required
def crear_academia():
    nombre = (request.form.get("nombre") or "").strip()
    if not nombre:
        return jsonify({"ok": False, "error": "Nombre requerido"}), 400

    # Buscar si ya existe (case-insensitive)
    existente = Academia.query.filter(func.lower(Academia.nombre) == nombre.lower()).first()
    if existente:
        return jsonify({"ok": True, "id": existente.id, "nombre": existente.nombre, "existe": True})

    a = Academia(nombre=nombre, activo=True)
    db.session.add(a)
    db.session.commit()

    return jsonify({"ok": True, "id": a.id, "nombre": a.nombre, "existe": False})

@resultados_bp.route("/torneo/<int:torneo_id>/nuevo", methods=["GET", "POST"])
@login_required
def nuevo(torneo_id):
    torneo = Torneo.query.get_or_404(torneo_id)

    categorias = CategoriaCompetencia.query.order_by(CategoriaCompetencia.nombre).all()
    academias = Academia.query.filter_by(activo=True).order_by(Academia.nombre).all()

    if request.method == "POST":
        modalidad = (request.form.get("modalidad") or "").strip().upper()
        categoria_id = request.form.get("categoria_id")
        total_competidores = int(request.form.get("total_competidores") or 0)
        observacion = request.form.get("observacion")

        if modalidad not in ("POOMSAE", "COMBATE"):
            flash("Modalidad inválida", "danger")
            return redirect(request.url)

        if not categoria_id:
            flash("Debe seleccionar una categoría", "danger")
            return redirect(request.url)

        # ===== Guardar foto acta =====
        folder = current_app.config.get("ACTAS_UPLOAD_FOLDER")
        if not folder:
            flash("No está configurado ACTAS_UPLOAD_FOLDER en la app.", "danger")
            return redirect(request.url)

        os.makedirs(folder, exist_ok=True)

        archivo = request.files.get("acta_foto")
        nombre_archivo = None

        if archivo and archivo.filename:
            ext = os.path.splitext(secure_filename(archivo.filename))[1].lower()
            nombre_archivo = f"acta_{torneo.id}_{categoria_id}_{modalidad}_{int(time.time())}{ext}"
            archivo.save(os.path.join(folder, nombre_archivo))

        # ===== Crear ResultadoCategoria =====
        rc = ResultadoCategoria(
            torneo_id=torneo.id,
            categoria_id=int(categoria_id),
            modalidad=modalidad,
            total_competidores=total_competidores,
            acta_foto=nombre_archivo,
            observacion=observacion
        )
        db.session.add(rc)
        db.session.commit()

        flash("Acta/categoría creada. Ahora ingresa los resultados.", "success")
        return redirect(url_for("resultados.editar_categoria", resultado_categoria_id=rc.id))

    return render_template(
        "resultados/nuevo.html",
        torneo=torneo,
        categorias=categorias,
        academias=academias
    )

@resultados_bp.route("/categoria/<int:resultado_categoria_id>/editar", methods=["GET", "POST"])
@login_required
def editar_categoria(resultado_categoria_id):
    rc = ResultadoCategoria.query.get_or_404(resultado_categoria_id)
    torneo = Torneo.query.get_or_404(rc.torneo_id)

    medallas = Medalla.query.order_by(Medalla.orden).all()
    academias = Academia.query.filter_by(activo=True).order_by(Academia.nombre).all()

    # --- DETALLES (con precarga automática) ---
    detalles = ResultadoDetalle.query.filter_by(resultado_categoria_id=rc.id).all()

    # Si no hay detalles aún, precargamos desde Participacion (solo en GET)
    if request.method == "GET" and len(detalles) == 0:
        participaciones = Participacion.query.filter_by(
            torneo_id=rc.torneo_id,
            categoria_id=rc.categoria_id,
            modalidad=rc.modalidad
        ).all()

        for p in participaciones:
            alumno = Alumno.query.get(p.alumno_id)

            # intenta academia desde sucursal (si tu modelo la tiene)
            academia_id = None
            if alumno and getattr(alumno, "sucursal", None) and getattr(alumno.sucursal, "academia_id", None):
                academia_id = alumno.sucursal.academia_id

            # fallback: primera academia activa
            if not academia_id and academias:
                academia_id = academias[0].id

            det = ResultadoDetalle(
                resultado_categoria_id=rc.id,
                alumno_id=p.alumno_id,
                academia_id=academia_id,
                puesto=None,
                medalla_id=None,
                puntaje=None,
                nombre_competidor=None
            )
            db.session.add(det)

        db.session.commit()

        # recargar
        detalles = ResultadoDetalle.query.filter_by(resultado_categoria_id=rc.id).all()

    # --- POST: guardar resultados ---
    if request.method == "POST":
        ResultadoDetalle.query.filter_by(resultado_categoria_id=rc.id).delete()
        filas = int(request.form.get("filas") or 0)

        for i in range(filas):
            puesto = request.form.get(f"puesto_{i}") or None
            medalla_id = request.form.get(f"medalla_{i}") or None
            puntaje = request.form.get(f"puntaje_{i}") or None

            academia_id = request.form.get(f"academia_{i}") or None
            alumno_id = request.form.get(f"alumno_{i}") or None
            nombre_competidor = (request.form.get(f"nombre_{i}") or "").strip() or None

            if not (academia_id and (alumno_id or nombre_competidor)):
                continue

            det = ResultadoDetalle(
                resultado_categoria_id=rc.id,
                alumno_id=int(alumno_id) if alumno_id else None,
                nombre_competidor=nombre_competidor,
                academia_id=int(academia_id),
                puesto=int(puesto) if puesto else None,
                medalla_id=int(medalla_id) if medalla_id else None,
                puntaje=float(puntaje) if (puntaje and rc.modalidad == "POOMSAE") else None,
            )
            db.session.add(det)

        db.session.commit()

        # Sincronizar participaciones (solo internos)
        detalles_guardados = ResultadoDetalle.query.filter_by(resultado_categoria_id=rc.id).all()
        for det in detalles_guardados:
            if not det.alumno_id:
                continue

            p = Participacion.query.filter_by(
                torneo_id=rc.torneo_id,
                alumno_id=det.alumno_id,
                modalidad=rc.modalidad
            ).first()

            if not p:
                p = Participacion(
                    torneo_id=rc.torneo_id,
                    alumno_id=det.alumno_id,
                    modalidad=rc.modalidad,
                    categoria_id=rc.categoria_id
                )
                db.session.add(p)

            p.medalla_id = det.medalla_id
            p.puesto = det.puesto
            p.puntaje = det.puntaje if rc.modalidad == "POOMSAE" else None

        db.session.commit()

        flash("Resultados guardados y sincronizados con el historial del alumno.", "success")
        return redirect(request.url)

    alumnos = Alumno.query.filter_by(activo=True).order_by(Alumno.apellidos, Alumno.nombres).all()

    return render_template(
        "resultados/editar.html",
        rc=rc,
        torneo=torneo,
        detalles=detalles,
        alumnos=alumnos,
        academias=academias,
        medallas=medallas
    )



@resultados_bp.route("/seleccionar-torneo", methods=["GET"])
@login_required
def seleccionar_torneo():
    torneos = Torneo.query.order_by(Torneo.fecha.desc()).all()
    return render_template("resultados/seleccionar_torneo.html", torneos=torneos)

