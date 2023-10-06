import base64
import pandas as pd
import numpy as np
from io import StringIO
from festividades_utils.festividades import get_festividad
from config.db import mydb
import aiohttp
import asyncio
import traceback

API_KEY = 'Aj943_sLvTzpse2YFv4FZSC13eoEU4djhgLF5Qdq0CcSVpomrm15eZad759fjYQu'
BASE_URL = "http://dev.virtualearth.net/REST/v1/Locations"

#Cabeceras
FECHA_DESDE = '[$AC01 Fecha Desde Hecho].[Dia Desde Hecho]'


def insert_data(contents):
    listdenuncias = np.zeros(len(contents))
    for i in range(len(contents)):
        cursor = mydb.cursor()
        denuncias_agregadas = 0

        try:
            decoded = base64.b64decode(contents[i].split(",")[1]).decode("utf-8")
            decoded = decoded.replace(';',',')

            df = pd.read_csv(StringIO(decoded),on_bad_lines='skip')
            df = df.fillna('No informado')
            df = df.reset_index(drop=True)  # reset index to ensure continuous memory allocation
        
            print(df)

            try:
                df.loc[:, 'Fecha_desde'] = pd.to_datetime(df['[$AC01 Fecha Desde Hecho].[Dia Desde Hecho]'],format='%d %B %Y')
                df.loc[:, 'Dia_desde'] = df['Fecha_desde'].apply(lambda x: x.strftime('%Y-%m-%d'))
                df.loc[:, 'Dia_semana'] = df['Fecha_desde'].apply(lambda x: x.strftime('%A'))
                df.loc[:, 'Dia'] = df['Fecha_desde'].dt.day
                df.loc[:, 'Mes'] = df['Fecha_desde'].dt.month
                df.loc[:, 'Año'] = df['Fecha_desde'].dt.year
            except Exception:
                df.loc[:, 'Dia_desde'] = "No informado"

                df.loc[:, 'Dia_semana'] = "Desconocido"
                df.loc[:, 'Dia'] = "No informado"
                df.loc[:, 'Mes'] = "No informado"
                df.loc[:, 'Año'] = "No informado"
            
            try:
                df['Address'] = f"{df['[$AC02 Lugar Hecho Via].[Lugar Hecho Tipo Via]']} {df['[$AC02 Lugar Hecho Via].[Lugar Hechos Via]']}, {df['[$AC02 Lugar Hecho].[Municipio Hecho]']}, {df['[$AC02 Lugar Hecho].[Provincia Hecho]']}"
                
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

            tipo_via = row['[$AC02 Lugar Hecho Via].[Lugar Hecho Tipo Via]']
            via = row['[$AC02 Lugar Hecho Via].[Lugar Hechos Via]']
            municipio = row['[$AC02 Lugar Hecho].[Municipio Hecho]']
            provincia = row['[$AC02 Lugar Hecho].[Provincia Hecho]']

            address = f"{tipo_via} {via}, {municipio}, {provincia}"
            tasks.append(geocode_address_bing_async(session, address))
        geocoded_results = await asyncio.gather(*tasks)
        return geocoded_results

def insert_fecha(row, cursor):                                                                                                  
    Dia = row['Dia']
    Mes = row['Mes']
    Año = row['Año']

    select_query = "SELECT idFecha from fecha WHERE fecha.Dia = %s and fecha.Mes = %s and fecha.Año = %s;"
    values_query = (str(Dia), str(Mes), str(Año))
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()
    
    if result:
        return result
    else:
        Dia_semana = row['Dia_semana']
        if type(Dia) == int and type(Mes) == int and type(Año) == int :
            Festividad_fecha_general, Festividad_fecha_concreta = get_festividad(Dia, Mes, Año)
        else:
            Festividad_fecha_general = Festividad_fecha_concreta = "No informado"

        insert_fecha = "INSERT IGNORE INTO fecha(Dia_semana, Dia, Mes, Año, Festividad_fecha_general, Festividad_fecha_concreta) VALUES (%s, %s, %s, %s, %s, %s);"
        values_fecha = (Dia_semana, Dia, Mes, Año, Festividad_fecha_general, Festividad_fecha_concreta)
        cursor.execute(insert_fecha, values_fecha)

        return cursor.lastrowid

