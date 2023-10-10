import base64
import pandas as pd
import numpy as np
from io import StringIO
from festividades_utils.festividades import get_festividad
from config.db import mydb
from cabeceras import *
import aiohttp
import asyncio
import traceback
import re

API_KEY = 'Aj943_sLvTzpse2YFv4FZSC13eoEU4djhgLF5Qdq0CcSVpomrm15eZad759fjYQu'
BASE_URL = "http://dev.virtualearth.net/REST/v1/Locations"

def insert_data(contents):
    listdenuncias = np.zeros(len(contents))
    for i in range(len(contents)):
        cursor = mydb.cursor()
        denuncias_agregadas = 0

        try:
            decoded = base64.b64decode(contents[i].split(",")[1]).decode("utf-8")
            decoded = decoded.replace(';',',')

            df = pd.read_csv(StringIO(decoded),on_bad_lines='skip')
            #df.fillna(value=None)
            # Iterate over columns and rows to replace NaN values with None
            for col in df.columns:
                for idx, value in enumerate(df[col]):
                    if pd.isna(value):
                        df.at[idx, col] = None

            df = df.reset_index(drop=True)  # reset index to ensure continuous memory allocation
            
            patternDolarNumeros = r'(\$?\w+\d+|\$\w+)'
            patternEspacios = r'(?<=\[)\s+'

            # Use regex to replace column names
            df.columns = [re.sub(patternEspacios, '', re.sub(patternDolarNumeros, '', column_name)) for column_name in df.columns]
          
            try:
                df.loc[:, 'Fecha_desde'] = pd.to_datetime(df[FECHA_DESDE],format='%d %B %Y')
                df.loc[:, 'Dia_desde'] = df['Fecha_desde'].apply(lambda x: x.strftime('%Y-%m-%d'))
                df.loc[:, 'Dia_semana'] = df['Fecha_desde'].apply(lambda x: x.strftime('%A'))
                df.loc[:, 'Dia'] = df['Fecha_desde'].dt.day
                df.loc[:, 'Mes'] = df['Fecha_desde'].dt.month
                df.loc[:, 'Año'] = df['Fecha_desde'].dt.year
            except Exception:
                df.loc[:, 'Dia_desde'] = None
                df.loc[:, 'Dia_semana'] = None
                df.loc[:, 'Dia'] = None
                df.loc[:, 'Mes'] = None
                df.loc[:, 'Año'] = None
            
            try:
                geocoded_results = asyncio.run(geocode_dataframe_addresses(df))

                df['Lat'] = [lat for lat,lon in geocoded_results]
                df['Lon'] = [lon for lat,lon in geocoded_results]
            except Exception:
                df['Lat'] = None
                df['Lon'] = None
                traceback.print_exc()
            
            denuncia_correcta = False
            for index, row in df.iterrows():
                denuncia_correcta = insert_hecho(row, cursor)
                if denuncia_correcta:
                    denuncias_agregadas = denuncias_agregadas + 1
            
        except Exception:
            traceback.print_exc()

        listdenuncias[i] = (denuncias_agregadas)

        mydb.commit()
        cursor.close()

    return listdenuncias

async def geocode_address_bing_async(session, address):
    try:
        params = {
            "q": address,
            "key": API_KEY
        }
        async with session.get(BASE_URL, params=params) as response:
            data = await response.json()

            if data.get('resourceSets') and data['resourceSets'][0].get('resources'):
                resource = data['resourceSets'][0]['resources'][0]
                coordinates = resource['point']['coordinates']
                return coordinates[0], coordinates[1]
            else:
                return "No informado", "No informado"
    except Exception as e:
        print(f"Error geocoding address: {e}")
        return "No informado", "No informado"

