from datetime import datetime

from .utils import fecha_en_intervalo

__fechas_feria_malaga = {}


def calculo_fechas_feria_malaga(anno):
    """
    Calcula el intervalo de fechas ente las que tuvo lugar la feria de ese anno.
    Sujeto a un pequeño error de +-2 dias
    :param anno: anno de la feria
    :return: tupla con la fecha inicio y la fecha fin del feria
    """
    dia_quince = datetime(anno, 8, 15).weekday()
    viernes = 4 - dia_quince
    if viernes > 0:
        if viernes < 2:
            viernes = 0
        else:
            viernes -= 7
    viernes += 15
    domingo = viernes + 9
    inicio_feria = viernes, 8, anno
    fin_feria = domingo, 8, anno
    return inicio_feria, fin_feria


def es_feria_malaga(dia, mes, anno):
    """
    Te devuelve si una fecha concreta es feria
    Sujeto a un pequeño error de +-2 dias
    :param dia: int
    :param mes: int
    :param anno: int
    :return: True si es feria, False si no
    """
    fechas = __fechas_feria_malaga.get(anno)
    if not fechas:
        fechas = __fechas_feria_malaga[anno] = calculo_fechas_feria_malaga(anno)
    semana = fecha_en_intervalo(fechas, dia, mes, anno)
    return semana


def devolver_feria_malaga(dia, mes, anno):
    """
    Te devuelve una representacion en string de si la fecha pasada como parametro es feria
    Sujeto a un pequeño error de +-2 dias
    :param dia: int
    :param mes: int
    :param anno: int
    :return: Te devuelve Feria_malaga, Feria_malaga si es carnaval None, None en caso contrario
    """
    resultado = None,None
    if es_feria_malaga(dia, mes, anno):
        resultado = 'Feria_malaga', 'Feria_malaga'
    return resultado
