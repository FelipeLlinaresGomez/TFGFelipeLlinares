def calcular_domingo_pascua(anno):
    """
    Calcula la fecha del domingo de pascua, algoritmo sacado de Internet
    :param anno: anno sobre el que calcular el domingo de pascua: int
    :return: dia, mes, anno
    """
    # Constantes
    M = 24
    N = 5

    a = anno % 19
    b = anno % 4
    c = anno % 7
    d = (19 * a + M) % 30
    e = (2 * b + 4 * c + 6 * d + N) % 7

    if d + e < 10:
        dia = d + e + 22
        mes = 3
    else:
        dia = d + e - 9
        mes = 4

    if dia == 26 and mes == 3:
        dia = 19
    if dia == 25 and mes == 4 and d == 28 and e == 6 and a > 10:
        dia = 18
    return dia, mes, anno


def es_bisiesto(a) -> bool:
    """
    Calcula si el anno es bisiesto
    :param a: anno:int
    :return: True si es bisisesto, False si no
    """
    return a % 4 == 0 and a % 100 != 0 or a % 400 == 0


def fecha_en_intervalo(fechas, dia, mes, anno):
    """
    Calcula si una fecha esá en un intervalo
    :param fechas: fechas sobre las que hace la pregunta, tupla tuplas
    :param dia: int
    :param mes: int
    :param anno: int
    :return: True si esta dentro del intervalo, False si no
    """
    semana = False
    if fechas[0][1] <= mes <= fechas[1][1]:
        if fechas[0][1] == fechas[1][1]:
            if fechas[0][0] <= dia <= fechas[1][0]:
                semana = True
        else:
            if (fechas[0][0] <= dia and mes == fechas[0][1]) or (dia <= fechas[1][0] and mes == fechas[1][1]):
                semana = True
    return semana


__meses = {1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30, 7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31}


def restar_dias_fechas(dia, mes, anno, dias_restar):
    """
    Resta x dias a la fecha pasada como paametro
    :param dia: int
    :param mes: int
    :param anno: int
    :param dias_restar: int
    :return: dia, mes, anno con la resta realizada
    """
    if dia < 1 or mes < 1 or dias_restar < 0:
        raise Exception("Parametros invalidos")
    dia_f = dia - dias_restar
    mes_f = mes
    anno_f = anno
    while dia_f <= 0:
        mes_f -= 1
        if mes_f == 0:
            mes_f = 12
            anno_f -= 1
        if mes_f == 2 and es_bisiesto(anno_f):
            dias_sumar = 29
        else:
            dias_sumar = __meses[mes_f]
        dia_f += dias_sumar
    return dia_f, mes_f, anno_f


def sumar_dias_fecha(dia, mes, anno, dias_sumar):
    """
    Suma x dias a la fecha pasada como paametro
    :param dia: int
    :param mes: int
    :param anno: int
    :param dias_sumar: int
    :return: dia, mes, anno con la suma realizada
    """
    if dia < 1 or mes < 1 or dias_sumar < 0:
        raise Exception("Parametros invalidos")
    dia_f = dia + dias_sumar
    mes_f = mes
    anno_f = anno
    while dia_f > __meses[mes_f] or (es_bisiesto(anno_f) and mes_f == 2 and dia_f > 29):
        if mes_f == 2 and es_bisiesto(anno_f):
            dia_f -= 29
        else:
            dia_f -= __meses[mes_f]
        mes_f += 1
        if mes_f == 13:
            mes_f = 1
            anno_f += 1

    return dia_f, mes_f, anno_f
