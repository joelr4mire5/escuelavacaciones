# pages/visualizacion_equipo.py

import dash
import sqlite3
import pandas as pd
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px
from database import DB_PATH

dash.register_page(__name__, path="/visualizacion-equipo")

layout = dbc.Container([
    html.H2("Visualización por Equipos", className="my-4"),
    dcc.Graph(id="grafico-puntaje-equipo")
])

@callback(
    Output("grafico-puntaje-equipo", "figure"),
    Input("grafico-puntaje-equipo", "id")
)
def actualizar_grafico(_):
    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT e.id, e.nombre, e.equipo,
               (a.puntaje_asistencia + a.puntaje_puntual) AS puntaje,
               'Asistencia' AS categoria
        FROM asistencia a
        JOIN estudiantes e ON e.id = a.estudiante_id

        UNION ALL

        SELECT e.id, e.nombre, e.equipo,
               (m.puntos_biblia + m.puntos_folder + m.puntos_completo) AS puntaje,
               'Materiales' AS categoria
        FROM materiales m
        JOIN estudiantes e ON e.id = m.estudiante_id

        UNION ALL

        SELECT e.id, e.nombre, e.equipo,
               v.puntaje,
               'Visitas' AS categoria
        FROM visitas v
        JOIN estudiantes e ON e.id = v.invitador_id

        UNION ALL

        SELECT e.id, e.nombre, e.equipo,
               c.puntaje,
               'Memorización' AS categoria
        FROM citas_completadas cc
        JOIN citas c ON c.id = cc.cita_id
        JOIN estudiantes e ON e.id = cc.estudiante_id
    """

    try:
        df = pd.read_sql_query(query, conn)
        conn.close()
    except Exception as e:
        conn.close()
        return px.bar(title=f"Error al cargar datos: {e}")

    df_total = df.groupby("equipo", as_index=False)["puntaje"].sum()
    fig = px.bar(df_total, x="equipo", y="puntaje", title="Puntaje Total por Equipo", text_auto=True)
    fig.update_layout(yaxis_title="Puntaje Total", xaxis_title="Equipo")

    return fig
