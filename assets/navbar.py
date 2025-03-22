# navbar.py

from dash import html, dcc
import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Inicio", href="/", className="nav-link")),
        dbc.NavItem(dcc.Link("Estudiantes", href="/registro-estudiantes", className="nav-link")),
        dbc.NavItem(dcc.Link("Puntajes", href="/registro-puntajes", className="nav-link")),
        dbc.NavItem(dcc.Link("Equipos", href="/visualizacion-equipos", className="nav-link")),
        dbc.NavItem(dcc.Link("Estudiantes (Stats)", href="/visualizacion-estudiantes", className="nav-link")),
        dbc.NavItem(dcc.Link("Tienda", href="/tienda", className="nav-link")),
        dbc.NavItem(dcc.Link("Cerrar sesión", href="/logout", className="nav-link text-danger")),
    ],
    brand="Escuela Bíblica",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"
)
