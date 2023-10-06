from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from festividades_utils.utils import es_bisiesto
from natsort import natsorted
from dash import html
import traceback
import pandas as pd
import plotly.express as px
import plotly.io as pio
from dash import dcc
from config.db import mydb
import dash_leaflet as dl

opciones_dropdown_tramos = [
    "Mañana", "Tarde", "Noche"
]

opciones_dropdown_meses = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

def crear_dataframe():
    cursor = mydb.cursor()

    #Create select query and execute
    select_query = "SELECT * from hecho inner join fecha ON hecho.Fecha = fecha.idFecha inner join lugar ON hecho.Lugar = lugar.idLugar WHERE fecha.Dia <> 'No informado';"
    cursor.execute(select_query)
    result_rows = cursor.fetchall()

    df = pd.DataFrame(result_rows, columns=[desc[0] for desc in cursor.description])

    # Close the connection
    mydb.commit()
    cursor.close()

    return df

def generar_figuras(df, dropdownTramo, dropdownMes, dropdownAnio, dropdownTipo, dropdownModus, dropdownCalificacion, dropdownDistrito):
    try:
        todaInformacion = df

        if dropdownTramo is not None:
            todaInformacion = todaInformacion[todaInformacion["Tramo_horario"] == dropdownTramo]

        if dropdownAnio is not None:
            todaInformacion = todaInformacion[todaInformacion["Año"] == int(dropdownAnio)]
            tituloAño = dropdownAnio
        else:
            tituloAño = ""
        
        indexDropdownMes = None
        if dropdownMes is not None:
            indexDropdownMes = opciones_dropdown_meses.index(dropdownMes)
            todaInformacion = todaInformacion[todaInformacion['Mes'] == str(indexDropdownMes + 1)]
            tituloMes = "en " + dropdownMes 
        else:
            tituloMes = ""

        if dropdownTipo is not None:
            todaInformacion = todaInformacion[todaInformacion["Tipos"] == dropdownTipo]

        if dropdownModus is not None:
            todaInformacion = todaInformacion[todaInformacion["Modus_operandi"] == dropdownModus]

        if dropdownCalificacion is not None:
            todaInformacion = todaInformacion[todaInformacion["Calificacion"] == dropdownCalificacion]

        if dropdownDistrito is not None:
            todaInformacion = todaInformacion[todaInformacion["Distrito"] == dropdownDistrito]

        #Fig1
        #src = "https://umalaga.maps.arcgis.com/apps/instant/basic/index.html?appid=dff95ce7c4d54b5a9bfd90bba82045d9&level=10&extent=36.73931208030581,-4.463859509979803,36.70333080013165,-4.354425385110552"
        #fig1 = html.Iframe(src=src, width="100%", height="400px")

        if todaInformacion.size > 0:
            #Fig1
            fig1 = create_graph_1(todaInformacion, indexDropdownMes, dropdownAnio)

            #Fig2
            fig2 = create_graph_2(todaInformacion, indexDropdownMes, dropdownAnio)

            #Fig3
            data_calificacion = todaInformacion.groupby(['Calificacion']).size().reset_index(name='Count')
            fig3 = px.bar(data_calificacion, x='Calificacion', y='Count', labels={'Calificacion': 'Calificacion', 'Count': 'Número de hechos'}, title="Hechos por calificación " + tituloMes + " " + tituloAño)
            
            #Fig 4
            fig4 = create_graph_4(todaInformacion, indexDropdownMes, dropdownAnio)

            filtered_coordinates_df = todaInformacion[(todaInformacion['LAT'] != 'No informado') & (todaInformacion['LON'] != 'No informado')]

            if dropdownMes is not None and dropdownAnio is not None:
                markers = [dl.Marker(
                                position=[row["LAT"], row["LON"]], 
                                children=[dl.Tooltip(content = f"Fecha: {row['Dia']}/{row['Mes']}/{row['Año']} <br> Tipología: {row['Tipos']} <br> Calificacion: {row['Calificacion']} <br> Modus operandi: {row['Modus_operandi']}")]) 
                                for i, row in filtered_coordinates_df.iterrows()]
                
                tile_layer = dl.TileLayer(url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", id="tile-layer")
                layer_group = dl.LayerGroup(markers, id="layer-group")
            
                return [tile_layer,layer_group], dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), dcc.Graph(figure=fig3), dcc.Graph(figure=fig4),  "", ""
            else:
                tile_layer = dl.TileLayer(url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", id="tile-layer")
                layer_group = dl.LayerGroup([], id="layer-group")
                return [tile_layer,layer_group], dcc.Graph(figure=fig1), dcc.Graph(figure=fig2), dcc.Graph(figure=fig3), dcc.Graph(figure=fig4), "", "Filtre por año y mes para visualizar la geolocalización"
        else:
            tile_layer = dl.TileLayer(url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", id="tile-layer")
            layer_group = dl.LayerGroup([], id="layer-group")
            return [tile_layer,layer_group], html.Div([]), html.Div([]), html.Div([]),html.Div([]), "No se dispone de datos para esta combinación de filtros", ""
        
    except Exception as e:
        print(e)
        traceback.print_exc()
        tile_layer = dl.TileLayer(url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", id="tile-layer")
        layer_group = dl.LayerGroup([], id="layer-group")
        return [tile_layer,layer_group], html.Div([]), html.Div([]), html.Div([]), html.Div([]), ["Ha habido un error procesando los archivos", html.Br(), "Inténtelo de nuevo"], ""

def create_graph_1(df, dropdownMes, dropdownAnio):
    if dropdownAnio is None and dropdownMes is None:
        df['Año'] = df['Año'].astype(int)
        all_years = pd.DataFrame({'Año': range(int(df['Año'].min()), int(df['Año'].max() + 1))})
        merged_data = all_years.merge(df.groupby(['Año']).size().reset_index(name='Count'), how='left').fillna(0)
        fig1 = px.line(merged_data , x='Año', y='Count', labels={'Año': 'Año', 'Count': 'Número de Hechos'}, title="Tendencia anual")
    
    elif dropdownAnio is not None and dropdownMes is None:
        df['Mes'] = df['Mes'].astype(int)
        all_meses = pd.DataFrame({'Mes': range(1, 13)})
        meses_data = all_meses.merge(df.groupby(['Mes', 'Tramo_horario']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Tramo_horario'] != 0]).sort_values(by='Mes')
        fig1 = px.line(meses_data , x='Mes', y='Count', color = "Tramo_horario", labels={'Mes': 'Mes', 'Count': 'Número de Hechos', 'Tramo_horario': 'Tramo horario'}, title= f"Tendencia mensual en {dropdownAnio} por tramo horario")
    
    elif dropdownAnio is not None and dropdownMes is not None:
        df['Dia'] = df['Dia'].astype(int)

        numero_dias_mes = get_number_of_days(dropdownMes + 1, es_bisiesto(int(dropdownAnio)))
        all_Dias = pd.DataFrame({'Dia': range(1, numero_dias_mes+1)})

        meses_data = all_Dias.merge(df.groupby(['Dia', 'Tramo_horario']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = meses_data[meses_data['Tramo_horario'] != 0]

        fig1 = px.line(meses_data , x='Dia', y='Count',  color='Tramo_horario', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Tramo_horario': 'Tramo horario'}, title= f"Tendencia diaria en {opciones_dropdown_meses[dropdownMes]} de {dropdownAnio} por tramo horario")
    
    elif dropdownAnio is None and dropdownMes is not None:
        df['Año'] = df['Año'].astype(int)

        all_years = pd.DataFrame({'Año': range(df['Año'].min(), df['Año'].max() + 1)})
        grouped = df.groupby(['Año', 'Tramo_horario']).size().reset_index(name='Count')
        grouped = all_years.merge(grouped, on=['Año'], how='left').fillna(0)
        grouped = (grouped[grouped['Tramo_horario'] != 0]).sort_values(by='Año')
        fig1 = px.line(grouped , x='Año', y='Count', color='Tramo_horario', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Tramo_horario': 'Tramo horario'}, title= f"Tendencia anual de {opciones_dropdown_meses[dropdownMes]} por tramo horario")
    
    return fig1 

def create_graph_2(df, dropdownMes, dropdownAnio):
    if dropdownAnio is None and dropdownMes is None:
        df['Año'] = df['Año'].astype(int)
        all_years = pd.DataFrame({'Año': range(int(df['Año'].min()), int(df['Año'].max() + 1))})
        merged_data = all_years.merge(df.groupby(['Año', "Distrito"]).size().reset_index(name='Count'), how='left').fillna(0)
        merged_data = (merged_data[merged_data['Distrito'] != 0])
        merged_data = (merged_data[merged_data['Count'] > 20]).sort_values(by='Año')
        fig2 = px.line(merged_data , x='Año', y='Count', color='Distrito', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title="Tendencia anual por distrito")
    
    elif dropdownAnio is not None and dropdownMes is None:
        df['Mes'] = df['Mes'].astype(int)
        all_meses = pd.DataFrame({'Mes': range(1, 13)})
        meses_data = all_meses.merge(df.groupby(['Mes', 'Distrito']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Distrito'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 10]).sort_values(by='Mes')
        fig2 = px.line(meses_data , x='Mes', y='Count', color = "Distrito", labels={'Mes': 'Mes', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title= f"Tendencia mensual en {dropdownAnio} por distrito")
    
    elif dropdownAnio is not None and dropdownMes is not None:
        df['Dia'] = df['Dia'].astype(int)

        numero_dias_mes = get_number_of_days(dropdownMes + 1, es_bisiesto(int(dropdownAnio)))
        all_Dias = pd.DataFrame({'Dia': range(1, numero_dias_mes+1)})

        meses_data = all_Dias.merge(df.groupby(['Dia', 'Distrito']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Distrito'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 5]).sort_values(by='Dia')

        fig2 = px.line(meses_data , x='Dia', y='Count',  color='Distrito', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title= f"Tendencia diaria en {opciones_dropdown_meses[dropdownMes]} de {dropdownAnio} por distrito")
    
    elif dropdownAnio is None and dropdownMes is not None:
        df['Año'] = df['Año'].astype(int)

        all_years = pd.DataFrame({'Año': range(df['Año'].min(), df['Año'].max() + 1)})
        grouped = df.groupby(['Año', 'Distrito']).size().reset_index(name='Count')
        grouped = all_years.merge(grouped, on=['Año'], how='left').fillna(0)
       
        grouped = (grouped[grouped['Distrito'] != 0])
        grouped = (grouped[grouped['Count'] > 20]).sort_values(by='Año')
       
        fig2 = px.line(grouped , x='Año', y='Count', color='Distrito', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title= f"Tendencia anual de {opciones_dropdown_meses[dropdownMes]} por distrito")
    
    return fig2

def create_graph_4(df, dropdownMes, dropdownAnio):
    if dropdownAnio is None and dropdownMes is None:
        df['Año'] = df['Año'].astype(int)
        all_years = pd.DataFrame({'Año': range(int(df['Año'].min()), int(df['Año'].max() + 1))})
        merged_data = all_years.merge(df.groupby(['Año', "Modus_operandi"]).size().reset_index(name='Count'), how='left').fillna(0)
        merged_data = (merged_data[merged_data['Modus_operandi'] != 0])
        merged_data = (merged_data[merged_data['Count'] > 20]).sort_values(by='Año')
        fig4 = px.line(merged_data , x='Año', y='Count', color='Modus_operandi', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title="Tendencia anual por modus operandi")
    
    elif dropdownAnio is not None and dropdownMes is None:
        df['Mes'] = df['Mes'].astype(int)
        all_meses = pd.DataFrame({'Mes': range(1, 13)})
        meses_data = all_meses.merge(df.groupby(['Mes', 'Modus_operandi']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Modus_operandi'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 10]).sort_values(by='Mes')
        fig4 = px.line(meses_data , x='Mes', y='Count', color = "Modus_operandi", labels={'Mes': 'Mes', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title= f"Tendencia mensual en {dropdownAnio} por modus operandi")
    
    elif dropdownAnio is not None and dropdownMes is not None:
        df['Dia'] = df['Dia'].astype(int)

        numero_dias_mes = get_number_of_days(dropdownMes + 1, es_bisiesto(int(dropdownAnio)))
        all_Dias = pd.DataFrame({'Dia': range(1, numero_dias_mes+1)})

        meses_data = all_Dias.merge(df.groupby(['Dia', 'Modus_operandi']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Modus_operandi'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 5]).sort_values(by='Dia')

        fig4 = px.line(meses_data , x='Dia', y='Count',  color='Modus_operandi', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title= f"Tendencia diaria en {opciones_dropdown_meses[dropdownMes]} de {dropdownAnio} por modus operandi")
    
    elif dropdownAnio is None and dropdownMes is not None:
        df['Año'] = df['Año'].astype(int)

        all_years = pd.DataFrame({'Año': range(df['Año'].min(), df['Año'].max() + 1)})
        grouped = df.groupby(['Año', 'Modus_operandi']).size().reset_index(name='Count')
        grouped = all_years.merge(grouped, on=['Año'], how='left').fillna(0)
       
        grouped = (grouped[grouped['Modus_operandi'] != 0])
        grouped = (grouped[grouped['Count'] > 20]).sort_values(by='Año')
       
        fig4 = px.line(grouped , x='Año', y='Count', color='Modus_operandi', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title= f"Tendencia anual de {opciones_dropdown_meses[dropdownMes]} por modus operandi")
    
    return fig4

def generar_informe_pdf(todaInformacion, n_clicks, dropdownTramo, dropdownMes, dropdownAnio, dropdownTipo, dropdownModus, dropdownCalificacion, dropdownDistrito):
    try:
        # Generate the PDF report and save it to a file
        if dropdownTramo is not None:
            todaInformacion = todaInformacion[todaInformacion["Tramo_horario"] == dropdownTramo]

        if dropdownAnio is not None:
            todaInformacion = todaInformacion[todaInformacion["Año"] == int(dropdownAnio)]
            tituloAño = dropdownAnio
        else:
            tituloAño = ""
        
        indexDropdownMes = None
        if dropdownMes is not None:
            indexDropdownMes = opciones_dropdown_meses.index(dropdownMes)
            todaInformacion = todaInformacion[todaInformacion['Mes'] == str(indexDropdownMes + 1)]
            tituloMes = "en " + dropdownMes 
        else:
            tituloMes = ""

        if dropdownTipo is not None:
            todaInformacion = todaInformacion[todaInformacion["Tipos"] == dropdownTipo]

        if dropdownModus is not None:
            todaInformacion = todaInformacion[todaInformacion["Modus_operandi"] == dropdownModus]

        if dropdownCalificacion is not None:
            todaInformacion = todaInformacion[todaInformacion["Calificacion"] == dropdownCalificacion]

        if dropdownDistrito is not None:
            todaInformacion = todaInformacion[todaInformacion["Distrito"] == dropdownDistrito]

        report_filename = f"Pdfs/Informe_plataforma_delitos_malaga_Felipe_Llinares_{n_clicks}.pdf"
        
        pdf_canvas = canvas.Canvas(report_filename, pagesize=letter)

        center_x = pdf_canvas._pagesize[0] / 2
        todos = "Todos"
        image_uma_path = "Imagenes/UniversidadMalaga.jpg"
        image_etsi_path = "Imagenes/ETSIInformatica.jpg"

        pdf_canvas.drawImage(image_uma_path, 50, 715, 204, 70)
        pdf_canvas.drawImage(image_etsi_path, pdf_canvas._pagesize[0]- 50 -204, 720, 204, 60)

        pdf_canvas.setFont("Helvetica-Bold", 20)
        pdf_canvas.drawCentredString(center_x, 670, "VISUALIZACIÓN DE DELITOS EN MÁLAGA")

        pdf_canvas.setFont("Helvetica-BoldOblique", 16)
        pdf_canvas.drawString(50, 620, "Filtros aplicados:")

        pdf_canvas.setFont("Helvetica", 14)
        pdf_canvas.drawString(50, 595, f"Año: {dropdownAnio if dropdownAnio is not None else todos }")
        pdf_canvas.drawString(50, 575, f"Mes: {dropdownMes if dropdownMes is not None else todos }")
        pdf_canvas.drawString(50, 555, f"Tramo horario: {dropdownTramo if dropdownTramo is not None else todos }")
        
        pdf_canvas.drawString(50, 535, f"Distrito: {dropdownDistrito if dropdownDistrito is not None else todos }")
        
        tipologia = dropdownTipo if dropdownTipo is not None else todos 
        tipologia = tipologia[:50]  + "..." if len(tipologia) > 49 else tipologia 
        pdf_canvas.drawString(50, 515, f"Tipología: {tipologia}")

        pdf_canvas.drawString(50, 495, f"Modus operandi: {dropdownModus if dropdownModus is not None else todos }")
        pdf_canvas.drawString(50, 475, f"Calificación: {dropdownCalificacion if dropdownCalificacion is not None else todos }")
        
        pdf_canvas.setFont("Helvetica-Bold", 14)
        pdf_canvas.drawString(50, 440, f"Número de delitos: {len(todaInformacion)}")

        #Fig1
        fig1 = create_graph_1(todaInformacion, indexDropdownMes, dropdownAnio)
        image1 = create_png_from_figura(fig1,'1')
        pdf_canvas.drawImage(image1, 50, 60, 512, 366)

        pdf_canvas.setFont("Helvetica", 14)
        pdf_canvas.drawString(320, 20, "Realizado por: FELIPE LLINARES GÓMEZ")
        
        
        #Cambiamos a la siguiente página
        pdf_canvas.showPage()

        #Fig2
        fig2 = create_graph_2(todaInformacion, indexDropdownMes, dropdownAnio)
        image2 = create_png_from_figura(fig2,'2')

        #Fig3
        data_calificacion = todaInformacion.groupby(['Calificacion']).size().reset_index(name='Count')
        fig3 = px.bar(data_calificacion, x='Calificacion', y='Count', labels={'Calificacion': 'Calificacion', 'Count': 'Número de hechos'}, title="Hechos por calificación " + tituloMes + " " + tituloAño)
        image3 = create_png_from_figura(fig3,'3')

        #Fig 4
        fig4 = create_graph_4(todaInformacion, indexDropdownMes, dropdownAnio)
        image4 = create_png_from_figura(fig4,'4')

        pdf_canvas.drawImage(image_uma_path, 50, 715, 204, 70)
        pdf_canvas.drawImage(image_etsi_path, pdf_canvas._pagesize[0]- 50 -204, 720, 204, 60)

        pdf_canvas.drawImage(image2, 106, 480, 400, 220)
        pdf_canvas.drawImage(image3, 106, 260 , 400, 220)
        pdf_canvas.drawImage(image4, 106, 40 , 400, 220)

        pdf_canvas.setFont("Helvetica", 14)
        pdf_canvas.drawString(320, 20, "Realizado por: FELIPE LLINARES GÓMEZ")

        pdf_canvas.save()
        
        return f"Informe {n_clicks} guardado con éxito en la carpeta del proyecto"
    except Exception as e:
        print(e)
        traceback.print_exc()
        return ["Ha habido un error generando el informe",  html.Br(), "Inténtelo de nuevo más tarde"]
    
def create_png_from_figura(fig, numero):
    image__path = "Figuras/figura" + numero + ".png"
    img = pio.to_image(fig, format = "png", engine='kaleido')
    with open(image__path, "wb") as img_file:
        img_file.write(img)

    return image__path
    
def get_number_of_days(month, bisiesto):
    if month == 2 and bisiesto:
        return 29
    elif month == 2:
        return 28
    elif month in [4, 6, 9, 11]:
        return 30
    else:
        return 31