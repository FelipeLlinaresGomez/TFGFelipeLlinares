from dash import html
import dash_leaflet as dl
import base64
from dash import dcc, dash_table

opciones_tramos = [
    "Mañana", "Tarde", "Noche"
]

opciones_meses = [
    "Enero", "Febrero", "Marzo", "Abril",
    "Mayo", "Junio", "Julio", "Agosto",
    "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

def generar_layout_usuario(df):
    #Crear dropdowns

    anios_data = df['Año'].apply(lambda x: x.strip())
    anios_data_ordenados = anios_data[anios_data != "No informado"].drop_duplicates().sort_values()
    opciones_dropdown_anios = anios_data_ordenados.values

    distritos_data = df[df['Distrito'] != "No informado"]
    distritos_data_grouped = distritos_data.groupby(['Distrito']).size().reset_index(name='Count')
    distritos_data_grouped = distritos_data_grouped[distritos_data_grouped['Count'] > 50]
    opciones_dropdown_distritos =distritos_data_grouped['Distrito']

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
                            options=[ {"label": k, "value": k} for k in opciones_meses ],
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
                            options=[ {"label": k, "value": k} for k in opciones_tramos],
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
            html.Div(
                children=[
                    html.H3("VISUALIZACIÓN DE DELITOS EN MÁLAGA", style= {"text-align": "center", "padding-top":"30px", "padding-bottom": "15px", "color":"#fbfbfb"}),
                ],
                className="row",
                style={"background-color": "#002b73"}
            ),
            html.Div(
                children=[
                    html.Div(
                        html.Button("Inserción datos", id='btn-administrador-insercion', style={"text-align": "center", "color":"#fbfbfb", "border": "none"}),
                        style={"flex-grow": 1, "text-align": "right"},
                    ),
                    html.Div(
                        html.Button("Borrado datos", id='btn-administrador-borrado', style={"text-align": "center", "color":"#fbfbfb", "border": "none"}),
                        style={"flex-grow": 1, "text-align": "right"},
                    ),
                    html.Div(
                        html.Button("Gestión usuarios", id='btn-administrador-usuarios', style={"text-align": "center", "color":"#fbfbfb", "border": "none"}),
                        style={"flex-grow": 1, "text-align": "right"},
                    ),
                ],
                className="row",
                style={"background-color": "#032357", "margin-bottom": "40px", "display": "flex", "justify-content": "flex-end"}
            ),
            generar_layout_administrador_insercion(),
            generar_layout_administrador_borrado(),
            generar_layout_administrador_usuarios(),
        ],
        id='layout-administrador',
        style={"background-color": "#ffffff", "font-family": "HelveticaNeue, sans-serif", "display": "none"}
    )

