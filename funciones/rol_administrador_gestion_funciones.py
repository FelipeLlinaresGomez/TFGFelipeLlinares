import pandas as pd
import hashlib
import random
from config.db import mydb

def borrar_datos(anios):
    cursor = mydb.cursor()

    select_hecho_query = f"""
        SELECT Identificador_denuncia
        FROM hecho
        JOIN fecha ON hecho.Fecha = fecha.IdFecha
        WHERE fecha.Año IN ({', '.join(['%s' for _ in anios])})
    """
    cursor.execute(select_hecho_query, anios)
    hechos_ids = cursor.fetchall()
    if hechos_ids is not None:
        hechos_list = [item[0] for item in hechos_ids]
    else:
        hechos_list = []

    delete_responsable_hecho = f"""
        DELETE responsableshechos
        FROM responsableshechos
        WHERE responsableshechos.identificador_denuncia IN ({', '.join(['%s' for _ in hechos_list])})
    """

    delete_query = f"""
        DELETE hecho
        FROM hecho
        JOIN fecha ON hecho.Fecha = fecha.IdFecha
        WHERE fecha.Año IN ({', '.join(['%s' for _ in anios])})
    """

    cursor.execute(delete_responsable_hecho, hechos_list)
    cursor.execute(delete_query, anios)

    mydb.commit()
    cursor.close()

def obtener_años_borrar():
    cursor = mydb.cursor()

    #Create select query and execute
    select_query = "SELECT DISTINCT Año from fecha f JOIN hecho h ON f.idFecha = h.Fecha ORDER BY Año;"
    cursor.execute(select_query)
    result_rows = cursor.fetchall()

    if result_rows is not None:
        result_lists = [item[0] for item in result_rows]
    else:
        result_lists = []
    mydb.commit()
    cursor.close()

    return result_lists

def obtener_usuarios():
    cursor = mydb.cursor()

    #Create select query and execute
    select_query = "SELECT Usuario, Administrador from Usuario;"
    cursor.execute(select_query)
    result_rows = cursor.fetchall()

    if result_rows is not None:
        dataframe_usuarios = pd.DataFrame(result_rows, columns=["Usuario", "Rol"])
        dataframe_usuarios['Rol'] = dataframe_usuarios['Rol'].apply(map_rol)
    else:
        dataframe_usuarios = pd.DataFrame(columns=["Usuario", "Rol"])
    mydb.commit()
    cursor.close()

    return dataframe_usuarios

def map_rol(rol):
    if rol == 1:
        return "Administrador"
    else :
        return "Usuario"
    
def crear_usuario(username, password, administrador):
    cursor = mydb.cursor()
    
    # Generar un número aleatorio de 6 dígitos
    salt = random.randint(100000, 999999)

    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    sha256_hash.update((str(salt) + password).encode())

    # Get the hexadecimal representation of the hash
    hex_digest = sha256_hash.hexdigest()

    insert_usuario = "INSERT INTO usuario(usuario, contraseña, administrador, salt) VALUES (%s, %s, %s, %s);"
    values_usuario = (username, hex_digest, administrador, salt)
    cursor.execute(insert_usuario, values_usuario)

    mydb.commit()
    cursor.close()

def borrar_usuarios(usernames):
    cursor = mydb.cursor()

    delete_filtros = f"""
    DELETE FROM combinacion_filtros
    WHERE combinacion_filtros.Usuario IN ({', '.join(['%s' for _ in usernames])})
    """

    delete_usuario = f"""
    DELETE FROM usuario
    WHERE usuario.usuario IN ({', '.join(['%s' for _ in usernames])})
    """

    cursor.execute(delete_filtros, usernames)
    cursor.execute(delete_usuario, usernames)

    mydb.commit()
    cursor.close()