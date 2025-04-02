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

    dbc.Row([
        dbc.Col([
            dbc.Label("Categoría"),
            dcc.Dropdown(
                id="filtro-categoria",
                options=[
                    {"label": "Todas las Categorías", "value": "Todas"},
                    {"label": "Asistencia", "value": "Asistencia"},
                    {"label": "Materiales", "value": "Materiales"},
                    {"label": "Visitas", "value": "Visitas"},
                    {"label": "Memorización", "value": "Memorización"}
                ],
                value="Todas"
            )
        ], width=6)
    ], className="mb-4"),

    dcc.Graph(id="grafico-puntaje-equipo")
])


@callback(
    Output("grafico-puntaje-equipo", "figure"),
    Input("filtro-categoria", "value")
)
def actualizar_grafico(categoria):
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

    if df.empty:
        return px.bar(title="No hay datos disponibles para visualizar.")

    if categoria != "Todas":
        df = df[df["categoria"] == categoria]

    df_total = df.groupby("equipo", as_index=False)["puntaje"].sum()

    color_map = {
        "Rojo": "#e74c3c",
        "Azul": "#3498db",
        "Verde": "#27ae60",
        "Amarillo": "#f1c40f"
    }

    fig = px.bar(
        df_total,
        x="equipo",
        y="puntaje",
        title=f"Puntaje por Equipo - {categoria if categoria != 'Todas' else 'Total'}",
        text_auto=True,
        color="equipo",
        color_discrete_map=color_map
    )
    fig.update_layout(yaxis_title="Puntaje Total", xaxis_title="Equipo")

    return fig
