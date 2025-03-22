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

    dbc.Button(id="btn-registrar", children="Registrar", color="primary", className="mb-3"),
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
    Input({"type": "btn-eliminar", "index": dash.ALL}, "n_clicks"),
    Input({"type": "btn-editar", "index": dash.ALL}, "n_clicks"),
    State("input-nombre", "value"),
    State("input-edad", "value"),
    State("input-equipo", "value"),
    State("selected-estudiante-id", "data"),
    prevent_initial_call=True
)
def manejar_estudiantes(n_registrar, eliminar_clicks, editar_clicks, nombre, edad, equipo, estudiante_id):
    triggered_id = ctx.triggered_id
    mensaje = ""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # --- ELIMINAR ---
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-eliminar":
        estudiante_id = triggered_id["index"]
        cursor.execute("DELETE FROM estudiantes WHERE id = ?", (estudiante_id,))
        mensaje = "Estudiante eliminado correctamente."
        conn.commit()
        conn.close()
        return mensaje, mostrar_estudiantes(), "", None, None, None, "Registrar"

    # --- EDITAR (rellenar campos) ---
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-editar":
        estudiante_id = triggered_id["index"]
        cursor.execute("SELECT nombre, edad, equipo FROM estudiantes WHERE id = ?", (estudiante_id,))
        row = cursor.fetchone()
        conn.close()
        return "", mostrar_estudiantes(), row[0], row[1], row[2], estudiante_id, "Actualizar"

    # --- REGISTRAR o ACTUALIZAR ---
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

    # Limpiar campos después de registrar o actualizar
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
    body = []

    for r in rows:
        body.append(html.Tr([
            html.Td(r[1]),
            html.Td(r[2]),
            html.Td(r[3]),
            html.Td([
                dbc.Button("Editar", id={"type": "btn-editar", "index": r[0]}, size="sm", color="warning", className="me-1"),
                dbc.Button("Eliminar", id={"type": "btn-eliminar", "index": r[0]}, size="sm", color="danger")
            ])
        ]))

    return dbc.Table([header, html.Tbody(body)], bordered=True, hover=True, responsive=True, striped=True)
