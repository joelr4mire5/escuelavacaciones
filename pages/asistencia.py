# pages/asistencia.py

import dash
import sqlite3
import datetime
from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
from database import DB_PATH
from dash.dependencies import ALL

dash.register_page(__name__, path="/asistencia")

DIAS = ["Día 1", "Día 2", "Día 3", "Día 4","Día 5"]

layout = dbc.Container([
    html.H2("Registro de Asistencia y Puntualidad", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(id="equipo-filtro", placeholder="Seleccione un equipo")
        ], md=6),
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="estudiante-filtro", placeholder="Seleccione un estudiante")
        ], md=6),
    ], className="mb-4"),

    html.Div(id="lista-asistencia"),

    html.Hr(),
    html.Div(id="tabla-resumen-asistencia")
])

@callback(
    Output("equipo-filtro", "options"),
    Input("equipo-filtro", "id")
)
def cargar_equipos(_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
    equipos = cursor.fetchall()
    conn.close()
    return [{"label": e[0], "value": e[0]} for e in equipos]

@callback(
    Output("estudiante-filtro", "options"),
    Input("equipo-filtro", "value")
)
def cargar_estudiantes_por_equipo(equipo):
    if not equipo:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes WHERE equipo = ? ORDER BY nombre", (equipo,))
    estudiantes = cursor.fetchall()
    conn.close()
    return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]

@callback(
    Output("lista-asistencia", "children"),
    Input("estudiante-filtro", "value")
)
def mostrar_asistencia_estudiante(estudiante_id):
    if not estudiante_id:
        return html.P("Seleccione un estudiante para registrar asistencia.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM estudiantes WHERE id = ?", (estudiante_id,))
    nombre = cursor.fetchone()[0]

    cursor.execute("SELECT dia, presente, puntual FROM asistencia WHERE estudiante_id = ?", (estudiante_id,))
    registros = cursor.fetchall()
    conn.close()

    dias_asistencia = [r[0] for r in registros if r[1] == 1]
    dias_puntualidad = [r[0] for r in registros if r[2] == 1]

    return html.Div([
        html.H5(nombre),
        dbc.Row([
            dbc.Col([
                html.Label("Asistencia"),
                dcc.Checklist(
                    id={"type": "asistencia", "estudiante": estudiante_id},
                    options=[{"label": d, "value": i} for i, d in enumerate(DIAS)],
                    value=dias_asistencia,
                    inline=True
                )
            ], md=6),
            dbc.Col([
                html.Label("Puntualidad"),
                dcc.Checklist(
                    id={"type": "puntualidad", "estudiante": estudiante_id},
                    options=[{"label": d, "value": i} for i, d in enumerate(DIAS)],
                    value=dias_puntualidad,
                    inline=True
                )
            ], md=6)
        ]),
        html.Hr(),
        dbc.Button("Guardar Asistencia", id="guardar-asistencia", color="primary", className="mt-3"),
        html.Div(id="mensaje-asistencia", className="text-success mt-2")
    ])

@callback(
    Output("mensaje-asistencia", "children"),
    Output("tabla-resumen-asistencia", "children"),
    Input("guardar-asistencia", "n_clicks"),
    State("estudiante-filtro", "value"),
    State({"type": "asistencia", "estudiante": ALL}, "value"),
    State({"type": "puntualidad", "estudiante": ALL}, "value"),
    State({"type": "asistencia", "estudiante": ALL}, "id"),
    prevent_initial_call=True
)
def guardar_asistencia(n, estudiante_id, lista_asistencia, lista_puntualidad, ids):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Crear tabla asistencia si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS asistencia (
            estudiante_id INTEGER,
            dia INTEGER,
            presente INTEGER DEFAULT 0,
            puntual INTEGER DEFAULT 0,
            puntaje_asistencia INTEGER DEFAULT 0,
            puntaje_puntual INTEGER DEFAULT 0,
            PRIMARY KEY(estudiante_id, dia),
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
        )
    """)

    for i, estado_asistencia in enumerate(lista_asistencia):
        estudiante_id = ids[i]["estudiante"]
        estado_puntualidad = lista_puntualidad[i]

        for dia in range(len(DIAS)):
            presente = dia in estado_asistencia
            puntual = dia in estado_puntualidad

            if puntual and not presente:
                return f"Error: No se puede marcar puntualidad en {DIAS[dia]} sin asistencia."

            cursor.execute("""
                INSERT INTO asistencia (estudiante_id, dia, presente, puntual, puntaje_asistencia, puntaje_puntual)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(estudiante_id, dia) DO UPDATE SET
                    presente=excluded.presente,
                    puntual=excluded.puntual,
                    puntaje_asistencia=excluded.puntaje_asistencia,
                    puntaje_puntual=excluded.puntaje_puntual
            """, (
                estudiante_id,
                dia,
                int(presente),
                int(puntual),
                2 if presente else 0,
                2 if puntual else 0
            ))

    conn.commit()
    cursor.execute("""
        SELECT SUM(puntaje_asistencia), SUM(puntaje_puntual)
        FROM asistencia
        WHERE estudiante_id = ?
    """, (estudiante_id,))
    resumen = cursor.fetchone()
    conn.close()

    tabla = dbc.Table([
        html.Thead(html.Tr([html.Th("Total Asistencia"), html.Th("Total Puntualidad")])),
        html.Tbody([
            html.Tr([html.Td(resumen[0] or 0), html.Td(resumen[1] or 0)])
        ])
    ], bordered=True, hover=True, responsive=True)

    return "Datos guardados correctamente.", tabla
