# pages/visualizacion_equipo.py

import dash
import pandas as pd
import psycopg2
from dash import html, dcc, callback, Input, Output
import dash_bootstrap_components as dbc
import plotly.express as px

# Heroku PostgreSQL connection string
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"

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
    # SQL query that aggregates data from different categories
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

    conn = None
    try:
        # Establish a connection to PostgreSQL
        conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        # Load the result into a pandas DataFrame
        df = pd.read_sql_query(query, conn)

    except Exception as e:
        # Handle database connection/query errors gracefully
        if conn:
            conn.close()
        return px.bar(title=f"Error al cargar datos: {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

    # Handle empty datasets
    if df.empty:
        return px.bar(title="No hay datos disponibles para visualizar.")

    # Filter data based on the selected category
    if categoria != "Todas":
        df = df[df["categoria"] == categoria]

    # Aggregate total scores by team
    df_total = df.groupby("equipo", as_index=False)["puntaje"].sum()

    # Define color mapping for each team
    color_map = {
        "Rojo": "#e74c3c",
        "Azul": "#3498db",
        "Verde": "#27ae60",
        "Amarillo": "#f1c40f"
    }

    # Create the bar chart
    fig = px.bar(
        df_total,
        x="equipo",
        y="puntaje",
        title=f"Puntaje por Equipo - {categoria if categoria != 'Todas' else 'Total'}",
        text_auto=True,
        color="equipo",
        color_discrete_map=color_map
    )

    # Customize chart layout
    fig.update_layout(yaxis_title="Puntaje Total", xaxis_title="Equipo")

    return fig