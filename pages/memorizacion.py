# pages/memorizacion.py

import dash
import sqlite3
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from database import DB_PATH
import datetime


dash.register_page(__name__, path="/memorizacion")

layout = dbc.Container([
    html.H2("Registro de Memorización", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(id="equipo-mem", placeholder="Seleccione un equipo")
        ], md=4),
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="estudiante-mem", placeholder="Seleccione un estudiante")
        ], md=4),
        dbc.Col([
            dbc.Label("Tipo"),
            dcc.Dropdown(
                id="tipo-cita-mem",
                options=[
                    {"label": "Versículo", "value": "Versículo"},
                    {"label": "Capítulo", "value": "Capítulo"}
                ],
                placeholder="Seleccione tipo"
            )
        ], md=4)
    ], className="mb-3"),

    html.Div(id="seccion-citas-mem"),
    html.Div(id="mensaje-mem", className="text-success mt-3")
])

@callback(
    Output("equipo-mem", "options"),
    Input("equipo-mem", "id")
)
def cargar_equipos(_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
    equipos = cursor.fetchall()
    conn.close()
    return [{"label": e[0], "value": e[0]} for e in equipos]

@callback(
    Output("estudiante-mem", "options"),
    Input("equipo-mem", "value")
)
def cargar_estudiantes(equipo):
    if not equipo:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes WHERE equipo = ? ORDER BY nombre", (equipo,))
    estudiantes = cursor.fetchall()
    conn.close()
    return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]

@callback(
    Output("seccion-citas-mem", "children"),
    Input("estudiante-mem", "value"),
    Input("tipo-cita-mem", "value")
)
def mostrar_citas(estudiante_id, tipo):
    if not estudiante_id or not tipo:
        return ""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS citas_completadas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER NOT NULL,
            cita_id INTEGER NOT NULL,
            completado INTEGER DEFAULT 1,
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id),
            FOREIGN KEY(cita_id) REFERENCES citas(id)
        )
    """)

    cursor.execute("SELECT id, cita, puntaje FROM citas WHERE tipo = ?", (tipo,))
    citas = cursor.fetchall()

    # Obtener los completados
    cursor.execute("SELECT cita_id FROM citas_completadas WHERE estudiante_id = ?", (estudiante_id,))
    completados = set(row[0] for row in cursor.fetchall())
    conn.close()

    checklist = dbc.Checklist(
        id="checklist-citas",
        options=[{"label": f"{cita} ({pts} pts)", "value": id_} for id_, cita, pts in citas],
        value=[id_ for id_, cita, pts in citas if id_ in completados],
        inline=False,
        switch=True
    )

    return html.Div([
        html.Label("Citas disponibles"),
        checklist,
        dbc.Button("Guardar", id="btn-guardar-mem", color="primary", className="mt-2")
    ])

@callback(
    Output("mensaje-mem", "children"),
    Input("btn-guardar-mem", "n_clicks"),
    State("estudiante-mem", "value"),
    State("checklist-citas", "value"),
    State("tipo-cita-mem", "value"),
    prevent_initial_call=True
)
def guardar_memorizacion(n, estudiante_id, seleccionados, tipo):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM citas WHERE tipo = ?", (tipo,))
    todos = [row[0] for row in cursor.fetchall()]

    for cita_id in todos:
        if cita_id in seleccionados:
            cursor.execute("""
                INSERT OR REPLACE INTO citas_completadas (estudiante_id, cita_id, completado)
                VALUES (?, ?, 1)
            """, (estudiante_id, cita_id))
        else:
            cursor.execute("DELETE FROM citas_completadas WHERE estudiante_id = ? AND cita_id = ?", (estudiante_id, cita_id))

    conn.commit()
    conn.close()
    return "Citas actualizadas correctamente."
