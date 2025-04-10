# pages/analisis_datos.py

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/analisis-datos")

layout = dbc.Container([
    html.H2("Analsisis de Datos", className="my-4"),

    html.P("Seleccione uno de los siguientes dashboards"),

    dbc.Row([
        dbc.Col(dbc.Button("Visualizaciones por Equipos", href="/visualizacion-equipo", color="primary", className="w-100 mb-2"), md=4),
        dbc.Col(dbc.Button("Visualizaciones por Estudiante", href="/visualizacion-estudiantes", color="success", className="w-100 mb-2"), md=4)
    ], className="mt-3")
])
