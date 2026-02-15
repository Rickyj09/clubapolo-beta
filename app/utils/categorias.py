from sqlalchemy import or_, case
from app.models.categoriascompetencia import CategoriaCompetencia

def calcular_edad(fecha_nacimiento, fecha_evento):
    if not fecha_nacimiento or not fecha_evento:
        return 0
    years = fecha_evento.year - fecha_nacimiento.year
    if (fecha_evento.month, fecha_evento.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        years -= 1
    return years

def obtener_categoria_competencia(*, alumno, torneo, modalidad):
    """
    Retorna UNA CategoriaCompetencia válida o None.
    Permite grado_id NULL como "aplica a todos".
    """

    edad = calcular_edad(alumno.fecha_nacimiento, torneo.fecha)
    sexo = alumno.genero
    peso = alumno.peso or 0

    # Regla negocio: combate usa "grado técnico" 99, poomsae usa el grado real
    if modalidad == "COMBATE":
        grado_usado = 99
    else:
        grado_usado = alumno.grado_id

    query = CategoriaCompetencia.query.filter(
        CategoriaCompetencia.modalidad == modalidad,
        CategoriaCompetencia.sexo == sexo,
        CategoriaCompetencia.activo == 1,
        CategoriaCompetencia.edad_min <= edad,
        CategoriaCompetencia.edad_max >= edad,
        # ✅ acepta grado exacto O NULL (aplica a todos)
        or_(CategoriaCompetencia.grado_id == grado_usado, CategoriaCompetencia.grado_id.is_(None))
    )

    if modalidad == "COMBATE":
        query = query.filter(
            CategoriaCompetencia.peso_min <= peso,
            CategoriaCompetencia.peso_max >= peso
        )
    elif modalidad == "POOMSAE":
        pass
    else:
        return None

    categoria = query.order_by(
        # primero los que NO son NULL (0), después los NULL (1)
        case((CategoriaCompetencia.grado_id.is_(None), 1), else_=0).asc(),
        # dentro de los no-nulos, preferir el grado más alto / exacto
        CategoriaCompetencia.grado_id.desc()
    ).first()

    return categoria