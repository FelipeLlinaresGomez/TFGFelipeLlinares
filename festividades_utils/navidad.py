def es_navidad(dia, mes):
    """
    Te devuelve si una fecha concreta es Navidad
    :param dia: int
    :param mes: int
    :return: True si es Navidad, False si no
    """
    return (dia >= 22 and mes == 12) or (mes == 1 and dia <= 6)


def devolver_navidad(dia, mes):
    """
    Te devuelve una representacion en string de si la fecha pasada como parametro es Navidad
    :param dia: int
    :param mes: int
    :return: Te devuelve Navidad, Dia concreto si es un dia concreto de la Navidad, Navidad, Navidad si no es
     ningun dia concreto y  None, None en caso de que no sea Navidad
    """
    resultado = None, None
    if es_navidad(dia, mes):
        if dia == 24:
            resultado = 'Nochebuena'
        elif dia == 25:
            resultado = 'Dia_navidad'
        elif dia == 28:
            resultado = 'Dia_de_los_inocentes'
        elif dia == 31:
            resultado = 'Nochevieja'
        elif dia == 1:
            resultado = 'Año_nuevo'
        elif dia == 5:
            resultado = 'Cabalgata'
        elif dia == 6:
            resultado = 'Dia_de_reyes'
        else:
            resultado = 'Navidad'
        resultado = 'Navidad', resultado
    return resultado
