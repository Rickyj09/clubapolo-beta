from flask_login import current_user
from flask import request
from app.extensions import db
from app.models.auditoria import Auditoria
from app.utils.json_utils import json_safe


def registrar_auditoria(
    *,
    accion,
    entidad,
    entidad_id=None,
    descripcion=None,
    datos_antes=None,
    datos_despues=None
):
    auditoria = Auditoria(
        usuario_id=current_user.id,
        usuario_nombre=getattr(current_user, "username", "desconocido"),
        accion=accion,
        entidad=entidad,
        entidad_id=entidad_id,
        descripcion=descripcion,
        datos_antes=json_safe(datos_antes),
        datos_despues=json_safe(datos_despues),
        ip=request.remote_addr
    )
    db.session.add(auditoria)
    db.session.commit()
