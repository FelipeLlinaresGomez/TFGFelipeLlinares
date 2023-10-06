from .carnaval import devolver_carnaval
from .feria_malaga import devolver_feria_malaga
from .navidad import devolver_navidad
from .otros import get_festividad_unico_dia
from .semana_blanca import devolver_semana_blanca
from .semana_santa import devolver_dia_semana_santa


def get_festividad(dia: int, mes: int, anno: int):
    """
    Metodo principal del modulo, te devuelve la representacion de si es un dia festivo dado un dia, mes y anno
    :param dia: int
    :param mes: int
    :param anno: int
    :return: fecha general, fecha concreta
    """
    dia_f, dia_c = get_festividad_unico_dia(dia, mes)
    if not dia_f:
        dia_f, dia_c = devolver_navidad(dia, mes)
        if not dia_f:
            if mes <= 2:
                dia_f, dia_c = devolver_semana_blanca(dia, mes, anno)
                if not dia_f:
                    dia_f, dia_c = devolver_carnaval(dia, mes, anno)
            else:
                dia_f, dia_c = devolver_dia_semana_santa(dia, mes, anno)
                if not dia_f:
                    dia_f, dia_c = devolver_feria_malaga(dia, mes, anno)
    return dia_f, dia_c
