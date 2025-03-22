# pages/inicio.py

import dash
dash.register_page(__name__, path="/")

from dash import html
import dash_bootstrap_components as dbc

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(
                src="/assets/inicio_imagen.webp",
                style={"width": "100%", "maxWidth": "700px", "borderRadius": "20px", "boxShadow": "0 0 15px rgba(0,0,0,0.2)"}
            ),
            html.H2("¡Bienvenido al Reino de la Verdad!", className="text-center mt-4"),
            html.P(
                "Aquí comienza la aventura real de nuestra Escuela Bíblica de Vacaciones.",
                className="lead text-center"
            ),
            html.P(
                "Los estudiantes ganan coronas a través de buenas acciones, memorización de versículos, puntualidad y trabajo en equipo. ¡Construyamos juntos este castillo espiritual!",
                className="text-center"
            )
        ], width=12)
    ], justify="center", className="mt-5")
])
