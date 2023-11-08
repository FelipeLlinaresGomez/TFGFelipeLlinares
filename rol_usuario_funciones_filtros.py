from config.db import mydb
import pandas as pd
from datetime import datetime

def obtener_filtros_usuario(username):
    cursor = mydb.cursor()

    #Create select query and execute
    select_query = "SELECT Nombre, Fecha_creacion, Años, Meses, Tramos_horarios, Distritos, Tipologias, Modus, Calificaciones from combinacion_filtros where Usuario = %s;"
    cursor.execute(select_query, username)
    result_rows = cursor.fetchall()

    if result_rows is not None:
        dataframe_filtros = pd.DataFrame(result_rows, columns=["Nombre", "Fecha creación", "Años", "Meses", "Tramos horarios", "Distritos", "Tipologias", "Modus", "Calificaciones" ])
        dataframe_filtros["Fecha creación"] = dataframe_filtros["Fecha creación"].dt.strftime("%H:%M %d-%m-%y")
    else:
        dataframe_filtros = pd.DataFrame(columns=["Nombre", "Fecha creación", "Años", "Meses", "Tramos horarios", "Distritos", "Tipologias", "Modus", "Calificaciones" ])

    mydb.commit()
    cursor.close()

    return dataframe_filtros

def obtener_nombres_filtros_usuario(username):
    cursor = mydb.cursor()

    #Create select query and execute
    select_query = "SELECT Nombre from combinacion_filtros where Usuario = %s;"
    cursor.execute(select_query, username)
    result_rows = cursor.fetchall()

    result_rows = [str(row[0]) for row in result_rows]

    mydb.commit()
    cursor.close()

    return result_rows

def obtener_valores_guardados_filtro(username, nombre):
    cursor = mydb.cursor()

    select_query = "SELECT Años, Meses, Tramos_horarios, Distritos, Tipologias, Modus, Calificaciones from combinacion_filtros where Usuario = %s and Nombre = %s;"
    cursor.execute(select_query, [username, nombre])
    result_rows = cursor.fetchone()

    if result_rows is not None:
        result_list = [string_to_list(value) for value in result_rows]
    else:
        result_list = []

    mydb.commit()
    cursor.close()

    return result_list

def borrar_filtros(username, nombres):
    cursor = mydb.cursor()

    placeholders = ', '.join(['%s' for _ in nombres])
    delete_filtros_query = f"""
    DELETE FROM combinacion_filtros
    WHERE combinacion_filtros.Nombre IN ({placeholders})
    AND combinacion_filtros.Usuario = %s
    """
    delete_filtros_values = nombres + [username]
    
    cursor.execute(delete_filtros_query, delete_filtros_values)

    mydb.commit()

def crear_filtro(username, nombre, dropdownTramo, dropdownMes, dropdownAnio, dropdownTipo, dropdownModus, dropdownCalificacion, dropdownDistrito):
    cursor = mydb.cursor()
    
    tramos = ", ".join(dropdownTramo) if dropdownTramo is not None else None
    meses =  ", ".join(dropdownMes) if dropdownMes is not None else None
    años =  ", ".join(dropdownAnio) if dropdownAnio is not None else None
    tipos =  ", ".join(dropdownTipo) if dropdownTipo is not None else None
    modus = ", ".join(dropdownModus) if dropdownModus is not None else None
    calificaciones = ", ".join(dropdownCalificacion) if dropdownCalificacion is not None else None
    distritos = ", ".join(dropdownDistrito) if dropdownDistrito is not None else None
    fecha_creacion = datetime.now()

    insert_filtro = "INSERT combinacion_filtros(Usuario, Nombre, Fecha_creacion, Años, Meses, Tramos_horarios, Distritos, Tipologias, Modus, Calificaciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    values_filtro = (username, nombre, fecha_creacion, años, meses, tramos, distritos, tipos, modus, calificaciones)

    cursor.execute(insert_filtro, values_filtro)

    mydb.commit()
    cursor.close()

def string_to_list(string_with_commas):
    if string_with_commas is None:
        return []
    else:
        # Split the string by commas and strip any leading/trailing whitespace
        result_list = [value.strip() for value in string_with_commas.split(',')]
        
        return result_list