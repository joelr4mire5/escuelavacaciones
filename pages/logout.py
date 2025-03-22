import dash
dash.register_page(__name__, path="/logout")

from dash import html
from flask import session

layout = html.Div([
    html.H3("Sesión cerrada. Redirigiendo al login...")
])

# Cerrar sesión al cargar la página
def _logout_session():
    session.pop("user", None)

_logout_session()
