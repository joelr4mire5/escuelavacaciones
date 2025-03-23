# pages/registro_estudiantes.py

import dash
dash.register_page(__name__, path="/registro-estudiantes")

from dash import html, dcc, Input, Output, State, ctx
import dash_bootstrap_components as dbc
import sqlite3
from database import DB_PATH

EQUIPOS = ["Amarillo", "Azul", "Verde", "Rojo"]

layout = dbc.Container([
    html.H2("Registro de Estudiantes", className="my-4"),

    dcc.Store(id="selected-estudiante-id", storage_type="session"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Nombre del Estudiante"),
            dbc.Input(id="input-nombre", type="text", placeholder="Ingrese el nombre"),
        ]),
        dbc.Col([
            dbc.Label("Edad"),
            dbc.Input(id="input-edad", type="number", min=1, placeholder="Edad"),
        ]),
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(
                id="input-equipo",
                options=[{"label": eq, "value": eq} for eq in EQUIPOS],
                placeholder="Seleccione un equipo"
            )
        ])
    ], className="mb-3"),

    dbc.Button("Registrar", id="btn-registrar", color="primary", className="mb-3"),
    html.Div(id="registro-msg", className="text-success mb-3"),

    html.Hr(),

    html.H4("Buscar y Filtrar Estudiantes", className="mt-3"),
    dbc.Row([
        dbc.Col([
            dbc.Label("Buscar por nombre"),
            dbc.Input(id="filtro-nombre", placeholder="Ej. Juan", type="text")
        ], md=6),
        dbc.Col([
            dbc.Label("Filtrar por equipo"),
            dcc.Dropdown(
                id="filtro-equipo",
                options=[{"label": eq, "value": eq} for eq in EQUIPOS],
                placeholder="Todos los equipos"
            )
        ], md=6)
    ], className="mb-3"),

    html.Div(id="lista-estudiantes")
])

# Callback único para manejar registro, edición, eliminación y filtros
@dash.callback(
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
    Input("filtro-nombre", "value"),
    Input("filtro-equipo", "value"),
    State("input-nombre", "value"),
    State("input-edad", "value"),
    State("input-equipo", "value"),
    State("selected-estudiante-id", "data"),
    prevent_initial_call=True
)
def manejar_estudiantes(n_registrar, eliminar_clicks, editar_clicks, filtro_nombre, filtro_equipo,
                        nombre, edad, equipo, estudiante_id):
    triggered_id = ctx.triggered_id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    mensaje = ""
    modo = "Registrar"

    # --- Eliminar ---
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-eliminar":
        estudiante_id = triggered_id["index"]
        cursor.execute("DELETE FROM estudiantes WHERE id = ?", (estudiante_id,))
        conn.commit()
        conn.close()
        return "Estudiante eliminado correctamente.", mostrar_estudiantes(filtro_nombre, filtro_equipo), "", None, None, None, modo

    # --- Editar: cargar datos al formulario ---
    if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-editar":
        estudiante_id = triggered_id["index"]
        cursor.execute("SELECT nombre, edad, equipo FROM estudiantes WHERE id = ?", (estudiante_id,))
        row = cursor.fetchone()
        conn.close()
        return "", mostrar_estudiantes(filtro_nombre, filtro_equipo), row[0], row[1], row[2], estudiante_id, "Actualizar"

    # --- Registrar o Actualizar ---
    if ctx.triggered_id == "btn-registrar":
        if not nombre or not edad or not equipo:
            conn.close()
            return "Por favor complete todos los campos.", mostrar_estudiantes(filtro_nombre, filtro_equipo), nombre, edad, equipo, estudiante_id, modo

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
        return mensaje, mostrar_estudiantes(filtro_nombre, filtro_equipo), "", None, None, None, "Registrar"

    # --- Filtros (nombre y equipo) ---
    conn.close()
    return "", mostrar_estudiantes(filtro_nombre, filtro_equipo), nombre, edad, equipo, estudiante_id, "Registrar"

# Mostrar estudiantes con filtros
def mostrar_estudiantes(filtro_nombre=None, filtro_equipo=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = "SELECT id, nombre, edad, equipo FROM estudiantes WHERE 1=1"
    params = []

    if filtro_nombre:
        query += " AND nombre LIKE ?"
        params.append(f"%{filtro_nombre}%")

    if filtro_equipo:
        query += " AND equipo = ?"
        params.append(filtro_equipo)

    query += " ORDER BY nombre"
    cursor.execute(query, params)
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
                dbc.Button("Editar", id={"type": "btn-editar", "index": r[0]}, size="sm", color="warning", className="me-1"),
                dbc.Button("Eliminar", id={"type": "btn-eliminar", "index": r[0]}, size="sm", color="danger")
            ])
        ]) for r in rows
    ])

    return dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)