async def geocode_dataframe_addresses(df):
    async with aiohttp.ClientSession() as session:
        tasks = []
        for index, row in df.iterrows():

            tipo_via = row[LUGAR_HECHO_TIPO_VIA]
            via = row[LUGAR_HECHO_VIA]
            municipio = row[LUGAR_HECHO_MUNICIPIO]
            provincia = row[LUGAR_HECHO_PROVINCIA]

            address = f"{tipo_via} {via}, {municipio}, {provincia}"
            tasks.append(geocode_address_bing_async(session, address))
        geocoded_results = await asyncio.gather(*tasks)
        return geocoded_results

def insert_lugar(row, cursor):
    Tipo_via = row[LUGAR_HECHO_TIPO_VIA] if LUGAR_HECHO_TIPO_VIA in row.index else None
    Via = row[LUGAR_HECHO_VIA] if LUGAR_HECHO_VIA in row.index else None
    Municipio = row[LUGAR_HECHO_MUNICIPIO] if LUGAR_HECHO_MUNICIPIO in row.index else None
    Provincia = row[LUGAR_HECHO_PROVINCIA] if LUGAR_HECHO_PROVINCIA in row.index else None

    #Si no existe uno de los campos, devuelvo None 
    if Tipo_via is None or Via is None or Municipio is None or Provincia is None:
        return None
    
    select_query = "SELECT idLugar from lugar WHERE lugar.Tipo_via = %s and lugar.Via = %s and lugar.Municipio = %s and lugar.Provincia = %s;"
    values_query = (Tipo_via, Via, Municipio, Provincia)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    if result:
        #Si ya existia el lugar devuelvo el id
        return result
    else:
        if Municipio.replace(" ", "").lower() == "malaga":
            Continente = row[LUGAR_HECHO_CONTINENTE] if LUGAR_HECHO_CONTINENTE in row.index else None
            Pais = row[LUGAR_HECHO_PAIS] if LUGAR_HECHO_PAIS in row.index else None
            Jefatura = row[LUGAR_HECHO_JEFATURA] if LUGAR_HECHO_JEFATURA in row.index else None
            Distrito = row[LUGAR_HECHO_DISTRITO] if LUGAR_HECHO_DISTRITO in row.index else None
            Lat = row['Lat']
            Lon = row['Lon']
            
            insert_lugar = "INSERT INTO lugar(Continente, Pais, Jefatura, Provincia, Municipio, Distrito, Tipo_via, Via, LAT, LON) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            values_lugar = (Continente, Pais, Jefatura, Provincia, Municipio, Distrito, Tipo_via, Via, Lat, Lon)

            try:
                #Si todo va bien devuelvo el id generado al insertar
                cursor.execute(insert_lugar, values_lugar)
                return cursor.lastrowid
            except Exception as e:
                #Si algo va mal devuelvo None
                print(e)
                traceback.print_exc()
                return None
        else:
            #Si el municipio no es Málaga devuelvo -1 para no introducir nada
            return -1

def insert_fecha(row, cursor):                                                                                                  
    Dia = row['Dia']
    Mes = row['Mes']
    Año = row['Año']

    #Si no existe uno de los campos, devuelvo None 
    if Dia is None or Mes is None or Año is None:
        return None

    select_query = "SELECT idFecha from fecha WHERE fecha.Dia = %s and fecha.Mes = %s and fecha.Año = %s;"
    values_query = (str(Dia), str(Mes), str(Año))
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()
    
    if result:
        #Si ya existia la fecha devuelvo el id
        return result
    else:
        Dia_semana = row['Dia_semana']
        if type(Dia) == int and type(Mes) == int and type(Año) == int :
            Festividad_fecha_general, Festividad_fecha_concreta = get_festividad(Dia, Mes, Año)
        else:
            Festividad_fecha_general = Festividad_fecha_concreta = None

        insert_fecha = "INSERT INTO fecha(Dia_semana, Dia, Mes, Año, Festividad_fecha_general, Festividad_fecha_concreta) VALUES (%s, %s, %s, %s, %s, %s);"
        values_fecha = (Dia_semana, Dia, Mes, Año, Festividad_fecha_general, Festividad_fecha_concreta)

        try:
            #Si todo va bien devuelvo el id generado al insertar
            cursor.execute(insert_fecha, values_fecha)
            return cursor.lastrowid
        except Exception as e:
            #Si algo va mal devuelvo None
            print(e)
            traceback.print_exc()
            return None
       
