# pages/tienda.py

import dash
dash.register_page(__name__, path="/tienda")

from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
from database import DB_PATH

layout = dbc.Container([
    html.H2("Tienda de Recompensas", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="dropdown-estudiante-tienda", placeholder="Seleccione un estudiante")
        ], md=6),
        dbc.Col([
            dbc.Label("Puntos Disponibles"),
            html.Div(id="puntos-disponibles", className="lead")
        ], md=6)
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Descripción del Artículo"),
            dbc.Input(id="input-descripcion", type="text", placeholder="Ej: Pelota")
        ]),
        dbc.Col([
            dbc.Label("Puntos a Descontar"),
            dbc.Input(id="input-puntos", type="number", min=1)
        ])
    ], className="mb-3"),

    dbc.Button("Registrar Compra", id="btn-comprar", color="primary", className="mb-3"),
    html.Div(id="mensaje-compra", className="text-success"),

    html.Hr(),

    html.H4("Historial de Compras"),
    html.Div(id="tabla-compras")
])


@callback(
    Output("dropdown-estudiante-tienda", "options"),
    Input("dropdown-estudiante-tienda", "id")
)
def cargar_estudiantes(_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes ORDER BY nombre")
    rows = cursor.fetchall()
    conn.close()
    return [{"label": nombre, "value": id_} for id_, nombre in rows]

@callback(
    Output("puntos-disponibles", "children"),
    Input("dropdown-estudiante-tienda", "value")
)
def mostrar_puntos(estudiante_id):
    if not estudiante_id:
        return "Seleccione un estudiante"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(puntos), 0) FROM puntajes WHERE estudiante_id = ?", (estudiante_id,))
    ganados = cursor.fetchone()[0]

    cursor.execute("SELECT COALESCE(SUM(puntos_gastados), 0) FROM compras WHERE estudiante_id = ?", (estudiante_id,))
    gastados = cursor.fetchone()[0]

    conn.close()
    disponibles = ganados - gastados
    return f"{disponibles} puntos disponibles"

@callback(
    Output("mensaje-compra", "children"),
    Output("tabla-compras", "children"),
    Input("btn-comprar", "n_clicks"),
    State("dropdown-estudiante-tienda", "value"),
    State("input-descripcion", "value"),
    State("input-puntos", "value"),
    prevent_initial_call=True
)
def registrar_compra(n_clicks, estudiante_id, descripcion, puntos):
    if not estudiante_id or not descripcion or not puntos:
        return "Complete todos los campos.", mostrar_historial(estudiante_id)

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO compras (estudiante_id, descripcion, puntos_gastados) VALUES (?, ?, ?)",
        (estudiante_id, descripcion.strip(), puntos)
    )
    conn.commit()
    conn.close()

    return f"Compra registrada: {descripcion} (-{puntos} pts)", mostrar_historial(estudiante_id)

@callback(
    Output("tabla-compras", "children"),
    Input("dropdown-estudiante-tienda", "value")
)
def mostrar_historial(estudiante_id):
    if not estudiante_id:
        return ""

    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        """
        SELECT descripcion, puntos_gastados, fecha
        FROM compras
        WHERE estudiante_id = ?
        ORDER BY fecha DESC
        """,
        conn,
        params=(estudiante_id,)
    )
    conn.close()

    if df.empty:
        return html.P("Este estudiante no ha realizado compras.")

    header = html.Thead(html.Tr([
        html.Th("Artículo"), html.Th("Puntos"), html.Th("Fecha")
    ]))
    body = html.Tbody([
        html.Tr([
            html.Td(row["descripcion"]),
            html.Td(row["puntos_gastados"]),
            html.Td(row["fecha"])
        ]) for _, row in df.iterrows()
    ])

    return dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)
