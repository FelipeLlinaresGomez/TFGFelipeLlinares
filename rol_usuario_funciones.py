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

opciones_tramos = [
    "Mañana", "Tarde", "Noche"
]

opciones_meses = [
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

def generar_opciones_dropdown(df):
    #Crear dropdowns
    opciones_tramos = [
        "Mañana", "Tarde", "Noche"
    ]

    tramos = [ {"label": k, "value": k} for k in opciones_tramos]

    opciones_meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    meses = [ {"label": k, "value": k} for k in opciones_meses]

    anios_data = df['Año'].apply(lambda x: x.strip())
    anios_data_ordenados = anios_data[anios_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_anios = anios_data_ordenados.values

    anios = [ {"label": k, "value": k} for k in opciones_dropdown_anios]

    distritos_data = df[df['Distrito'] != "No informado"]
    distritos_data_grouped = distritos_data.groupby(['Distrito']).size().reset_index(name='Count')
    distritos_data_grouped = distritos_data_grouped[distritos_data_grouped['Count'] > 50]
    opciones_dropdown_distritos =distritos_data_grouped['Distrito']

    distritos = [ {"label": k, "value": k} for k in opciones_dropdown_distritos]

    tipos_data = df['Tipos'].apply(lambda x: x.strip())
    tipos_data = tipos_data[tipos_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_tipos = tipos_data.values

    tipos = [ {"label": k, "value": k} for k in opciones_dropdown_tipos]

    modus_data = df['Modus_operandi'].apply(lambda x: x.strip())
    modus_data = modus_data[modus_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_modus = modus_data.values

    modus = [ {"label": k, "value": k} for k in opciones_dropdown_modus]

    calificacion_data = df['Calificacion'].apply(lambda x: x.strip())
    calificacion_data = calificacion_data[calificacion_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_calificacion = calificacion_data.values

    calificaciones = [ {"label": k, "value": k} for k in opciones_dropdown_calificacion]

    return anios, meses, tramos, distritos, tipos, modus, calificaciones

def generar_figuras(df, dropdownTramo, dropdownMes, dropdownAnio, dropdownTipo, dropdownModus, dropdownCalificacion, dropdownDistrito):
    try:
        todaInformacion = df

        if todaInformacion is None or todaInformacion.size <= 0:
            tile_layer = dl.TileLayer(url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", id="tile-layer")
            layer_group = dl.LayerGroup([], id="layer-group")
            return [tile_layer,layer_group], html.Div([]), html.Div([]), html.Div([]),html.Div([]), "No se disponen datos suficientes para mostrar", ""
    
        if dropdownTramo is not None and len(dropdownTramo) > 0:
            todaInformacion = todaInformacion[todaInformacion["Tramo_horario"].isin(dropdownTramo)].copy()

        anioSeleccionado = False
        if dropdownAnio is not None and len(dropdownAnio) > 0:
            todaInformacion = todaInformacion[todaInformacion["Año"].isin(dropdownAnio)].copy()
            anioSeleccionado = True
        
        mesSeleccionado = False
        if dropdownMes is not None and len(dropdownMes) > 0:
            indices = [str(opciones_meses.index(mes) + 1) for mes in dropdownMes]
            todaInformacion = todaInformacion[todaInformacion['Mes'].isin(indices)].copy()
            mesSeleccionado = True

        if dropdownTipo is not None and len(dropdownTipo) > 0:
            todaInformacion = todaInformacion[todaInformacion["Tipos"].isin(dropdownTipo)].copy()

        if dropdownModus is not None and len(dropdownModus) > 0:
            todaInformacion = todaInformacion[todaInformacion["Modus_operandi"].isin(dropdownModus)].copy()

        if dropdownCalificacion is not None and len(dropdownCalificacion) > 0:
            todaInformacion = todaInformacion[todaInformacion["Calificacion"].isin(dropdownCalificacion)].copy()

        if dropdownDistrito is not None and len(dropdownDistrito) > 0:
            todaInformacion = todaInformacion[todaInformacion["Distrito"].isin(dropdownDistrito)].copy()

        if todaInformacion is not None and len(todaInformacion) > 0:
            #Fig1
            fig1 = create_graph_1(todaInformacion, mesSeleccionado, anioSeleccionado)

            #Fig2
            fig2 = create_graph_2(todaInformacion, mesSeleccionado, anioSeleccionado)

            #Fig3
            data_calificacion = todaInformacion.groupby(['Calificacion']).size().reset_index(name='Count')
            fig3 = px.bar(data_calificacion, x='Calificacion', y='Count', labels={'Calificacion': 'Calificacion', 'Count': 'Número de hechos'}, title="Hechos por calificación")
            
            #Fig 4
            fig4 = create_graph_4(todaInformacion, mesSeleccionado, anioSeleccionado)

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
        return [tile_layer,layer_group], html.Div([]), html.Div([]), html.Div([]), html.Div([]), ["Ha habido un error generando las gráficas", html.Br(), "Inténtelo de nuevo"], ""

def create_graph_1(df, mesSeleccionado, anioSeleccionado):
    if not anioSeleccionado and not mesSeleccionado:
        df['Año'] = df['Año'].astype(int)
        all_years = pd.DataFrame({'Año': range(int(df['Año'].min()), int(df['Año'].max() + 1))})
        merged_data = all_years.merge(df.groupby(['Año']).size().reset_index(name='Count'), how='left').fillna(0)
        fig1 = px.line(merged_data , x='Año', y='Count', labels={'Año': 'Año', 'Count': 'Número de Hechos'}, title="Tendencia anual")
    
    elif anioSeleccionado and not mesSeleccionado:
        df['Mes'] = df['Mes'].astype(int)
        all_meses = pd.DataFrame({'Mes': range(1, 13)})
        meses_data = all_meses.merge(df.groupby(['Mes', 'Tramo_horario']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Tramo_horario'] != 0]).sort_values(by='Mes')
        fig1 = px.line(meses_data , x='Mes', y='Count', color = "Tramo_horario", labels={'Mes': 'Mes', 'Count': 'Número de Hechos', 'Tramo_horario': 'Tramo horario'}, title= f"Tendencia mensual por tramo horario")
    
    elif anioSeleccionado and mesSeleccionado:
        df['Dia'] = df['Dia'].astype(int)

        all_Dias = pd.DataFrame({'Dia': range(1, 32)})

        meses_data = all_Dias.merge(df.groupby(['Dia', 'Tramo_horario']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = meses_data[meses_data['Tramo_horario'] != 0]

        fig1 = px.line(meses_data , x='Dia', y='Count',  color='Tramo_horario', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Tramo_horario': 'Tramo horario'}, title= f"Tendencia diaria por tramo horario")
    
    elif not anioSeleccionado and mesSeleccionado:
        df['Año'] = df['Año'].astype(int)

        all_years = pd.DataFrame({'Año': range(df['Año'].min(), df['Año'].max() + 1)})
        grouped = df.groupby(['Año', 'Tramo_horario']).size().reset_index(name='Count')
        grouped = all_years.merge(grouped, on=['Año'], how='left').fillna(0)
        grouped = (grouped[grouped['Tramo_horario'] != 0]).sort_values(by='Año')
        fig1 = px.line(grouped , x='Año', y='Count', color='Tramo_horario', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Tramo_horario': 'Tramo horario'}, title= f"Tendencia anual por tramo horario")
    
    return fig1 

def create_graph_2(df, mesSeleccionado, anioSeleccionado):
    if not anioSeleccionado and not mesSeleccionado:
        df['Año'] = df['Año'].astype(int)
        all_years = pd.DataFrame({'Año': range(int(df['Año'].min()), int(df['Año'].max() + 1))})
        merged_data = all_years.merge(df.groupby(['Año', "Distrito"]).size().reset_index(name='Count'), how='left').fillna(0)
        merged_data = (merged_data[merged_data['Distrito'] != 0])
        merged_data = (merged_data[merged_data['Count'] > 20]).sort_values(by='Año')
        fig2 = px.line(merged_data , x='Año', y='Count', color='Distrito', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title="Tendencia anual por distrito")
    
    elif anioSeleccionado and not mesSeleccionado:
        df['Mes'] = df['Mes'].astype(int)
        all_meses = pd.DataFrame({'Mes': range(1, 13)})
        meses_data = all_meses.merge(df.groupby(['Mes', 'Distrito']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Distrito'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 10]).sort_values(by='Mes')
        fig2 = px.line(meses_data , x='Mes', y='Count', color = "Distrito", labels={'Mes': 'Mes', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title= f"Tendencia mensual por distrito")
    
    elif anioSeleccionado and mesSeleccionado:
        df['Dia'] = df['Dia'].astype(int)
        all_Dias = pd.DataFrame({'Dia': range(1, 32)})

        meses_data = all_Dias.merge(df.groupby(['Dia', 'Distrito']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Distrito'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 5]).sort_values(by='Dia')

        fig2 = px.line(meses_data , x='Dia', y='Count',  color='Distrito', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title= f"Tendencia diaria por distrito")
    
    elif not anioSeleccionado and mesSeleccionado:
        df['Año'] = df['Año'].astype(int)

        all_years = pd.DataFrame({'Año': range(df['Año'].min(), df['Año'].max() + 1)})
        grouped = df.groupby(['Año', 'Distrito']).size().reset_index(name='Count')
        grouped = all_years.merge(grouped, on=['Año'], how='left').fillna(0)
       
        grouped = (grouped[grouped['Distrito'] != 0])
        grouped = (grouped[grouped['Count'] > 20]).sort_values(by='Año')
       
        fig2 = px.line(grouped , x='Año', y='Count', color='Distrito', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Distrito': 'Distrito'}, title= f"Tendencia anual por distrito")
    
    return fig2

def create_graph_4(df, mesSeleccionado, anioSeleccionado):
    if not anioSeleccionado and not mesSeleccionado:
        df['Año'] = df['Año'].astype(int)
        all_years = pd.DataFrame({'Año': range(int(df['Año'].min()), int(df['Año'].max() + 1))})
        merged_data = all_years.merge(df.groupby(['Año', "Modus_operandi"]).size().reset_index(name='Count'), how='left').fillna(0)
        merged_data = (merged_data[merged_data['Modus_operandi'] != 0])
        merged_data = (merged_data[merged_data['Count'] > 20]).sort_values(by='Año')
        fig4 = px.line(merged_data , x='Año', y='Count', color='Modus_operandi', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title="Tendencia anual por modus operandi")
    
    elif anioSeleccionado and not mesSeleccionado:
        df['Mes'] = df['Mes'].astype(int)
        all_meses = pd.DataFrame({'Mes': range(1, 13)})
        meses_data = all_meses.merge(df.groupby(['Mes', 'Modus_operandi']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Modus_operandi'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 10]).sort_values(by='Mes')
        fig4 = px.line(meses_data , x='Mes', y='Count', color = "Modus_operandi", labels={'Mes': 'Mes', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title= f"Tendencia mensual por modus operandi")
    
    elif anioSeleccionado and mesSeleccionado:
        df['Dia'] = df['Dia'].astype(int)
        all_Dias = pd.DataFrame({'Dia': range(1, 32)})

        meses_data = all_Dias.merge(df.groupby(['Dia', 'Modus_operandi']).size().reset_index(name='Count'), how='left').fillna(0)
        meses_data = (meses_data[meses_data['Modus_operandi'] != 0])
        meses_data = (meses_data[meses_data['Count'] > 5]).sort_values(by='Dia')

        fig4 = px.line(meses_data , x='Dia', y='Count',  color='Modus_operandi', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title= f"Tendencia diaria por modus operandi")
    
    elif not anioSeleccionado and mesSeleccionado:
        df['Año'] = df['Año'].astype(int)

        all_years = pd.DataFrame({'Año': range(df['Año'].min(), df['Año'].max() + 1)})
        grouped = df.groupby(['Año', 'Modus_operandi']).size().reset_index(name='Count')
        grouped = all_years.merge(grouped, on=['Año'], how='left').fillna(0)
       
        grouped = (grouped[grouped['Modus_operandi'] != 0])
        grouped = (grouped[grouped['Count'] > 20]).sort_values(by='Año')
       
        fig4 = px.line(grouped , x='Año', y='Count', color='Modus_operandi', labels={'Año': 'Año', 'Count': 'Número de Hechos', 'Modus_operandi': 'Modus operandi'}, title= f"Tendencia anual por modus operandi")
    
    return fig4

def generar_informe_pdf(todaInformacion, n_clicks, dropdownTramo, dropdownMes, dropdownAnio, dropdownTipo, dropdownModus, dropdownCalificacion, dropdownDistrito):
    try:
        # Generate the PDF report and save it to a file
        if dropdownTramo is not None and len(dropdownTramo) > 0:
            todaInformacion = todaInformacion[todaInformacion["Tramo_horario"].isin(dropdownTramo)].copy()

        anioSeleccionado = False
        if dropdownAnio is not None and len(dropdownAnio) > 0:
            todaInformacion = todaInformacion[todaInformacion["Año"].isin(dropdownAnio)].copy()
            anioSeleccionado = True
        
        mesSeleccionado = False
        if dropdownMes is not None and len(dropdownMes) > 0:
            indices = [str(opciones_meses.index(mes) + 1) for mes in dropdownMes]
            todaInformacion = todaInformacion[todaInformacion['Mes'].isin(indices)].copy()
            mesSeleccionado = True

        if dropdownTipo is not None and len(dropdownTipo) > 0:
            todaInformacion = todaInformacion[todaInformacion["Tipos"].isin(dropdownTipo)].copy()

        if dropdownModus is not None and len(dropdownModus) > 0:
            todaInformacion = todaInformacion[todaInformacion["Modus_operandi"].isin(dropdownModus)].copy()

        if dropdownCalificacion is not None and len(dropdownCalificacion) > 0:
            todaInformacion = todaInformacion[todaInformacion["Calificacion"].isin(dropdownCalificacion)].copy()

        if dropdownDistrito is not None and len(dropdownDistrito) > 0:
            todaInformacion = todaInformacion[todaInformacion["Distrito"].isin(dropdownDistrito)].copy()

        if todaInformacion is not None and len(todaInformacion) > 0:
            #Fig1
            fig1 = create_graph_1(todaInformacion,mesSeleccionado, anioSeleccionado)
            image1 = create_png_from_figura(fig1,'1')
            
            #Fig2
            fig2 = create_graph_2(todaInformacion, mesSeleccionado, anioSeleccionado)
            image2 = create_png_from_figura(fig2,'2')

            #Fig3
            data_calificacion = todaInformacion.groupby(['Calificacion']).size().reset_index(name='Count')
            fig3 = px.bar(data_calificacion, x='Calificacion', y='Count', labels={'Calificacion': 'Calificacion', 'Count': 'Número de hechos'}, title="Hechos por calificación ")
            image3 = create_png_from_figura(fig3,'3')

            #Fig 4
            fig4 = create_graph_4(todaInformacion, mesSeleccionado, anioSeleccionado)
            image4 = create_png_from_figura(fig4,'4')

            report_filename = f"Pdfs/Informe_plataforma_delitos_malaga_Felipe_Llinares_{n_clicks}.pdf"
            pdf_canvas = canvas.Canvas(report_filename, pagesize=letter)

            center_x = pdf_canvas._pagesize[0] / 2
            todos = "Todos"
            image_uma_path = "Imagenes/UniversidadMalaga.jpg"
            image_etsi_path = "Imagenes/ETSIInformatica.jpg"
            
            #Header - Footer
            pdf_canvas.drawImage(image_uma_path, 50, 715, 204, 70)
            pdf_canvas.drawImage(image_etsi_path, pdf_canvas._pagesize[0]- 50 -204, 720, 204, 60)
            pdf_canvas.setFont("Helvetica", 14)
            pdf_canvas.drawString(320, 15, "Realizado por: FELIPE LLINARES GÓMEZ")

            #Titulo
            pdf_canvas.setFont("Helvetica-Bold", 20)
            pdf_canvas.drawCentredString(center_x, 670, "VISUALIZACIÓN DE DELITOS EN MÁLAGA")

            pdf_canvas.setFont("Helvetica-BoldOblique", 16)
            pdf_canvas.drawString(50, 630, "Filtros aplicados:")
            
            #Filtros
            pdf_canvas.setFont("Helvetica", 14)
            altura = 605
            
            años = ", ".join([str(anio) for anio in dropdownAnio]) if (dropdownAnio is not None and len(dropdownAnio) > 0) else todos
            start = 0
            while start < len(años):
                if start == 0:
                    pdf_canvas.drawString(50, altura, f"Años: {años[start:start+70]}")
                else:
                    pdf_canvas.drawString(50, altura, años[start:start+70])
                    if (start+70 >= len(años)):
                        altura = altura - 5
                start += 70
                altura = altura - 20
                

            meses = ", ".join([mes for mes in dropdownMes]) if (dropdownMes is not None and len(dropdownMes) > 0) else todos
            start = 0
            while start < len(meses):
                if start == 0:
                    pdf_canvas.drawString(50, altura, f"Meses: {meses[start:start+70]}")
                else:
                    pdf_canvas.drawString(50, altura, meses[start:start+70])
                    if (start+70 >= len(meses)):
                        altura = altura - 5
                start += 70
                altura = altura - 20
            
            tramos = ", ".join([tramo for tramo in dropdownTramo]) if (dropdownTramo is not None and len(dropdownTramo) > 0) else todos
            start = 0
            while start < len(tramos):
                if start == 0:
                    pdf_canvas.drawString(50, altura, f"Tramos horarios: {tramos[start:start+70]}")
                else:
                    pdf_canvas.drawString(50, altura, tramos[start:start+70])
                    if (start+70 >= len(tramos)):
                        altura = altura - 5
                start += 70
                altura = altura - 20
            
            distritos = ", ".join([distrito for distrito in dropdownDistrito]) if (dropdownDistrito is not None and len(dropdownDistrito) > 0) else todos
            start = 0
            while start < len(distritos):
                if start == 0:
                    pdf_canvas.drawString(50, altura, f"Distritos: {distritos[start:start+50]}")
                else:
                    pdf_canvas.drawString(50, altura, distritos[start:start+50])
                    if (start+50 >= len(distritos)):
                        altura = altura - 5
                start += 50
                altura = altura - 20

            tipos = ", ".join([tipologia for tipologia in dropdownTipo]) if (dropdownTipo is not None and len(dropdownTipo) > 0) else todos
            start = 0
            while start < len(tipos):
                if start == 0:
                    pdf_canvas.drawString(50, altura, f"Tipologías: {tipos[start:start+50]}")
                else:
                    pdf_canvas.drawString(50, altura, tipos[start:start+50])
                    if (start+50 >= len(tipos)):
                        altura = altura - 5
                start += 50
                altura = altura - 20

            modus = ", ".join([modus for modus in dropdownModus]) if (dropdownModus is not None and len(dropdownModus) > 0) else todos
            start = 0
            while start < len(modus):
                if start == 0:
                    pdf_canvas.drawString(50, altura, f"Modus operandis: {modus[start:start+70]}")
                else:
                    pdf_canvas.drawString(50, altura, modus[start:start+70])
                    if (start+70 >= len(modus)):
                        altura = altura - 5
                start += 70
                altura = altura - 20

            calificaciones = ", ".join([calificacion for calificacion in dropdownCalificacion]) if (dropdownCalificacion is not None and len(dropdownCalificacion) > 0) else todos
            start = 0
            while start < len(calificaciones):
                if start == 0:
                    pdf_canvas.drawString(50, altura, f"Calificaciones: {calificaciones[start:start+70]}")
                else:
                    pdf_canvas.drawString(50, altura, calificaciones[start:start+70])
                    if (start+70 >= len(calificaciones)):
                        altura = altura - 5
                start += 70
                altura = altura - 20

            pdf_canvas.setFont("Helvetica-Bold", 14)
            pdf_canvas.drawString(50, altura, f"Número de delitos: {len(todaInformacion)}")

            #Graficas
            #Si tenemos hueco para pintar la grafica 1 en la primera pantalla lo hacemos y metemos las otras 3 en la 2
            print(altura)
            if (altura > 406):
                pdf_canvas.drawImage(image1, 50, 40, 512, 366)

                #Cambiamos a la siguiente página
                pdf_canvas.showPage()

                #Header - Footer
                pdf_canvas.drawImage(image_uma_path, 50, 715, 204, 70)
                pdf_canvas.drawImage(image_etsi_path, pdf_canvas._pagesize[0]- 50 -204, 720, 204, 60)
                pdf_canvas.setFont("Helvetica", 14)
                pdf_canvas.drawString(320, 15, "Realizado por: FELIPE LLINARES GÓMEZ")

                pdf_canvas.drawImage(image2, 106, 480, 400, 220)
                pdf_canvas.drawImage(image3, 106, 260 , 400, 220)
                pdf_canvas.drawImage(image4, 106, 40 , 400, 220)

            else:
                #Si no tenemos hueco para la grafica en la primera pantalla, hacemos 1 y 2 en la pagina 2 y 3 y 4 en la pagina 3
                #Cambiamos a la siguiente página
                pdf_canvas.showPage()

                #Header - Footer
                pdf_canvas.drawImage(image_uma_path, 50, 715, 204, 70)
                pdf_canvas.drawImage(image_etsi_path, pdf_canvas._pagesize[0]- 50 -204, 720, 204, 60)
                pdf_canvas.setFont("Helvetica", 14)
                pdf_canvas.drawString(320, 15, "Realizado por: FELIPE LLINARES GÓMEZ")

                pdf_canvas.drawImage(image1, 90, 340, 420, 300)
                pdf_canvas.drawImage(image2, 90, 40, 420, 300)
                
                #Cambiamos a la siguiente página
                pdf_canvas.showPage()

                #Header - Footer
                pdf_canvas.drawImage(image_uma_path, 50, 715, 204, 70)
                pdf_canvas.drawImage(image_etsi_path, pdf_canvas._pagesize[0]- 50 -204, 720, 204, 60)
                pdf_canvas.setFont("Helvetica", 14)
                pdf_canvas.drawString(320, 15, "Realizado por: FELIPE LLINARES GÓMEZ")

                pdf_canvas.drawImage(image3, 90, 340 , 420, 300)
                pdf_canvas.drawImage(image4, 90, 40 , 420, 300)
            
            pdf_canvas.save()
            
            return f"Informe {n_clicks} guardado con éxito en la carpeta del proyecto"
        
        else:
            return "Debe de disponer de datos para poder generar el informe"
         
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