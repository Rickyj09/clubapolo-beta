from datetime import date
from app.models import Pago


def meses_entre(inicio, fin):
    meses = []
    y, m = inicio.year, inicio.month

    while (y < fin.year) or (y == fin.year and m <= fin.month):
        meses.append((m, y))
        m += 1
        if m > 12:
            m = 1
            y += 1

    return meses


def calcular_deuda(alumno):
    hoy = date.today()

    inicio = alumno.fecha_ingreso or date(hoy.year, 1, 1)

    meses_totales = meses_entre(inicio, hoy)

    pagos = Pago.query.filter_by(alumno_id=alumno.id).all()
    meses_pagados = {(p.mes, p.anio) for p in pagos}

    pendientes = [
        {"mes": m, "anio": y}
        for (m, y) in meses_totales
        if (m, y) not in meses_pagados
    ]

    return {
        "total_meses": len(meses_totales),
        "pagados": len(meses_pagados),
        "pendientes": pendientes,
        "cantidad_pendientes": len(pendientes)
    }
