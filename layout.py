from dash import html
import dash_leaflet as dl
import base64
from dash import dcc

def generar_layout_usuario(df):    

    #Creamos listas para desplegables
    opciones_dropdown_tramos = [
        "Mañana", "Tarde", "Noche"
    ]

    opciones_dropdown_meses = [
        "Enero", "Febrero", "Marzo", "Abril",
        "Mayo", "Junio", "Julio", "Agosto",
        "Septiembre", "Octubre", "Noviembre", "Diciembre"
    ]

    anios_data = df['Año'].apply(lambda x: x.strip())
    anios_data_ordenados = anios_data[anios_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_anios = anios_data_ordenados.values

    distritos_data = df[df['Distrito'] != "No informado"]
    distritos_data_grouped = distritos_data.groupby(['Distrito']).size().reset_index(name='Count')
    distritos_data_grouped = distritos_data_grouped[distritos_data_grouped['Count'] > 50]
    opciones_dropdown_distritos = distritos_data_grouped['Distrito']

    tipos_data = df['Tipos'].apply(lambda x: x.strip())
    tipos_data = tipos_data[tipos_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_tipos = tipos_data.values

    modus_data = df['Modus_operandi'].apply(lambda x: x.strip())
    modus_data = modus_data[modus_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_modus = modus_data.values

    calificacion_data = df['Calificacion'].apply(lambda x: x.strip())
    calificacion_data = calificacion_data[calificacion_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_calificacion = calificacion_data.values

    #Creamos mapa
    markers = []
    tile_layer = dl.TileLayer(url="https://a.tile.openstreetmap.org/{z}/{x}/{y}.png", id="tile-layer")
    layer_group = dl.LayerGroup(markers, id="layer-group")

    return html.Div(
    [
        generar_header(),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Año"),
                        dcc.Dropdown(
                            id="dropdownAnios",
                            options=[ {"label": k, "value": k} for k in opciones_dropdown_anios],
                            #value= opciones_dropdown_anios[0],
                            placeholder = "Selecciona de la lista",
                            style= {"width": "400px", "margin-left": 0, "margin-bottom": "10px"},
                        ),
                    ],
                    style={"margin-bottom": "10px", "display": "table"},
                    id="dropdown-container-anios",
                ),
                html.Div(
                    [
                        html.Label("Mes"),
                        dcc.Dropdown(
                            id="dropdownMeses",
                            options=[ {"label": k, "value": k} for k in opciones_dropdown_meses ],
                            #value= opciones_dropdown_meses[0],
                            placeholder = "Selecciona de la lista",
                            style= {"width": "400px", "margin-left": 0, "margin-bottom": "10px"},
                        ),
                    ],
                    style={"margin-bottom": "10px", "margin-left": "50px", "display": "table"},
                    id="dropdown-container-meses"
                ),
                html.Div(
                    [
                        html.Label("Tramo horario"),
                        dcc.Dropdown(
                            id="dropdownTramos",
                            options=[ {"label": k, "value": k} for k in opciones_dropdown_tramos],
                            #value= opciones_dropdown_tramos[0],
                            placeholder = "Selecciona de la lista",
                            style= {"width": "400px", "margin-left": 0, "margin-bottom": "10px"},
                        ),
                    ],
                    style={"margin-bottom": "10px", "margin-left": "50px", "display": "table"},
                    id="dropdown-container-tramo"
                ),
            ],
            className="row",
            style= {"margin-bottom": "10px", "display": "flex", "justify-content": "center", "align-items": "center"}
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Distrito"),
                        dcc.Dropdown(
                            id="dropdownDistrito",
                            options=[ {"label": k, "value": k} for k in opciones_dropdown_distritos],
                            #value= opciones_dropdown_anios[0],
                            placeholder = "Selecciona de la lista",
                            style= {"width": "300px", "margin-left": 0, "margin-bottom": "10px"},
                        ),
                    ],
                    style={"margin-bottom": "10px", "display": "table"},
                    id="dropdown-container-distrito", 
                ),
                html.Div(
                    [
                        html.Label("Tipología"),
                        dcc.Dropdown(
                            id="dropdownTipos",
                            options=[ {"label": k, "value": k} for k in opciones_dropdown_tipos],
                            #value= opciones_dropdown_tipos[0],
                            placeholder = "Selecciona de la lista",
                            style= {"width": "300px", "margin-left": 0, "margin-bottom": "10px"},
                        ),
                    ],
                    style={"margin-bottom": "10px", "margin-left": "50px", "display": "table"},
                    id="dropdown-container-tipos",
                ),
                html.Div(
                    [
                        html.Label("Modus operandi"),
                        dcc.Dropdown(
                            id="dropdownModus",
                            options=[ {"label": k, "value": k} for k in opciones_dropdown_modus ],
                            #value= opciones_dropdown_meses[0],
                            placeholder = "Selecciona de la lista",
                            style= {"width": "300px", "margin-left": 0, "margin-bottom": "10px"},
                        ),
                    ],
                    style={"margin-bottom": "10px", "margin-left": "50px", "display": "table"},
                    id="dropdown-container-modus",
                ),
                html.Div(
                    [
                        html.Label("Calificación"),
                        dcc.Dropdown(
                            id="dropdownCalificacion",
                            options=[ {"label": k, "value": k} for k in opciones_dropdown_calificacion],
                            #value= opciones_dropdown_anios[0],
                            placeholder = "Selecciona de la lista",
                            style= {"width": "300px", "margin-left": 0, "margin-bottom": "10px"},
                        ),
                    ],
                    style={"margin-bottom": "10px", "margin-left": "50px", "display": "table"},
                    id="dropdown-container-calficacion",
                ),
            ],
            className="row",
            style= {"margin-bottom": "10px", "display": "flex", "justify-content": "center", "align-items": "center"}
        ),
        html.H4(id="output-data-message", style= {"text-align": "center", "margin-bottom": "20px"}),
        html.Div(
            [
                html.Button('GENERAR INFORME', id='generar-informe-button', n_clicks=0, style={"margin": "0 auto", "display": "block", "background-color": "#002b73", "color": "#fbfbfb"}),
            ],
            className="row",
            style={"margin-bottom": "30px"}
        ),
        html.H5(id="informe-output-message", style= {"text-align": "center", "margin-bottom": "40px", "font-family": "HelveticaNeue, sans-serif"}),
        html.Div(
            [
                html.Div(id="output-data-1", className="six columns"),
                html.Div(id="output-data-2", className="six columns"),
            ],
            className="row",
            style={"margin-left": "20px", "margin-right": "20px", "margin-bottom": "40px", "display": "flex", "justify-content": "center", "align-items": "center",}
        ),
        html.Div(
            [
                html.Div(id="output-data-3", className="six columns"),
                html.Div(id="output-data-4", className="six columns"),
            ],
            className="row",
            style={"margin-left": "20px", "margin-right": "20px", "display": "flex", "justify-content": "center", "align-items": "center",}
        ),
        html.H5(id="output-data-message-mapa", style= {"text-align": "center", "font-family": "HelveticaNeue, sans-serif"}),
        html.Div(
            [
                html.Div([
                    dl.Map(children=[tile_layer, layer_group],
                        style={'width': "1200px", 'height': "700PX", "font-size": "12px"}, center=[36.72016, -4.42034], zoom=13, id="map"),
                    ], 
                    className="row",
                    style={
                        "text-align": "center",  # Center the text horizontally
                        "margin": "auto",  # Center the div horizontally
                        "margin-top": "20px",  # Add top margin
                        "margin-bottom": "80px",  # Add bottom margin
                        "margin-left": "20px",  # Add left margin
                        "margin-right": "20px",  # Add right margin
                    },
                )
            ],
            style={"display": "flex", "justify-content": "center", "align-items": "center"},
        ),
        generar_footer(),
    ],
    id='layout-usuario',
    style={"background-color": "#fbfbfb", "font-family": "HelveticaNeue, sans-serif", "display": "none"}
)

