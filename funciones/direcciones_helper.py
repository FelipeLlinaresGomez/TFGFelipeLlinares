def map_tipo_via(tipo_via):
    tipo_via_shp = tipo_via
    if tipo_via == "CALLE":
        tipo_via_shp = "CL"
    elif tipo_via == "AVDA":
        tipo_via_shp = "AV"
    elif tipo_via == "CTRA":
        tipo_via_shp = "CTRA"
    elif tipo_via == "CJON":
        tipo_via_shp = "CJON"
    elif tipo_via == "GRUPO":
        tipo_via_shp = "GPO"
    elif tipo_via == "PLAZA":
        tipo_via_shp = "PL"
    elif tipo_via == "PASEO":
        tipo_via_shp = "PSO"
    elif tipo_via == "CAMIN":
        tipo_via_shp = "CMNO"
    elif tipo_via == "PJE":
        tipo_via_shp = "PJE"
    elif tipo_via == "GTA":
        tipo_via_shp = "GTA"

    if tipo_via == "URB":
        tipo_via_shp = "CL"
    elif tipo_via == "BARRI":
        tipo_via_shp = "CL"
    elif tipo_via == "COL":
        tipo_via_shp = "CL"
    elif tipo_via == "POLIG":
        tipo_via_shp = "CL"
    elif tipo_via == "HITO":
        tipo_via_shp = "CL"
    elif tipo_via == "TRAV":
        tipo_via_shp = "CL"
    elif tipo_via == "EDIF":
        tipo_via_shp = "CL"
    elif tipo_via == "TREN":
        tipo_via_shp = "CL"
    elif tipo_via == "BUS":
        tipo_via_shp = "CL"
    elif tipo_via == "METRO":
        tipo_via_shp = "CL"
    elif tipo_via == "POBLA":
        tipo_via_shp = "CL"
    elif tipo_via == "LUGAR":
        tipo_via_shp = "CL"

    return tipo_via_shp