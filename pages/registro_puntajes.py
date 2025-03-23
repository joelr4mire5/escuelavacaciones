# pages/registro_puntajes.py

import dash
from dash import html, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/registro-puntajes")

layout = dbc.Container([
    html.H2("Registro de Puntajes", className="my-4"),

    html.P("Seleccione la categoría de registro de puntajes:"),

    dbc.Row([
        dbc.Col(dbc.Button("Asistencia", href="/asistencia", color="primary", className="w-100 mb-2"), md=4),
        dbc.Col(dbc.Button("Materiales", href="/materiales", color="success", className="w-100 mb-2"), md=4),
        dbc.Col(dbc.Button("Memorización", href="/memorizacion", color="warning", className="w-100 mb-2"), md=4),
        dbc.Col(dbc.Button("Visitas", href="/visitas", color="warning", className="w-100 mb-2"), md=4),
    ], className="mt-3")
])