def insert_plantilla_actuacion(row, cursor):
    Cod_plantilla_actuacion = row[PLANTILLA_ACTUACION_PLANTILLA_COD] if PLANTILLA_ACTUACION_PLANTILLA_COD in row.index else (row[PLANTILLA_ACTUACION_UNIDAD_COD] if PLANTILLA_ACTUACION_UNIDAD_COD in row.index else None)
    
    select_query = "SELECT idPlantillaActuacion from plantilla_actuacion WHERE plantilla_actuacion.Cod = %s;"
    values_query = (Cod_plantilla_actuacion)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    if result:
        #Si ya existia la plantilla devuelvo el id
        return result
    else:
        Unidad_plantilla_actuacion = row[PLANTILLA_ACTUACION_ACTUACION] if PLANTILLA_ACTUACION_ACTUACION in row.index else None
        Jefatura_plantilla_actuacion = row[PLANTILLA_ACTUACION_JEFATURA] if PLANTILLA_ACTUACION_JEFATURA in row.index else None
        Provincia_plantilla_actuacion = row[PLANTILLA_ACTUACION_PROVINCIA] if PLANTILLA_ACTUACION_PROVINCIA in row.index else None
        Municipio_plantilla_actuacion = row[PLANTILLA_ACTUACION_MUNICIPIO] if PLANTILLA_ACTUACION_MUNICIPIO in row.index else None

        insert_plantilla_actuacion = f"INSERT INTO plantilla_actuacion(Cod, Unidad, Jefatura, Provincia, Municipio) VALUES  (%s, %s, %s, %s, %s);"
        values_plantilla_actuacion = (Cod_plantilla_actuacion, Unidad_plantilla_actuacion, Jefatura_plantilla_actuacion, Provincia_plantilla_actuacion, Municipio_plantilla_actuacion)
        
        try:
            #Si todo va bien devuelvo el id generado al insertar
            cursor.execute(insert_plantilla_actuacion, values_plantilla_actuacion)
            return cursor.lastrowid
        except Exception as e:
            #Si algo va mal devuelvo None
            print(e)
            traceback.print_exc()
            return None
        
def insert_actuacion(row, cursor):
    idPlantillaActuacion = insert_plantilla_actuacion(row, cursor)

    #Si la plantilla no existe, devuelvo None  
    if idPlantillaActuacion is None:
        return None
    
    Dia = row[ACTUACION_DIA] if ACTUACION_DIA in row.index else None
    Plantillas = row[ACTUACION_PLANTILLAS] if ACTUACION_PLANTILLAS in row.index else None

    select_query = "SELECT idActuacion from actuacion WHERE actuacion.Plantilla_actuacion = %s and actuacion.Dia = %s and actuacion.Plantillas = %s;"
    values_query = (idPlantillaActuacion, Dia,Plantillas)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    if result:
        #Si ya existia la actuacion devuelvo el id
        return result
    else:
        Origen = row[ACTUACION_ORIGEN] if ACTUACION_ORIGEN in row.index else None

        insert_actuacion = "INSERT INTO actuacion(Plantilla_actuacion, PLantillas, Dia, Origen) VALUES (%s, %s, %s, %s);"
        values_actuacion = (idPlantillaActuacion, Plantillas, Dia, Origen)

        try:
            #Si todo va bien devuelvo el id generado al insertar     
            cursor.execute(insert_actuacion, values_actuacion)
            return cursor.lastrowid
        except Exception as e:
            #Si algo va mal devuelvo None
            print(e)
            traceback.print_exc()
            return None