def insert_lugar(row, cursor):
    Provincia = row['[$AC02 Lugar Hecho].[Provincia Hecho]'] if '[$AC02 Lugar Hecho].[Provincia Hecho]' in row.index else 'No informado'
    Municipio = row['[$AC02 Lugar Hecho].[Municipio Hecho]'] if '[$AC02 Lugar Hecho].[Municipio Hecho]' in row.index else 'No informado'
    Tipo_via = row['[$AC02 Lugar Hecho Via].[Lugar Hecho Tipo Via]'] if '[$AC02 Lugar Hecho Via].[Lugar Hecho Tipo Via]' in row.index else 'No informado'
    Via = row['[$AC02 Lugar Hecho Via].[Lugar Hechos Via]'] if '[$AC02 Lugar Hecho Via].[Lugar Hechos Via]' in row.index else 'No informado'

    select_query = "SELECT idLugar from lugar WHERE lugar.Tipo_via = %s and lugar.Via = %s and lugar.Municipio = %s and lugar.Provincia = %s;"
    values_query = (Tipo_via, Via, Municipio, Provincia)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    if result:
        return result
    else:
        if Municipio.replace(" ", "").lower() == "malaga":
            Continente = row['[$AC02 Lugar Hecho Pais].[Continente Hecho]'] if '[$AC02 Lugar Hecho Pais].[Continente Hecho]' in row.index else 'No informado'
            Pais = row['[$AC02 Lugar Hecho Pais].[Pais Hecho]'] if '[$AC02 Lugar Hecho Pais].[Pais Hecho]' in row.index else 'No informado'
            Jefatura = row['[$AC02 Lugar Hecho].[Jefatura Hecho]'] if '[$AC02 Lugar Hecho].[Jefatura Hecho]' in row.index else 'No informado'
            Distrito = row['[$AC02 Lugar Hecho Distrito].[Lugar Hecho Distrito]'] if '[$AC02 Lugar Hecho Distrito].[Lugar Hecho Distrito]' in row.index else 'No informado'
            Lat = row['Lat']
            Lon = row['Lon']
            
            insert_lugar = "INSERT IGNORE INTO lugar(Continente, Pais, Jefatura, Provincia, Municipio, Distrito, Tipo_via, Via, LAT, LON) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            values_lugar = (Continente, Pais, Jefatura, Provincia, Municipio, Distrito, Tipo_via, Via, Lat, Lon)
            cursor.execute(insert_lugar, values_lugar)
            return cursor.lastrowid
        else:
            return -1

def insert_responsable(row, cursor):
    DNI_responsable = row['[$BC01 Identificacion Responsable].[Numero Documento Responsable]'] if '[$BC01 Identificacion Responsable].[Numero Documento Responsable]' in row.index else ""
    
    select_query = "SELECT Dni from responsable WHERE responsable.Dni = %s;"
    values_query = (DNI_responsable)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    if result:
        return result
    else:
        if DNI_responsable != "" and DNI_responsable.strip().lower() != 'no informado' and DNI_responsable.strip().lower() != 'indocumentado desconocido' and DNI_responsable.strip().lower() != 'no asociado':
            Pais_responsable = row['[$BC05 Pais Residencia Responsable].[Paises Residencia Responsable]'] if '[$BC05 Pais Residencia Responsable].[Paises Residencia Responsable]' in row.index else ""
            Edad_responsable = row['[$BC03 Edad Responsable].[Edades Responsable]'] if '[$BC03 Edad Responsable].[Edades Responsable]' in row.index else ""
            Sexo_responsable = row['[$BC02 Sexo Responsale].[Sexo Responsable]'] if '[$BC02 Sexo Responsale].[Sexo Responsable]' in row.index else ""
            Municipio_responsable = row['[$BC05 Lugar Residencia Responsable].[Municipio Residencia Responsable]'] if '[$BC05 Lugar Residencia Responsable].[Municipio Residencia Responsable]' in row.index else ""
            Nacionalidad_responsable = row['[$BC04 Nacionalidad Actual Responsable].[Nacionalidad Actual Responsable]'] if '[$BC04 Nacionalidad Actual Responsable].[Nacionalidad Actual Responsable]' in row.index else ""
            Extranjeria_responsable = row['[$BC14 Situacion Extranjero EspaÃ±a Responsable].[Situacion Extranjero EspaÃ±a Responsable]'] if '[$BC14 Situacion Extranjero EspaÃ±a Responsable].[Situacion Extranjero EspaÃ±a Responsable]' in row.index else ""
            Entrada_extranjero_responsable = row['[$BB08 Medio Utilizado Entrada Ilegal Responsable].[Medio Utilizado Entrada Ilegal Responsable]'] if '[$BB08 Medio Utilizado Entrada Ilegal Responsable].[Medio Utilizado Entrada Ilegal Responsable]' in row.index else ""
            Detenciones_responsable = row['[$BC13 Numero Detenciones Responsable].[Numero Detenciones Responsable]'] if '[$BC13 Numero Detenciones Responsable].[Numero Detenciones Responsable]' in row.index else ""
            insert_responsable = "INSERT IGNORE INTO responsable(Dni, Pais, Edad, Sexo, Municipio, Nacionalidad, Extranjeria, Entrada_extranjero, Detenciones) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"
            values_responsable = (DNI_responsable, Pais_responsable, Edad_responsable, Sexo_responsable, Municipio_responsable, Nacionalidad_responsable, Extranjeria_responsable, Entrada_extranjero_responsable, Detenciones_responsable)
            cursor.execute(insert_responsable, values_responsable)

            return cursor.lastrowid
        else:
            return -1
    
