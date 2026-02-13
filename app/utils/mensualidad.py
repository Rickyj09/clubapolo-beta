from datetime import date
from app.models.pago import Pago

def mensualidad_pagada(alumno_id: int, sucursal_id: int, fecha: date) -> bool:
    """
    True si existe un pago del mes/año actual para ese alumno y sucursal.
    Ajusta si tu lógica de pagos no depende de sucursal_id.
    """
    existe = (
        Pago.query
        .filter(Pago.alumno_id == alumno_id)
        .filter(Pago.sucursal_id == sucursal_id)
        .filter(Pago.anio == fecha.year)
        .filter(Pago.mes == fecha.month)
        .first()
    )
    return existe is not None


def aviso_mensualidad(fecha: date, pagada: bool) -> dict | None:
    """
    Devuelve un dict para UI: {type, title, text}
    type: 'warning' (3-5) o 'danger' (>=6)
    """
    if pagada:
        return None

    dia = fecha.day
    if 3 <= dia <= 5:
        return {
            "type": "warning",
            "title": "Aviso de mensualidad",
            "text": "No registras el pago de tu mensualidad. Tienes hasta el día 5 para pagarla."
        }

    if dia >= 6:
        return {
            "type": "danger",
            "title": "Atraso de mensualidad",
            "text": "Registras atraso en el pago de tu mensualidad. Por favor regulariza tu pago."
        }

    return None  # días 1-2 sin aviso