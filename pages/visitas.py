import dash
dash.register_page(__name__, path="/visitas")

from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
import sqlite3
from database import DB_PATH
import datetime

layout = dbc.Container([
    html.H2("Registro de Visitas", className="my-4"),

    dcc.Store(id="selected-visita-id", storage_type="session"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo del Invitador"),
            dcc.Dropdown(id="dropdown-equipo-visita", placeholder="Seleccione un equipo")
        ]),
        dbc.Col([
            dbc.Label("¿Quién lo invitó?"),
            dcc.Dropdown(id="dropdown-invitador-visita", placeholder="Seleccione al estudiante que invitó")
        ])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Nombre de la Visita"),
            dbc.Input(id="input-nombre-visita", type="text", placeholder="Ingrese el nombre")
        ]),
        dbc.Col([
            dbc.Label("¿Es adulto?"),
            dcc.Checklist(
                id="check-adulto-visita",
                options=[{"label": "Sí", "value": "adulto"}],
                value=[],
                inline=True
            )
        ])
    ], className="mb-3"),

    dbc.Button("Registrar", id="btn-registrar-visita", color="primary", className="mb-3"),
    html.Div(id="mensaje-visita", className="text-success"),

    html.Hr(),
    html.H4("Visitas Registradas"),
    html.Div(id="tabla-visitas")
])

# Cargar equipos
@callback(
    Output("dropdown-equipo-visita", "options"),
    Input("dropdown-equipo-visita", "id")
)
def cargar_equipos(_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
    equipos = cursor.fetchall()
    conn.close()
    return [{"label": e[0], "value": e[0]} for e in equipos]

# Cargar estudiantes según equipo seleccionado
@callback(
    Output("dropdown-invitador-visita", "options"),
    Input("dropdown-equipo-visita", "value")
)
def filtrar_estudiantes_por_equipo(equipo):
    if not equipo:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes WHERE equipo = ? ORDER BY nombre", (equipo,))
    estudiantes = cursor.fetchall()
    conn.close()
    return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]

# Manejar crear, editar y eliminar
@callback(
    Output("mensaje-visita", "children"),
    Output("tabla-visitas", "children"),
    Output("input-nombre-visita", "value"),
    Output("check-adulto-visita", "value"),
    Output("dropdown-invitador-visita", "value"),
    Output("selected-visita-id", "data"),
    Output("btn-registrar-visita", "children"),
    Input("btn-registrar-visita", "n_clicks"),
    Input({"type": "btn-editar-visita", "index": dash.ALL}, "n_clicks"),
    Input({"type": "btn-eliminar-visita", "index": dash.ALL}, "n_clicks"),
    State("input-nombre-visita", "value"),
    State("check-adulto-visita", "value"),
    State("dropdown-invitador-visita", "value"),
    State("selected-visita-id", "data"),
    prevent_initial_call=True
)
def manejar_visita(n_reg, editar_clicks, eliminar_clicks, nombre, adulto_valor, invitador_id, visita_id):
    triggered_id = ctx.triggered_id
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-eliminar-visita":
        visita_id = triggered_id["index"]
        cursor.execute("DELETE FROM visitas WHERE id = ?", (visita_id,))
        conn.commit()
        conn.close()
        return "Visita eliminada correctamente.", mostrar_visitas(), "", [], None, None, "Registrar"

    if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-editar-visita":
        visita_id = triggered_id["index"]
        cursor.execute("SELECT nombre, es_adulto, invitador_id FROM visitas WHERE id = ?", (visita_id,))
        row = cursor.fetchone()
        conn.close()
        return "", mostrar_visitas(), row[0], ["adulto"] if row[1] else [], row[2], visita_id, "Actualizar"

    if not nombre or not invitador_id:
        conn.close()
        return "Debe ingresar nombre e invitador.", mostrar_visitas(), nombre, adulto_valor, invitador_id, visita_id, "Registrar"

    es_adulto = 1 if "adulto" in adulto_valor else 0
    puntaje = 6 if es_adulto else 4

    if visita_id:
        cursor.execute("""
            UPDATE visitas
            SET nombre = ?, es_adulto = ?, invitador_id = ?, puntaje = ?
            WHERE id = ?
        """, (nombre.strip(), es_adulto, invitador_id, puntaje, visita_id))
        mensaje = "Visita actualizada correctamente."
    else:
        cursor.execute("""
            INSERT INTO visitas (nombre, es_adulto, invitador_id, puntaje)
            VALUES (?, ?, ?, ?)
        """, (nombre.strip(), es_adulto, invitador_id, puntaje))
        mensaje = "Visita registrada correctamente."

    conn.commit()
    conn.close()
    return mensaje, mostrar_visitas(), "", [], None, None, "Registrar"

# Tabla de visitas registradas
def mostrar_visitas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT v.id, v.nombre, v.es_adulto, v.puntaje, e.nombre
        FROM visitas v
        JOIN estudiantes e ON v.invitador_id = e.id
        ORDER BY v.nombre
    """)
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return html.P("No hay visitas registradas.")

    header = html.Thead(html.Tr([
        html.Th("Nombre"), html.Th("Adulto"), html.Th("Invitado por"), html.Th("Puntaje"), html.Th("Acciones")
    ]))
    body = html.Tbody([
        html.Tr([
            html.Td(r[1]),
            html.Td("Sí" if r[2] else "No"),
            html.Td(r[4]),
            html.Td(r[3]),
            html.Td([
                dbc.Button("Editar", id={"type": "btn-editar-visita", "index": r[0]}, size="sm", color="warning", className="me-1"),
                dbc.Button("Eliminar", id={"type": "btn-eliminar-visita", "index": r[0]}, size="sm", color="danger")
            ])
        ]) for r in rows
    ])

    return dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)
