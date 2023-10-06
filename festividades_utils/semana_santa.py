from enum import Enum

from .utils import calcular_domingo_pascua, fecha_en_intervalo

__fechas_semana_santa = {}


class DiasSemanaSanta(Enum):
    Viernes_dolores = 0
    Sabado_pasion = 1
    Domingo_ramos = 2
    Lunes_santo = 3
    Martes_santo = 4
    Miercoloes_santo = 5
    Jueves_santo = 6
    Viernes_santo = 7
    Sabado_santo = 8
    Domingo_resurreccion = 9
    Lunes_pascua = 10


def devolver_dia_semana_santa(dia, mes, anno):
    """
    Te devuelve una representacion en string de si la fecha pasada como parametro es Semana Santa
    :param dia: int
    :param mes: int
    :param anno: int
    :return: Te devuelve Semana_santa, Dia_concreto de la Semana Santa si es Semana Santa None, None en caso contrario
    """
    resultado = None, None
    if es_semana_santa(dia, mes, anno):
        fechas = __fechas_semana_santa.get(anno)
        var = dia - fechas[0][0]
        if var < 0:
            if fechas[0][1] == 3:
                var = 31 + var
            else:
                var = 30 + var
        resultado = 'Semana_santa', DiasSemanaSanta(var).name
    return resultado


def es_semana_santa(dia, mes, anno) -> bool:
    """
    Te devuelve si una fecha concreta es Semana Santa
    :param dia: int
    :param mes: int
    :param anno: int
    :return: True si es Semana Santa, False si no
    """
    fechas = __fechas_semana_santa.get(anno)
    if not fechas:
        fechas = __fechas_semana_santa[anno] = calculo_fecha_semana_santa(anno)
    semana = fecha_en_intervalo(fechas, dia, mes, anno)
    return semana


def calculo_fecha_semana_santa(anno):
    """
    Calcula el intervalo de fechas ente las que tuvo lugar la Semana Santa de ese anno.
    :param anno: anno de la Semana Santa
    :return: tupla con la fecha inicio y la fecha fin de la Semana Santa
    """
    (dia, mes, anno) = calcular_domingo_pascua(anno)
    max_dia = 31
    if mes == 4:
        max_dia = -1000
    if dia == max_dia:
        lunes_pascua = (1, mes + 1, anno)
    else:
        lunes_pascua = (dia + 1, mes, anno)

    if lunes_pascua[1] == 3:
        dia_v = lunes_pascua[0] - 10
        mes_v = 3
        if dia_v < 1:
            dia_v = 28 + dia_v
            mes_v = 2
        viernes_dolores = (dia_v, mes_v, anno)
    else:
        dia_v = lunes_pascua[0] - 10
        mes_v = 4
        if dia_v < 1:
            dia_v = 31 + dia_v
            mes_v = 3
        viernes_dolores = (dia_v, mes_v, anno)
    return viernes_dolores, lunes_pascua
