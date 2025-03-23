# pages/registro_estudiantes.py

import dash
dash.register_page(__name__, path="/registro-estudiantes")

from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
import sqlite3
from database import DB_PATH

equipos = ["Amarillo", "Azul", "Verde", "Rojo"]

layout = dbc.Container([
    html.H2("Registro de Estudiantes", className="my-4"),

    dcc.Store(id="selected-estudiante-id", storage_type="session"),

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
    Output("input-nombre", "value"),
    Output("input-edad", "value"),
    Output("input-equipo", "value"),
    Output("selected-estudiante-id", "data"),
    Output("btn-registrar", "children"),
    Input("btn-registrar", "n_clicks"),
    Input({"type": "btn-editar-est", "index": dash.ALL}, "n_clicks"),
    Input({"type": "btn-eliminar-est", "index": dash.ALL}, "n_clicks"),
    State("input-nombre", "value"),
    State("input-edad", "value"),
    State("input-equipo", "value"),
    State("selected-estudiante-id", "data"),
    prevent_initial_call=True
)
def manejar_estudiantes(n_clicks_registrar, editar_clicks, eliminar_clicks, nombre, edad, equipo, estudiante_id):
    triggered = ctx.triggered_id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Eliminar
    if isinstance(triggered, dict) and triggered.get("type") == "btn-eliminar-est":
        est_id = triggered["index"]
        cursor.execute("DELETE FROM estudiantes WHERE id = ?", (est_id,))
        conn.commit()
        conn.close()
        return "Estudiante eliminado correctamente.", mostrar_estudiantes(), "", None, None, None, "Registrar"

    # Editar (cargar datos en inputs)
    if isinstance(triggered, dict) and triggered.get("type") == "btn-editar-est":
        est_id = triggered["index"]
        cursor.execute("SELECT nombre, edad, equipo FROM estudiantes WHERE id = ?", (est_id,))
        row = cursor.fetchone()
        conn.close()
        return "", mostrar_estudiantes(), row[0], row[1], row[2], est_id, "Actualizar"

    # Registrar o actualizar
    if not nombre or not edad or not equipo:
        conn.close()
        return "Por favor complete todos los campos.", mostrar_estudiantes(), nombre, edad, equipo, estudiante_id, "Registrar"

    if estudiante_id:
        cursor.execute("UPDATE estudiantes SET nombre = ?, edad = ?, equipo = ? WHERE id = ?",
                       (nombre.strip(), edad, equipo, estudiante_id))
        mensaje = "Estudiante actualizado correctamente."
    else:
        cursor.execute("INSERT INTO estudiantes (nombre, edad, equipo) VALUES (?, ?, ?)",
                       (nombre.strip(), edad, equipo))
        mensaje = f"Estudiante '{nombre}' registrado exitosamente."

    conn.commit()
    conn.close()

    return mensaje, mostrar_estudiantes(), "", None, None, None, "Registrar"

def mostrar_estudiantes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, edad, equipo FROM estudiantes ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return html.P("No hay estudiantes registrados aún.")

    header = html.Thead(html.Tr([
        html.Th("Nombre"), html.Th("Edad"), html.Th("Equipo"), html.Th("Acciones")
    ]))
    body = html.Tbody([
        html.Tr([
            html.Td(r[1]),
            html.Td(r[2]),
            html.Td(r[3]),
            html.Td([
                dbc.Button("Editar", id={"type": "btn-editar-est", "index": r[0]}, color="warning", size="sm", className="me-1"),
                dbc.Button("Eliminar", id={"type": "btn-eliminar-est", "index": r[0]}, color="danger", size="sm")
            ])
        ]) for r in rows
    ])

    return dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)
