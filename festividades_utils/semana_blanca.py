from datetime import datetime

from .utils import fecha_en_intervalo, restar_dias_fechas, sumar_dias_fecha

__fechas_semana_blanca = {}


def calculo_fechas_semana_blanca(anno):
    """
    Calcula el intervalo de fechas ente las que tuvo lugar la semana blanca de ese anno.
    :param anno: anno de la semana blanca
    :return: tupla con la fecha inicio y la fecha fin de la semana blanca
    """
    dia = datetime(anno, 2, 28).weekday()
    inicio_semana = restar_dias_fechas(28, 2, anno, dia)
    fin_semana = sumar_dias_fecha(inicio_semana[0], inicio_semana[1], inicio_semana[2], 6)
    return inicio_semana, fin_semana


def es_semana_blanca(dia, mes, anno):
    """
    Te devuelve si una fecha concreta es semana blanca
    :param dia: int
    :param mes: int
    :param anno: int
    :return: True si es semana blanca, False si no
    """
    fechas = __fechas_semana_blanca.get(anno)
    if not fechas:
        fechas = __fechas_semana_blanca[anno] = calculo_fechas_semana_blanca(anno)
    semana = fecha_en_intervalo(fechas, dia, mes, anno)
    return semana


def devolver_semana_blanca(dia, mes, anno):
    """
    Te devuelve una representacion en string de si la fecha pasada como parametro es carnaval
    :param dia: int
    :param mes: int
    :param anno: int
    :return: Te devuelve Semana_blanca, Semana_blanca si es Semana_blanca,
    Semana_blanca, Dia_Andalucia si es el Dia_Andalucia, None, None en caso de que no sea semana blanca
    """
    resultado = None, None
    if es_semana_blanca(dia, mes, anno):
        if dia == 28 and mes == 2:
            resultado = 'Dia_Andalucia'
        else:
            resultado = 'Semana_blanca'
        resultado = 'Semana_blanca', resultado
    return resultado
