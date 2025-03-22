# pages/registro_estudiantes.py

import dash
dash.register_page(__name__, path="/registro-estudiantes")

from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlite3
from database import DB_PATH

equipos = ["Amarillo", "Azul", "Verde", "Rojo"]

layout = dbc.Container([
    html.H2("Registro de Estudiantes", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Nombre del Estudiante"),
            dbc.Input(id="input-nombre", type="text", placeholder="Ingrese el nombre", required=True),
        ]),
        dbc.Col([
            dbc.Label("Edad"),
            dbc.Input(id="input-edad", type="number", min=1, placeholder="Edad", required=True),
        ]),
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(
                id="input-equipo",
                options=[{"label": eq, "value": eq} for eq in equipos],
                placeholder="Seleccione un equipo"
            ),
        ])
    ], className="mb-3"),

    dbc.Button("Registrar", id="btn-registrar", color="primary", className="mb-3"),
    html.Div(id="registro-msg", className="text-success"),

    html.Hr(),

    html.H4("Estudiantes Registrados"),
    html.Div(id="lista-estudiantes")
])

@callback(
    Output("registro-msg", "children"),
    Output("lista-estudiantes", "children"),
    Input("btn-registrar", "n_clicks"),
    State("input-nombre", "value"),
    State("input-edad", "value"),
    State("input-equipo", "value"),
    prevent_initial_call=True
)
def registrar_estudiante(n_clicks, nombre, edad, equipo):
    if not nombre or not edad or not equipo:
        return "Por favor complete todos los campos.", mostrar_estudiantes()

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO estudiantes (nombre, edad, equipo) VALUES (?, ?, ?)",
        (nombre.strip(), edad, equipo)
    )
    conn.commit()
    conn.close()

    return f"Estudiante '{nombre}' registrado exitosamente.", mostrar_estudiantes()

def mostrar_estudiantes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, edad, equipo FROM estudiantes ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return html.P("No hay estudiantes registrados aún.")

    table_header = [
        html.Thead(html.Tr([html.Th("Nombre"), html.Th("Edad"), html.Th("Equipo")]))
    ]
    table_body = [html.Tr([html.Td(r[0]), html.Td(r[1]), html.Td(r[2])]) for r in rows]

    return dbc.Table(table_header + [html.Tbody(table_body)], bordered=True, hover=True, responsive=True)
