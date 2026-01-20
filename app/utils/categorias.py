from datetime import date
from app.models.categoriascompetencia import CategoriaCompetencia


def calcular_edad(fecha_nacimiento, fecha_referencia):
    edad = fecha_referencia.year - fecha_nacimiento.year
    if (fecha_referencia.month, fecha_referencia.day) < (
        fecha_nacimiento.month,
        fecha_nacimiento.day
    ):
        edad -= 1
    return edad


def obtener_categoria_competencia(*, alumno, torneo, modalidad):
    """
    Retorna UNA CategoriaCompetencia válida o None
    """

    # =========================
    # DATOS BASE
    # =========================
    edad = calcular_edad(alumno.fecha_nacimiento, torneo.fecha)
    sexo = alumno.genero
    peso = alumno.peso or 0

    # 🔑 regla de negocio
    if modalidad == "COMBATE":
        grado_id = 99  # grado técnico
    else:
        grado_id = alumno.grado_id

    print("DEBUG CATEGORIA")
    print("Alumno:", alumno.id, sexo, edad, alumno.fecha_nacimiento)
    print("Torneo:", torneo.id, torneo.fecha)
    print("Modalidad:", modalidad)
    print("Grado usado:", grado_id)
    print("Peso:", peso)

    # =========================
    # QUERY BASE
    # =========================
    query = CategoriaCompetencia.query.filter(
        CategoriaCompetencia.modalidad == modalidad,
        CategoriaCompetencia.sexo == sexo,
        CategoriaCompetencia.grado_id == grado_id,
        CategoriaCompetencia.activo == 1,
        CategoriaCompetencia.edad_min <= edad,
        CategoriaCompetencia.edad_max >= edad
    )

    # =========================
    # FILTRO POR MODALIDAD
    # =========================
    if modalidad == "COMBATE":
        query = query.filter(
            CategoriaCompetencia.peso_min <= peso,
            CategoriaCompetencia.peso_max >= peso
        )

    elif modalidad == "POOMSAE":
        # poomsae NO usa peso → no filtrar peso
        pass

    else:
        print("❌ Modalidad no soportada:", modalidad)
        return None

    categoria = query.first()

    # =========================
    # VALIDACIÓN FINAL
    # =========================
    if not categoria:
        print("❌ CATEGORIA NO ENCONTRADA")
        print("Buscado:")
        print(
            f"modalidad={modalidad}, sexo={sexo}, edad={edad}, "
            f"grado_id={grado_id}, peso={peso}"
        )
        return None

    print("✅ Categoria encontrada:", categoria.id, categoria.nombre)
    return categoria
