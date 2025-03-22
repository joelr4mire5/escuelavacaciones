import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from auth import validate_login
from flask import Flask, session
import os
from assets.navbar import navbar  # 👈 importa navbar
from database import init_db

# Inicializar base de datos
init_db()

# Servidor Flask
server = Flask(__name__)
server.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

# App Dash con soporte de páginas
app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

# Layout principal
app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div(id='page-content')
])

# Callback para cargar la página actual
@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if session.get('user') is None and pathname != "/login":
        # ✅ Buscar la página de login por su path
        for page in dash.page_registry.values():
            if page["path"] == "/login":
                return page["layout"]
        return html.Div("Error: No se encontró la página de login.")

    # Usuario autenticado o ya en /login
    return html.Div([
        navbar,
        dash.page_container
    ])

# Ejecutar app
if __name__ == '__main__':
    app.run(debug=True)