def insert_responsable_hecho(dniResponsable, Identificador_denuncia, cursor):
    if dniResponsable != -1:
        insert_responsable_hecho = "INSERT IGNORE INTO responsableshechos(identificador_denuncia, id_responsable) VALUES (%s, %s);"
        values_responsable_hecho = (Identificador_denuncia, dniResponsable)
        cursor.execute(insert_responsable_hecho, values_responsable_hecho)

def insert_plantilla_actuacion(row, cursor):
    Cod_plantilla_actuacion = row['[$AA03 Plantilla Actuacion].[Unidad Cod]'] if '[$AA03 Plantilla Actuacion].[Unidad Cod]' in row.index else 'No informado'
    
    select_query = "SELECT idPlantillaActuacion from plantilla_actuacion WHERE plantilla_actuacion.Cod = %s;"
    values_query = (Cod_plantilla_actuacion)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    if result:
        return result
    else:
        Unidad_plantilla_actuacion = row['[$AA03 Plantilla Actuacion].[Unidad Actuacion]'] if '[$AA03 Plantilla Actuacion].[Unidad Actuacion]' in row.index else 'No informado'
        Jefatura_plantilla_actuacion = row['[$AA03 Plantilla Actuacion Lugar].[Plantilla Actuacion Jefatura]'] if '[$AA03 Plantilla Actuacion Lugar].[Plantilla Actuacion Jefatura]' in row.index else 'No informado'
        Provincia_plantilla_actuacion = row['[$AA03 Plantilla Actuacion Lugar].[Plantilla Actuacion Provincia]'] if '[$AA03 Plantilla Actuacion Lugar].[Plantilla Actuacion Provincia]' in row.index else 'No informado'
        Municipio_plantilla_actuacion = row['[$AA03 Plantilla Actuacion Lugar].[Plantilla Actuacion Municipio]'] if '[$AA03 Plantilla Actuacion Lugar].[Plantilla Actuacion Municipio]' in row.index else 'No informado'

        insert_plantilla_actuacion = f"INSERT INTO plantilla_actuacion(Cod, Unidad, Jefatura, Provincia, Municipio) VALUES  (%s, %s, %s, %s, %s);"
        values_plantilla_actuacion = (Cod_plantilla_actuacion, Unidad_plantilla_actuacion, Jefatura_plantilla_actuacion, Provincia_plantilla_actuacion, Municipio_plantilla_actuacion)
        cursor.execute(insert_plantilla_actuacion, values_plantilla_actuacion)

        return cursor.lastrowid

def insert_actuacion(row, cursor):
    idPlantillaActuacion = insert_plantilla_actuacion(row, cursor)
    Dia = row['[$AA03 Fecha Actuacion].[Dia Actuacion]']  if '[$AA03 Fecha Actuacion].[Dia Actuacion]' in row.index else 'No informado'
    Plantillas = row['[$AA03 Plantilla Actuacion].[Plantillas Actuacion]']  if '[$AA03 Plantilla Actuacion].[Plantillas Actuacion]' in row.index else 'No informado'

    select_query = "SELECT idActuacion from actuacion WHERE actuacion.Plantilla_actuacion = %s and actuacion.Dia = %s and actuacion.Plantillas = %s;"
    values_query = (idPlantillaActuacion, Dia,Plantillas)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    if result:
        return result
    else:
        Origen = row['[$AA01 Origen Actuacion].[Origen Actuacion]']  if '[$AA01 Origen Actuacion].[Origen Actuacion]' in row.index else 'No informado'

        insert_actuacion = "INSERT INTO actuacion(Plantilla_actuacion, PLantillas, Dia, Origen) VALUES (%s, %s, %s, %s);"
        values_actuacion = (idPlantillaActuacion, Plantillas, Dia, Origen)
        cursor.execute(insert_actuacion, values_actuacion)
        return cursor.lastrowid