def insert_responsable(row, cursor):
    DNI_responsable = str(row[RESPONSABLE_DNI]) if RESPONSABLE_DNI in row.index else None

    if DNI_responsable is None or DNI_responsable is 'nan':
        #Si la columna no está o es nan
        return None
    
    DNI_responsable_copia = str(DNI_responsable).strip().lower()
    if DNI_responsable_copia != "" and DNI_responsable_copia != 'no informado' and DNI_responsable_copia != 'indocumentado desconocido' and DNI_responsable_copia != 'no asociado':
        #Si el dni es no informado, no asociado o indocumentado desconocido devuelvo None
        return None
    
    try:
        select_query = "SELECT Dni from responsable WHERE responsable.Dni = %s;"
        values_query = (DNI_responsable)
        cursor.execute(select_query, values_query)
        result = cursor.fetchone()
    except Exception as e:
        #Si algo va mal devuelvo None
        print(e)
        traceback.print_exc()
        result = None

    if result:
        #Si ya existia el responsable devuelvo el dni
        return result
    else:
        edad = None
        try:
            if (RESPONSABLE_EDAD in row.index):
                edad = int( row[RESPONSABLE_EDAD])
        except Exception:
            edad = None

        detenciones = None
        try:
            if (RESPONSABLE_DETENCIONES in row.index):
                detenciones = int( row[RESPONSABLE_DETENCIONES])
        except Exception:
            detenciones = None

        Edad_responsable = edad
        Sexo_responsable = row[RESPONSABLE_SEXO] if RESPONSABLE_SEXO in row.index else None
        Pais_responsable = row[RESPONSABLE_PAIS] if RESPONSABLE_PAIS in row.index else None
        Municipio_responsable = row[RESPONSABLE_MUNICIPIO] if RESPONSABLE_MUNICIPIO in row.index else None
        Nacionalidad_responsable = row[RESPONSABLE_NACIONALIDAD] if RESPONSABLE_NACIONALIDAD in row.index else None
        Extranjeria_responsable = row[RESPONSABLE_EXTRANJERIA] if RESPONSABLE_EXTRANJERIA in row.index else None
        Entrada_extranjero_responsable = row[RESPONSABLE_ENTRADA_EXTRANJERO] if RESPONSABLE_ENTRADA_EXTRANJERO in row.index else None
        Detenciones_responsable = detenciones
        insert_responsable = "INSERT INTO responsable(Dni, Pais, Edad, Sexo, Municipio, Nacionalidad, Extranjeria, Entrada_extranjero, Detenciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        values_responsable = (DNI_responsable, Pais_responsable, Edad_responsable, Sexo_responsable, Municipio_responsable, Nacionalidad_responsable, Extranjeria_responsable, Entrada_extranjero_responsable, Detenciones_responsable)

        try:
            #Si todo va bien devuelvo el dni insertado
            cursor.execute(insert_responsable, values_responsable)
            return DNI_responsable
        except Exception as e:
            #Si algo va mal devuelvo None
            print(e)
            traceback.print_exc()
            return None
    
def insert_responsable_hecho(dniResponsable, Identificador_denuncia, cursor):
    #Si el dni es distino de None, inserto
    if dniResponsable is not None:
        select_query = "SELECT identificador_denuncia from responsableshechos WHERE responsableshechos.identificador_denuncia = %s AND responsableshechos.id_responsable = %s;"
        values_query = (Identificador_denuncia, dniResponsable)
        cursor.execute(select_query, values_query)
        result = cursor.fetchone()

        #Si no existe la relación entre el reponsable y el hecho, se añade
        if result is None:
            insert_responsable_hecho = "INSERT INTO responsableshechos(identificador_denuncia, id_responsable) VALUES (%s, %s);"
            values_responsable_hecho = (Identificador_denuncia, dniResponsable)

            try:
                cursor.execute(insert_responsable_hecho, values_responsable_hecho)
            except Exception as e:
                print(e)
                traceback.print_exc()
       