def generar_layout_administrador_insercion():
    return html.Div(
            children=[
                html.Div(
                    html.P("Suba todos los archivos CSV en el siguiente recuadro:", style={"margin": "0 auto", "font-size": "20px"}),
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
                html.Div(id="output-data-upload", style={"margin": "0 auto", "text-align": "center"}),
                generar_footer_bottom(),
            ],
            id='layout-administrador-subida-archivos',
            style = {"display": "block"}
        )

def generar_layout_administrador_borrado():
    return html.Div(
            children=[
                html.Div(
                    html.P("Borre todos los datos del año seleccionado:", style={"margin": "0 auto", "font-size": "20px"}),
                    style={"display": "flex", "justify-content": "center",  "margin-bottom": "30px"}
                ),
                html.Div(
                    html.Div(
                        [
                            html.Label("Año"),
                            dcc.Dropdown(
                                id="dropdownAnios-borrado",
                                options=[],
                                #value= opciones_dropdown_anios[0],
                                placeholder = "Selecciona de la lista",
                                style= {"width": "400px"},
                                multi=True
                            ),
                        ],
                        style={"margin-bottom": "10px", "display": "table", "margin": "0 auto"},
                        id="dropdown-container-borrado-anios",
                    ),
                    style={"display": "flex", "justify-content": "center", "margin-bottom": "50px"}
                ),
                html.Div(
                    html.Button('BORRAR DATOS', id='borrar-datos-button', n_clicks=0, style={"margin": "0 auto",  "background-color": "#002b73", "color": "#fbfbfb"}),
                    style={"display": "flex", "justify-content": "center", "margin-bottom": "30px"}
                ),
                html.Div(id="output-data-borrado", style={"margin": "0 auto", "text-align": "center", "font-family": "HelveticaNeue, sans-serif", "font-size":"20px"}),
                generar_footer_bottom(),
            ],
            id='layout-administrador-borrado-archivos',
            style = {"display": "none"}
        )

def generar_layout_administrador_usuarios():
    opciones_administrador = ["Usuario", "Administrador"]
    return html.Div(
                children=[
                    html.Div([
                        html.Div([
                            html.Div(
                                html.P("Gestione los usuarios", style={"margin": "0 auto", "font-size": "20px"}),
                                style={"display": "flex", "justify-content": "center",  "margin-bottom": "20px"},
                                className="row"
                            ),
                            html.Div( 
                                dash_table.DataTable(
                                    id='table-usuarios',
                                    columns=[
                                        {'name': 'Usuario', 'id': 'Usuario'},
                                        {'name': 'Rol', 'id': 'Rol'},
                                    ],
                                    data=[],
                                    row_selectable='multiple',  # Allows selecting one or more row at a time
                                    selected_rows=[],  # Initially, no rows are selected
                                    style_table={'margin': '0 auto', 'text-align': 'center', 'margin-bottom':'45px'}
                                ),
                            ),
                            html.Button('BORRAR USUARIOS SELECCIONADOS', id='borrar-usuarios-button', n_clicks=0, style={"background-color": "#002b73", "color": "#fbfbfb", "margin-bottom": "30px"}),
                            html.Div(id="output-data-borrado-usuarios", style={"margin": "0 auto", "text-align": "center", "margin-bottom": "150px", "font-family": "HelveticaNeue, sans-serif", "font-size":"20px"}),
                        ], className="six columns", style={'text-align': 'center'}),  # Center the 6 columns div
                    ]),                
                    html.Div(
                        children=[
                            html.Div(
                                html.P("Cree un nuevo usuario", style={"margin": "0 auto", "font-size": "20px"}),
                                style={"display": "flex", "justify-content": "center",  "margin-bottom": "20px"},
                                className="row"
                            ),
                            html.Div(
                                children=[
                                    html.Div(
                                        [
                                            html.Label("Nuevo usuario", style={"text-align": "left", "font-family": "HelveticaNeue, sans-serif"}),
                                            dcc.Input(id="crear-usuario-username-input", type="text", placeholder="Ingrese nuevo usuario", style={"width": "300px", "font-family": "HelveticaNeue, sans-serif"}),
                                        ],
                                        style={"margin-bottom": "15px"},
                                        className="row"
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Contraseña", style={"text-align": "left", "font-family": "HelveticaNeue, sans-serif",}),
                                            dcc.Input(id="crear-usuario-password-input", type="password", placeholder="Ingrese nueva contraseña", style={"width": "300px", "font-family": "HelveticaNeue, sans-serif",}),
                                        ],
                                        style={"margin-bottom": "15px"},
                                        className="row"
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Repita la contraseña", style={"text-align": "left", "font-family": "HelveticaNeue, sans-serif",}),
                                            dcc.Input(id="crear-usuario-password-repetida-input", type="password", placeholder="Ingrese nueva contraseña", style={"width": "300px", "font-family": "HelveticaNeue, sans-serif",}),
                                        ],
                                        style={"margin-bottom": "15px"},
                                    ),
                                    html.Div(
                                        [
                                            html.Label("Rol", style={"text-align": "left", "font-family": "HelveticaNeue, sans-serif"}),
                                            dcc.Dropdown(
                                                id="dropdownRol",
                                                options=[ {"label": desc, "value": index} for index, desc in enumerate(opciones_administrador) ],
                                                placeholder = "Selecciona el rol",
                                                style= {"width": "300px", "text-align": "left", "font-family": "HelveticaNeue, sans-serif"},
                                            ),
                                        ],  
                                        style={"margin-bottom": "45px"},
                                        id="dropdown-container-rol",
                                    ),
                                    html.Button('CREAR USUARIO', id='crear-usuario-button', n_clicks=0, style={"background-color": "#002b73", "color": "#fbfbfb"}),
                                ],
                                className="row",
                                style={"margin": "0 auto", "display": "block", "width": "300px", "text-align": "center", "margin-bottom": "30px"}
                            ),               
                            html.Div(id="output-data-usuarios", style={"margin": "0 auto", "text-align": "center", "margin-bottom": "150px", "font-family": "HelveticaNeue, sans-serif", "font-size":"20px"}),
                        ],
                        className="six columns",
                    ),
                    html.Div(
                        children=[
                            generar_footer()
                        ],
                        className="twelve columns"  # Set this to occupy all twelve columns
                    ),
                ],
                id='layout-administrador-usuarios',
                style = {"display": "none", "font-family": "HelveticaNeue, sans-serif"}
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
            style={"margin": "0 auto", "display": "block", "width": "300px", "text-align": "center", "margin-bottom": "30px"}
        ),
        html.H6(id="login-error-message", style= {"text-align": "center", "color":"red" ,"margin-bottom": "120px", "font-family": "HelveticaNeue, sans-serif"}),
        generar_footer_bottom()
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
        generar_footer_bottom()
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
                    html.H6("Realizado por: Felipe Llinares Gómez", style={"margin-left":"auto", "margin-right": "10px"}),
                ],
                className="row",
                style={"margin-top": "20px", "margin-bottom": "20px", "display": "flex", "align-items": "center"}
            )
        ]
    )

def generar_footer_bottom():
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
                    html.H6("Realizado por: Felipe Llinares Gómez", style={"margin-left":"auto","margin-right": "10px"}),
                ],
                className="row",
                style={"margin-top": "20px", "margin-bottom": "20px","display": "flex", "align-items": "center"}
            )
        ],
        style={"width": "99%", "position": "fixed", "bottom": "0"}
    )