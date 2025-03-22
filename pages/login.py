# pages/login.py

import dash
dash.register_page(__name__, path="/login")

from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc
from auth import validate_login
from flask import session

layout = html.Div([
    dbc.Container([
        html.H2("Iniciar Sesión - Escuela Bíblica"),
        dbc.Input(id="username", placeholder="Usuario", type="text", className="mb-2"),
        dbc.Input(id="password", placeholder="Contraseña", type="password", className="mb-2"),
        dbc.Button("Entrar", id="login-button", color="primary", className="mb-2"),
        html.Div(id="login-message", className="text-danger")
    ], className="mt-5", style={"maxWidth": "400px"})
])

@callback(
    Output("login-message", "children"),
    Input("login-button", "n_clicks"),
    State("username", "value"),
    State("password", "value"),
    prevent_initial_call=True
)
def handle_login(n_clicks, username, password):
    if validate_login(username, password):
        session['user'] = username
        return dcc.Location(href="/", id="redirect-login")
    else:
        return "Usuario o contraseña incorrectos."