def generar_layout_administrador():
    return html.Div(
        [
            generar_header(),
            html.Div(
                html.P("¡Bienvenido! \n\n Suba todos los archivos CSV en el siguiente recuadro:", style={"margin": "0 auto", "font-size": "20px"}),
                style={"display": "flex", "justify-content": "center",  "margin-bottom": "20px"}
            ),
            html.Div(
                dcc.Upload(
                id="upload-data",
                children=html.Div([
                    "Arraste y suelte o ", 
                    html.A("Seleccione Archivos")
                ]),
                style={
                    "width": "800px",
                    "height": "60px",
                    "lineHeight": "60px",
                    "borderWidth": "1px",
                    "borderStyle": "dashed",
                    "borderRadius": "5px",
                    "textAlign": "center",
                    "margin": "0 auto",
                    "margin-bottom": "20px",
                    "font-family": "HelveticaNeue, sans-serif"
                },
                # Allow multiple files to be uploaded
                multiple=True,
                ),
                style={"display": "flex", "justify-content": "center",  "width":"100%"}
            ),
            html.Div(id="output-data-not-upload", style={"margin": "0 auto", "text-align": "center", "margin-bottom": "20px"}),
            html.Div(
                html.Button('INSERTAR ARCHIVOS SELECCIONADOS', id='submit-button', n_clicks=0, style={"margin": "0 auto",  "background-color": "#002b73", "color": "#fbfbfb"}),
                style={"display": "flex", "justify-content": "center", "margin-bottom": "20px"}
            ),
            html.Div(id="output-data-upload", style={"margin": "0 auto", "text-align": "center", "margin-bottom": "150px",}),
            generar_footer(),
        ],
        id='layout-administrador',
        style={"background-color": "#ffffff", "font-family": "HelveticaNeue, sans-serif", "display": "none"}
    )

