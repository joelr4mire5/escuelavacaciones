# pages/visualizacion_estudiantes.py

import dash
dash.register_page(__name__, path="/visualizacion-estudiantes")

from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
from database import DB_PATH

layout = dbc.Container([
    html.H2("Ranking de Estudiantes", className="my-4"),
    html.Div(id="tabla-estudiantes")
])

@callback(
    Output("tabla-estudiantes", "children"),
    Input("tabla-estudiantes", "id")  # se activa al cargar
)
def mostrar_tabla_estudiantes(_):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT e.nombre, e.equipo, COALESCE(SUM(p.puntos), 0) as total_puntos
        FROM estudiantes e
        LEFT JOIN puntajes p ON e.id = p.estudiante_id
        GROUP BY e.id
        ORDER BY total_puntos DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return html.P("No hay estudiantes registrados aún.")

    header = html.Thead(html.Tr([
        html.Th("Nombre"), html.Th("Equipo"), html.Th("Total de Puntos")
    ]))
    body = html.Tbody([
        html.Tr([
            html.Td(row["nombre"]),
            html.Td(row["equipo"]),
            html.Td(row["total_puntos"])
        ]) for _, row in df.iterrows()
    ])

    return dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)
