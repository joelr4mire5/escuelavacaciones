# pages/tienda.py

import dash
dash.register_page(__name__, path="/tienda")

from dash import html, dcc, Input, Output, State, callback, ctx
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
    html.Div(id="mensaje-compra", className="text-success mb-3"),

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
    Output("tabla-compras", "children"),
    Output("mensaje-compra", "children"),
    Output("puntos-disponibles", "children"),
    Input("dropdown-estudiante-tienda", "value"),
    Input("btn-comprar", "n_clicks"),
    State("input-descripcion", "value"),
    State("input-puntos", "value"),
    prevent_initial_call=True
)
def actualizar_compras(estudiante_id, n_clicks, descripcion, puntos):
    if not estudiante_id:
        return "", "", ""

    # Determinar qué disparó el callback
    triggered_id = ctx.triggered_id if ctx.triggered_id else None
    mensaje = ""

    # Si se presionó el botón de compra
    if triggered_id == "btn-comprar":
        if not descripcion or not puntos:
            mensaje = "Debe ingresar descripción y puntos."
        else:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO compras (estudiante_id, descripcion, puntos_gastados) VALUES (?, ?, ?)",
                (estudiante_id, descripcion.strip(), puntos)
            )
            conn.commit()
            conn.close()
            mensaje = f"Compra registrada: {descripcion} (-{puntos} pts)"

    # Obtener puntos ganados y gastados
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COALESCE(SUM(puntos), 0) FROM puntajes WHERE estudiante_id = ?", (estudiante_id,))
    ganados = cursor.fetchone()[0]
    cursor.execute("SELECT COALESCE(SUM(puntos_gastados), 0) FROM compras WHERE estudiante_id = ?", (estudiante_id,))
    gastados = cursor.fetchone()[0]
    disponibles = ganados - gastados

    # Obtener historial de compras
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
        tabla = html.P("Este estudiante no ha realizado compras.")
    else:
        tabla = dbc.Table([
            html.Thead(html.Tr([html.Th("Artículo"), html.Th("Puntos"), html.Th("Fecha")])),
            html.Tbody([
                html.Tr([html.Td(r["descripcion"]), html.Td(r["puntos_gastados"]), html.Td(r["fecha"])])
                for _, r in df.iterrows()
            ])
        ], bordered=True, hover=True, responsive=True, striped=True)

    return tabla, mensaje, f"{disponibles} puntos disponibles"