def insert_hecho(row, cursor):
    columna_insertada = False

    plantilla_cod = row[PLANTILLA_ACTUACION_PLANTILLA_COD] if PLANTILLA_ACTUACION_PLANTILLA_COD in row.index else (row[PLANTILLA_ACTUACION_UNIDAD_COD] if PLANTILLA_ACTUACION_UNIDAD_COD in row.index else None)
    num_actuacion = row[ACTUACION_NUMERO] if ACTUACION_NUMERO in row.index else None
    
    if  num_actuacion != None and plantilla_cod != None:
        idLugar = insert_lugar(row, cursor)
        
        #Si el lugar no está en Málaga no insertamos nada
        if idLugar != -1:

            idFecha = insert_fecha(row, cursor)
            idActuacion = insert_actuacion(row, cursor)
            idResponsable = insert_responsable(row, cursor)

            Identificador_denuncia = str(num_actuacion) + "_" + str(plantilla_cod) + "-" + str(row['Año']) 

            Grupo_tipos = row[HECHO_GRUPOS_TIPO] if HECHO_GRUPOS_TIPO in row.index else None
            Tipos = row[HECHO_TIPOS] if HECHO_TIPOS in row.index else None
            Calificacion = row[HECHO_CALIFICACION] if HECHO_CALIFICACION in row.index else None
            Grado_ejecucion = row[HECHO_GRADO_EJECUCION] if HECHO_GRADO_EJECUCION in row.index else None
            Modus_operandi = row[HECHO_MODUS_OPERANDI] if HECHO_MODUS_OPERANDI in row.index else None
            Relacionado_tipos = row[HECHO_RELACIONADO_TIPOS] if HECHO_RELACIONADO_TIPOS in row.index else None

            Horas = row[HECHO_HORAS] if HECHO_HORAS in row.index else None
            Tramo_horario = tramo_horario(Horas)

            General = row[HECHO_LUGAR_GENERAL] if HECHO_LUGAR_GENERAL in row.index else None
            Grupo_especifico = row[HECHO_GRUPO_LUGAR_ESPECIFICO] if HECHO_GRUPO_LUGAR_ESPECIFICO in row.index else None
            Especificos = row[HECHO_LUGARES_ESPECIFICOS] if HECHO_LUGARES_ESPECIFICOS in row.index else None

            select_query = "SELECT Identificador_denuncia from hecho WHERE hecho.Identificador_denuncia = %s;"
            values_query = (Identificador_denuncia)
            cursor.execute(select_query, values_query)
            result = cursor.fetchone()

            if result:
                #Si ya existia el hecho con el mismo identificador, damos la columna por insertada
                columna_insertada = True
            else:
                #Si no existia el hecho con el mismo identificador, insertamos
                insert_hecho = "INSERT INTO hecho(Identificador_denuncia, Actuacion, Fecha, Lugar, Grupo_tipos, Tipos, Calificacion, Grado_ejecucion, Modus_operandi, Relacionado_tipos, Tramo_horario, Lugar_general, Lugar_grupo_especifico, Lugar_especificos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
                values_hecho = (Identificador_denuncia, idActuacion, idFecha, idLugar, Grupo_tipos, Tipos, Calificacion, Grado_ejecucion, Modus_operandi, Relacionado_tipos, Tramo_horario, General, Grupo_especifico, Especificos)
                
                try:
                    #Si todo va bien damos la columna por insertada einsertamos la relacion con el responsable si tuviera
                    cursor.execute(insert_hecho, values_hecho)
                    if cursor.lastrowid > 0:
                        columna_insertada = True
                        insert_responsable_hecho(idResponsable, Identificador_denuncia, cursor)
                except Exception as e:
                    #Si algo va mal no está la columna insertada
                    print(e)
                    traceback.print_exc()
                    columna_insertada = False
        
    return columna_insertada

def tramo_horario(hora):
    tramo_horario = 'No informado'
    try:
        if hora != None:
            hora = int(hora)
            if hora >= 0 and hora < 8:
                tramo_horario = 'Mañana'
            elif hora >= 8 and hora <= 16:
                tramo_horario = 'Tarde'
            elif hora > 16 and hora <= 24:
                tramo_horario = 'Noche'

        return tramo_horario
    except Exception:
        return 'No informado'