def generar_layout_login():
    return html.Div(
    [
        generar_header(),
        html.Div(
            [
                html.Div(
                    [
                        html.Label("Usuario", style={"text-align": "left", "font-family": "HelveticaNeue, sans-serif",}),
                        dcc.Input(id="username-input", type="text", placeholder="Ingrese su usuario", style={"width": "300px", "font-family": "HelveticaNeue, sans-serif",}),
                    ],
                    style={"margin-bottom": "15px"},
                ),
                html.Div(
                    [
                        html.Label("Contraseña", style={"text-align": "left", "font-family": "HelveticaNeue, sans-serif",}),
                        dcc.Input(id="password-input", type="password", placeholder="Ingrese su contraseña", style={"width": "300px", "font-family": "HelveticaNeue, sans-serif",}),
                    ],
                    style={"margin-bottom": "30px"},
                ),
                html.Button("Iniciar Sesión", id="login-button", n_clicks=0, style={"background-color": "#002b73", "color": "#fbfbfb"}),
            ],
            className="row",
            style={"margin": "0 auto", "display": "block", "width": "300px", "text-align": "center", "margin-bottom": "150px"}
        ),
        generar_footer()
    ],
    id='layout-login',
    style={"background-color": "#fbfbfb", "font-family": "HelveticaNeue, sans-serif", "display": "block"}
    )

def generar_layout_elegir_rol():
    return html.Div(
    [
        generar_header(),
        html.Div(
            [
                html.H5("Elige con que rol desea acceder", style= {"text-align": "center", "margin-bottom": "20px", "font-family": "HelveticaNeue, sans-serif"}),
                html.Button("USUARIO", id="elegir-usuario-button", n_clicks=0, style={"width": "200px", "background-color": "#002b73", "color": "#fbfbfb", "margin-right": "10px",}),
                html.Button("ADMINISTRADOR", id="elegir-administrador-button", n_clicks=0, style={"width": "200px", "background-color": "#002b73", "color": "#fbfbfb","margin-left": "10px",}),
            ],
            className="row",
            style={"margin": "0 auto", "display": "block", "width": "500px", "text-align": "center", "margin-bottom": "150px", "margin-top": "150px"}
        ),
        generar_footer()
    ],
    id='layout-elegir-rol',
    style={"background-color": "#fbfbfb", "font-family": "HelveticaNeue, sans-serif", "display": "none"}
    )

def generar_header():
    return html.Div(
        children=[
            html.H3("VISUALIZACIÓN DE DELITOS EN MÁLAGA", style= {"text-align": "center", "padding-top":"30px", "padding-bottom": "15px", "color":"#fbfbfb"}),
        ],
        className="row",
        style={"background-color": "#002b73", "margin-bottom": "40px"}
    )

def generar_footer():
    with open('Imagenes/UniversidadMalaga.jpg', 'rb') as f:
        logo_uma = base64.b64encode(f.read()).decode()

    with open('Imagenes/ETSIInformatica.jpg', 'rb') as f:
        logo_etsi = base64.b64encode(f.read()).decode()


    return  html.Div(
        children=[
            html.Div(className="row", style={"background-color": "#002b73", "height": "1px"}),
            html.Div(
                [
                    html.Img(src='data:image/jpg;base64,{}'.format(logo_uma), width="150px", height="50px", style={"margin-right": "30px"}),
                    html.Img(src='data:image/jpg;base64,{}'.format(logo_etsi), width="150px", height="50px"),
                    html.H6("Realizado por: Felipe Llinares Gómez", style={"margin-left": "auto", "margin-right": "20px"}),
                ],
                className="row",
                style={"margin-top": "20px", "margin-bottom": "20px", "display": "flex", "align-items": "center"}
            )
        ]
    )
