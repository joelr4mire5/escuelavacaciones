# pages/registro_puntajes.py

import dash
dash.register_page(__name__, path="/registro-puntajes")

from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlite3
from database import DB_PATH
import datetime

# Actividades y puntos
ACTIVIDADES = {
    "Puntualidad": 2,
    "Asistencia": 2,
    "Visita Niño": 4,
    "Visita Adulto": 6,
    "Folder": 1,
    "Biblia": 5,
    "Versículo": 5,
    "Capítulo": 10,
    "Folder Completo": 10
}

layout = dbc.Container([
    html.H2("Registro de Puntajes", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="dropdown-estudiante", placeholder="Seleccione un estudiante")
        ]),
        dbc.Col([
            dbc.Label("Actividad"),
            dcc.Dropdown(
                id="dropdown-actividad",
                options=[{"label": k, "value": k} for k in ACTIVIDADES.keys()],
                placeholder="Seleccione una actividad"
            )
        ])
    ], className="mb-3"),

    dbc.Button("Registrar Puntaje", id="btn-puntaje", color="success", className="mb-3"),
    html.Div(id="mensaje-puntaje", className="text-success mb-4"),

    html.Hr(),
    html.H4("Historial de Puntajes Recientes"),
    html.Div(id="tabla-puntajes")
])

@callback(
    Output("dropdown-estudiante", "options"),
    Input("dropdown-estudiante", "id")  # solo para disparar al cargar
)
def cargar_estudiantes(_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()
    return [{"label": nombre, "value": id_} for id_, nombre in rows]

@callback(
    Output("mensaje-puntaje", "children"),
    Output("tabla-puntajes", "children"),
    Input("btn-puntaje", "n_clicks"),
    State("dropdown-estudiante", "value"),
    State("dropdown-actividad", "value"),
    prevent_initial_call=True
)
def registrar_puntaje(n_clicks, estudiante_id, actividad):
    if not estudiante_id or not actividad:
        return "Seleccione un estudiante y una actividad.", mostrar_puntajes()

    puntos = ACTIVIDADES[actividad]
    fecha = datetime.date.today().isoformat()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO puntajes (estudiante_id, actividad, puntos, fecha) VALUES (?, ?, ?, ?)",
        (estudiante_id, actividad, puntos, fecha)
    )
    conn.commit()
    conn.close()

    return f"Se registraron {puntos} puntos por '{actividad}'.", mostrar_puntajes()

def mostrar_puntajes(limit=20):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT e.nombre, p.actividad, p.puntos, p.fecha
        FROM puntajes p
        JOIN estudiantes e ON p.estudiante_id = e.id
        ORDER BY p.id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return html.P("No hay puntajes registrados aún.")

    header = html.Thead(html.Tr([
        html.Th("Nombre"), html.Th("Actividad"), html.Th("Puntos"), html.Th("Fecha")
    ]))
    body = html.Tbody([
        html.Tr([html.Td(r[0]), html.Td(r[1]), html.Td(r[2]), html.Td(r[3])]) for r in rows
    ])

    return dbc.Table([header, body], bordered=True, hover=True, responsive=True)
