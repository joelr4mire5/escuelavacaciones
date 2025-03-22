# pages/visualizacion_equipos.py

import dash
dash.register_page(__name__, path="/visualizacion-equipos")

from dash import html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
import plotly.express as px
from database import DB_PATH

layout = dbc.Container([
    html.H2("Visualización por Equipos", className="my-4"),

    dcc.Graph(id="grafico-totales-equipos"),
    html.Hr(),
    dcc.Graph(id="grafico-por-actividad")
])

@callback(
    Output("grafico-totales-equipos", "figure"),
    Output("grafico-por-actividad", "figure"),
    Input("grafico-totales-equipos", "id")
)
def actualizar_graficos(_):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT e.equipo, p.actividad, SUM(p.puntos) as total_puntos
        FROM puntajes p
        JOIN estudiantes e ON p.estudiante_id = e.id
        GROUP BY e.equipo, p.actividad
    """
    df = pd.read_sql_query(query, conn)
    conn.close()

    if df.empty:
        return px.bar(title="Sin datos disponibles"), px.bar(title="")

    # ✅ Total por equipo (suma global)
    total_equipo = df.groupby("equipo")["total_puntos"].sum().reset_index()
    fig_equipo = px.bar(
        total_equipo,
        x="equipo",
        y="total_puntos",
        title="Puntaje Total por Equipo",
        labels={"equipo": "Equipo", "total_puntos": "Puntos"},
        text_auto=True
    )

    # ✅ Total por actividad y equipo
    fig_actividad = px.bar(
        df,
        x="actividad",
        y="total_puntos",
        color="equipo",
        barmode="group",
        title="Puntos por Actividad y por Equipo",
        labels={"actividad": "Actividad", "total_puntos": "Puntos"},
        text_auto=True
    )

    return fig_equipo, fig_actividad
