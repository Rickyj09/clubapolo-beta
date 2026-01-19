from datetime import date

from app.models.categoriascompetencia import CategoriaCompetencia  # ajusta al nombre real del archivo/modelo


def calcular_edad(fecha_nacimiento: date, fecha_referencia: date) -> int:
    edad = fecha_referencia.year - fecha_nacimiento.year
    if (fecha_referencia.month, fecha_referencia.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    return edad


def normalizar_sexo(genero: str) -> str:
    """
    Devuelve 'M' o 'F' a partir de valores típicos:
    'M', 'F', 'Masculino', 'Femenino', 'Hombre', 'Mujer', etc.
    """
    if not genero:
        return ""
    g = genero.strip().lower()
    if g in ("m", "masculino", "hombre", "varon", "varón"):
        return "M"
    if g in ("f", "femenino", "mujer", "dama"):
        return "F"
    return ""


def obtener_categoria_competencia(alumno, torneo, modalidad: str):
    """
    - POOMSAE: edad + sexo + grado_id
    - COMBATE: edad + sexo + peso
    """
    if not alumno or not torneo or not modalidad:
        return None

    modalidad = modalidad.strip().upper()
    if modalidad not in ("POOMSAE", "COMBATE"):
        return None

    sexo = normalizar_sexo(getattr(alumno, "genero", None))
    if sexo not in ("M", "F"):
        return None

    if not getattr(alumno, "fecha_nacimiento", None):
        return None

    edad = calcular_edad(alumno.fecha_nacimiento, torneo.fecha)

    q = (
        CategoriaCompetencia.query
        .filter_by(activo=True, modalidad=modalidad, sexo=sexo)
        .filter(CategoriaCompetencia.edad_min <= edad)
        .filter(CategoriaCompetencia.edad_max >= edad)
    )

    if modalidad == "POOMSAE":
        # exige grado
        if not getattr(alumno, "grado_id", None):
            return None
        q = q.filter(CategoriaCompetencia.grado_id == alumno.grado_id)

    if modalidad == "COMBATE":
        # exige peso
        peso = getattr(alumno, "peso", None)
        if peso is None:
            return None
        q = (
            q.filter(CategoriaCompetencia.peso_min <= float(peso))
             .filter(CategoriaCompetencia.peso_max >= float(peso))
        )

    # Si existiera más de una coincidencia, toma la más específica (normalmente única)
    return q.order_by(CategoriaCompetencia.id.asc()).first()