def insert_hecho(row, cursor):
    columna_insertada = False

    plantilla_cod = row['[$AA03 Plantilla Actuacion].[Plantilla Cod]'] if '[$AA03 Plantilla Actuacion].[Plantilla Cod]' in row.index else (row['[$AA03 Plantilla Actuacion].[Unidad Cod]'] if '[$AA03 Plantilla Actuacion].[Unidad Cod]' in row.index else None)
    num_actuacion = row['[$AA03 NumActuacion].[Numactuacion]'] if '[$AA03 NumActuacion].[Numactuacion]' in row.index else None
    
    if  num_actuacion != None and plantilla_cod != None:
        idLugar = insert_lugar(row, cursor)

        if idLugar != -1:

            idFecha = insert_fecha(row, cursor)
            idActuacion = insert_actuacion(row, cursor)
            idResponsable = insert_responsable(row, cursor)

            Grupo_tipos = row['[$AC03 Tipo Hecho].[Grupo Tipos Hecho]'] if '[$AC03 Tipo Hecho].[Grupo Tipos Hecho]' in row.index else 'No informado'
            Tipos = row['[$AC03 Tipo Hecho].[Tipos Hecho]'] if '[$AC03 Tipo Hecho].[Tipos Hecho]' in row.index else 'No informado'
            Calificacion = row['[$AC04 Calificacion Hecho].[Calificacion Hecho]'] if '[$AC04 Calificacion Hecho].[Calificacion Hecho]' in row.index else 'No informado'
            Grado_ejecucion = row['[$AC05 Grado Ejecucion Hecho].[Grado Ejecucion Hecho]'] if '[$AC05 Grado Ejecucion Hecho].[Grado Ejecucion Hecho]' in row.index else 'No informado'
            Modus_operandi = row['[$AC08 Modus Operandi Hecho].[Modus Operandi Hecho]'] if '[$AC08 Modus Operandi Hecho].[Modus Operandi Hecho]' in row.index else 'No informado'
            Relacionado_tipos = row['[$AC15 Tipo Hecho Relacionado].[Tipos Hecho]'] if '[$AC15 Tipo Hecho Relacionado].[Tipos Hecho]' in row.index else 'No informado'

            Horas = row['[$AC01 Hora Desde Hecho].[Horas Desde Hecho]'] if '[$AC01 Hora Desde Hecho].[Horas Desde Hecho]' in row.index else 'No informado'
            Tramo_horario = tramo_horario(Horas)

            General = row['[$AC11 Lugar General Hecho].[Lugar General]'] if '[$AC11 Lugar General Hecho].[Lugar General]' in row.index else 'No informado'
            Grupo_especifico = row['[$AC10 AC12 Lugar Especifico Hecho].[Grupo Lugar Especifico]'] if '[$AC10 AC12 Lugar Especifico Hecho].[Grupo Lugar Especifico]' in row.index else 'No informado'
            Especificos = row['[$AC10 AC12 Lugar Especifico Hecho].[Lugares Especificos]'] if '[$AC10 AC12 Lugar Especifico Hecho].[Lugares Especificos]' in row.index else 'No informado'
            Identificador_denuncia = str(num_actuacion) + "_" + str(plantilla_cod) + "-" + str(row['Año']) 
            
            insert_hecho = "INSERT INTO hecho(Identificador_denuncia, Actuacion, Fecha, Lugar, Grupo_tipos, Tipos, Calificacion, Grado_ejecucion, Modus_operandi, Relacionado_tipos, Tramo_horario, Lugar_general, Lugar_grupo_especifico, Lugar_especificos) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
            values_hecho = (Identificador_denuncia, idActuacion, idFecha, idLugar, Grupo_tipos, Tipos, Calificacion, Grado_ejecucion, Modus_operandi, Relacionado_tipos, Tramo_horario, General, Grupo_especifico, Especificos)
            cursor.execute(insert_hecho, values_hecho)
            if cursor.lastrowid > 0:
                columna_insertada = True
            insert_responsable_hecho(idResponsable, Identificador_denuncia, cursor)


    return columna_insertada

def tramo_horario(hora):
    try:
        hora = int(hora)
        if hora >= 0 and hora < 8:
            return 'Mañana'
        elif hora >= 8 and hora <= 16:
            return 'Tarde'
        elif hora > 16 and hora <= 24:
            return 'Noche'
        else:
            return 'No informado'
    except Exception:
        return 'No informado'