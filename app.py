import dash
from dash import html, dcc, Input, Output
import dash_bootstrap_components as dbc
from auth import validate_login
from flask import Flask, session
import os
from assets.navbar import navbar  # 👈 importa navbar

server = Flask(__name__)
server.secret_key = os.getenv('SECRET_KEY', 'supersecretkey')

app = dash.Dash(
    __name__,
    server=server,
    use_pages=True,
    suppress_callback_exceptions=True,
    external_stylesheets=[dbc.themes.BOOTSTRAP]
)

app.layout = html.Div([
    dcc.Location(id='url'),
    html.Div(id='page-content')
])

@app.callback(
    Output('page-content', 'children'),
    Input('url', 'pathname')
)
def display_page(pathname):
    if session.get('user') is None and pathname != "/login":
        return dash.page_registry['login']['layout']

    layout = [
        navbar,  # 👈 muestra navbar solo si hay sesión
        dash.page_container
    ]
    return layout

if __name__ == '__main__':
    app.run(debug=True)
