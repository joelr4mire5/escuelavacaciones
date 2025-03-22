# pages/logout.py

import dash
dash.register_page(__name__, path="/logout")

from dash import html, dcc, callback, Output, Input
from flask import session

layout = html.Div([
    dcc.Location(id="url-logout", refresh=True),
    html.H3("Cerrando sesión..."),
    html.Div(id="logout-redirect")
])

@callback(
    Output("logout-redirect", "children"),
    Input("url-logout", "pathname"),
    prevent_initial_call=False
)
def logout_user(_):
    session.pop("user", None)
    return dcc.Location(href="/login", id="redirect-login")
