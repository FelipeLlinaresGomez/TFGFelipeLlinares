__festividades = {
    '14/2': 'San_Valentín',
    '6/12': 'Día_de_la_Constitución',
    '8/12': 'Día_de_la_Inmaculada',
    '23/6': 'San_Juan',
    '24/6': 'San_Juan',
    '1/5': 'Día_del_trabajador',
    '31/10': 'Halloween_Dia_de_los_muertos',
    '1/11': 'Halloween_Dia_de_los_muertos',
    '12/10': 'Día_de_la_Hispanidad',
    '8/9': 'Virgen_de_la_Victoria'
}
#
# import threading
# from pathlib import Path
#
# from antlr4 import CommonTokenStream
# from antlr4 import FileStream
# from antlr4 import ParseTreeWalker
#
# from server.importador.lector.festividades_utils.gramaticaFestividades.festividadesLexer import festividadesLexer
# from server.importador.lector.festividades_utils.gramaticaFestividades.festividadesParser import festividadesParser
# from server.importador.lector.festividades_utils.gramaticaFestividades.listenerFestividades import ListenerFestiviades
#
# __festividades = {}
# __thread = threading.Lock()
#
# def __cargar_festividades():
#     """
#     Inicia la gramatica para cargar las festividades
#     """
#     global __festividades
#     ruta = str(Path(__file__).parent)
#     input = FileStream(ruta + "\\festividades.txt", encoding='cp1252')
#     lexer = festividadesLexer(input)
#     stream = CommonTokenStream(lexer)
#     parser = festividadesParser(stream)
#     tree = parser.fichero_definition()
#
#     lector_gramtica = ListenerFestiviades()
#     walker = ParseTreeWalker()
#     walker.walk(lector_gramtica, tree)
#     __festividades = lector_gramtica.get_festividades


def get_festividad_unico_dia(dia, mes):
    """
    Te devuelve la representacion en String, si el dia y el mes pertenecen a un dia concreto almacenado.
    :param dia: int
    :param mes: int
    :return: representacion str del dia si lo es None, None si no es ninguno
    """
    #
    # if not __festividades:
    #     with __thread:
    #         if not __festividades:
    #             __cargar_festividades()
    buscar = str(dia) + '/' + str(mes)
    dia_f = __festividades.get(buscar)
    return dia_f, dia_f
