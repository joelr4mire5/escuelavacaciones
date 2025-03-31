import dash
import pandas as pd
import sqlite3
from dash import html, dcc, callback, Input, Output, State
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from database import DB_PATH

dash.register_page(__name__, path="/visualizacion_estudiantes")

layout = dbc.Container([
    html.H2("Informes y Ranking", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Seleccione Informe"),
            dcc.Dropdown(
                id="dropdown-informe",
                options=[
                    {"label": "Asistencia Perfecta", "value": "asistencia"},
                    {"label": "Top 3 por Clase - Visitas", "value": "visitas"},
                    {"label": "Top 3 por Clase - Memorización", "value": "memoria"},
                    {"label": "Top 3 por Clase - Puntaje Total", "value": "total"},
                ],
                placeholder="Seleccione una opción"
            )
        ]),
        dbc.Col([
            dbc.Button("Exportar a Excel", id="btn-exportar", color="primary", className="mt-4")
        ])
    ]),

    html.Hr(),
    html.Div(id="tabla-informe"),
    dcc.Download(id="download-informe")
])

EDAD_CLASES = {
    "0-3": (0, 3),
    "4-5": (4, 5),
    "6-8": (6, 8),
    "9-11": (9, 11),
    "12+": (12, 99)
}

@callback(
    Output("tabla-informe", "children"),
    Input("dropdown-informe", "value")
)
def mostrar_informe(tipo):
    if not tipo:
        raise PreventUpdate

    conn = sqlite3.connect(DB_PATH)
    df_est = pd.read_sql_query("SELECT id, nombre, edad FROM estudiantes", conn)

    if tipo == "asistencia":
        df = pd.read_sql_query("""
            SELECT e.nombre, e.edad,
                   SUM(a.presente) AS total_presente,
                   SUM(a.puntual) AS total_puntual
            FROM asistencia a
            JOIN estudiantes e ON e.id = a.estudiante_id
            GROUP BY a.estudiante_id
            HAVING total_presente = 5 AND total_puntual = 5
        """, conn)
        conn.close()
        return dbc.Table.from_dataframe(df[["nombre", "edad","total_presente","total_puntual"]], striped=True, bordered=True, hover=True)

    # Crear vista unificada
    conn.executescript("""
        CREATE TEMP VIEW IF NOT EXISTS resumen_puntaje AS
        SELECT e.id, e.nombre, e.edad,
               v.puntaje,
               'Visitas' AS categoria
        FROM visitas v
        JOIN estudiantes e ON e.id = v.invitador_id
        UNION ALL
        SELECT e.id, e.nombre, e.edad,
               c.puntaje,
               'Memoria' AS categoria
        FROM citas_completadas cc
        JOIN citas c ON c.id = cc.cita_id
        JOIN estudiantes e ON e.id = cc.estudiante_id
        UNION ALL
        SELECT e.id, e.nombre, e.edad,
               (a.puntaje_asistencia + a.puntaje_puntual) AS puntaje,
               'Asistencia' AS categoria
        FROM asistencia a
        JOIN estudiantes e ON e.id = a.estudiante_id
        UNION ALL
        SELECT e.id, e.nombre, e.edad,
               (m.puntos_biblia + m.puntos_folder + m.puntos_completo) AS puntaje,
               'Materiales' AS categoria
        FROM materiales m
        JOIN estudiantes e ON e.id = m.estudiante_id;
    """)

    df = pd.read_sql_query("SELECT * FROM resumen_puntaje", conn)

    if tipo == "visitas":
        df_f = df[df["categoria"] == "Visitas"]
    elif tipo == "memoria":
        df_f = df[df["categoria"] == "Memoria"]
    else:  # total
        df_f = df.groupby(["id", "nombre", "edad"], as_index=False)["puntaje"].sum()

    conn.close()

    resultados = []

    for clase, (min_edad, max_edad) in EDAD_CLASES.items():
        df_clase = df_f[(df_f["edad"] >= min_edad) & (df_f["edad"] <= max_edad)]
        top3 = df_clase.sort_values("puntaje", ascending=False).head(3)
        if not top3.empty:
            resultados.append(html.H5(f"Clase {clase}"))
            resultados.append(dbc.Table.from_dataframe(top3[["nombre", "edad", "puntaje"]], striped=True, bordered=True, hover=True))

    return html.Div(resultados)

@callback(
    Output("download-informe", "data"),
    Input("btn-exportar", "n_clicks"),
    State("dropdown-informe", "value"),
    prevent_initial_call=True
)
def exportar_excel(n, tipo):
    if not tipo:
        raise PreventUpdate

    conn = sqlite3.connect(DB_PATH)

    if tipo == "asistencia":
        df = pd.read_sql_query("""
            SELECT e.nombre, e.edad,
                   SUM(a.presente) AS total_presente,
                   SUM(a.puntual) AS total_puntual
            FROM asistencia a
            JOIN estudiantes e ON e.id = a.estudiante_id
            GROUP BY a.estudiante_id
            HAVING total_presente = 5 AND total_puntual = 5
        """, conn)
        df = df[["nombre", "edad","total_presente","total_puntual"]]
        filename = "asistencia_perfecta.xlsx"
    else:
        conn.executescript("""
            CREATE TEMP VIEW IF NOT EXISTS resumen_puntaje AS
            SELECT e.id, e.nombre, e.edad,
                   v.puntaje,
                   'Visitas' AS categoria
            FROM visitas v
            JOIN estudiantes e ON e.id = v.invitador_id
            UNION ALL
            SELECT e.id, e.nombre, e.edad,
                   c.puntaje,
                   'Memoria' AS categoria
            FROM citas_completadas cc
            JOIN citas c ON c.id = cc.cita_id
            JOIN estudiantes e ON e.id = cc.estudiante_id
            UNION ALL
            SELECT e.id, e.nombre, e.edad,
                   (a.puntaje_asistencia + a.puntaje_puntual) AS puntaje,
                   'Asistencia' AS categoria
            FROM asistencia a
            JOIN estudiantes e ON e.id = a.estudiante_id
            UNION ALL
            SELECT e.id, e.nombre, e.edad,
                   (m.puntos_biblia + m.puntos_folder + m.puntos_completo) AS puntaje,
                   'Materiales' AS categoria
            FROM materiales m
            JOIN estudiantes e ON e.id = m.estudiante_id;
        """)
        df = pd.read_sql_query("SELECT * FROM resumen_puntaje", conn)
        if tipo == "visitas":
            df = df[df["categoria"] == "Visitas"]
            filename = "top3_visitas.xlsx"
        elif tipo == "memoria":
            df = df[df["categoria"] == "Memoria"]
            filename = "top3_memoria.xlsx"
        else:
            df = df.groupby(["id", "nombre", "edad"], as_index=False)["puntaje"].sum()
            filename = "top3_total.xlsx"

    conn.close()
    return dcc.send_data_frame(df.to_excel, filename, index=False)