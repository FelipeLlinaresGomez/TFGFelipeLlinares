from .utils import fecha_en_intervalo, calcular_domingo_pascua, restar_dias_fechas

__fechas_carnaval = {}


def calculo_fechas_carnaval(anno):
    """
    Calcula el intervalo de fechas ente las que tuvo lugar el carnaval de ese anno.
    :param anno: anno del carnaval
    :return: tupla con la fecha inicio y la fecha fin del carnaval
    """
    (dia, mes, anno) = calcular_domingo_pascua(anno)
    fin_carnaval = restar_dias_fechas(dia, mes, anno, 47)
    inicio_carnaval = restar_dias_fechas(fin_carnaval[0], fin_carnaval[1], fin_carnaval[2], 5)
    return inicio_carnaval, fin_carnaval


def es_carnaval(dia, mes, anno):
    """
    Te devuelve si una fecha concreta es carnaval
    :param dia: int
    :param mes: int
    :param anno: int
    :return: True si es carnaval, False si no
    """
    fechas = __fechas_carnaval.get(anno)
    if not fechas:
        fechas = __fechas_carnaval[anno] = calculo_fechas_carnaval(anno)
    semana = fecha_en_intervalo(fechas, dia, mes, anno)
    return semana


def devolver_carnaval(dia, mes, anno):
    """
    Te devuelve una representacion en string de si la fecha pasada como parametro es carnaval
    :param dia: int
    :param mes: int
    :param anno: int
    :return: Te devuelve Carnaval, Carnaval si es carnaval None, None en caso contrario
    """
    resultado = None, None
    if es_carnaval(dia, mes, anno):
        resultado = 'Carnaval', 'Carnaval'
    return resultado
