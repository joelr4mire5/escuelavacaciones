# navbar.py

from dash import html, dcc
import dash_bootstrap_components as dbc

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dcc.Link("Inicio", href="/", className="nav-link")),
        dbc.NavItem(dcc.Link("Registro Estudiantes", href="/registro-estudiantes", className="nav-link")),
        dbc.NavItem(dcc.Link("Registro de Puntajes", href="/registro-puntajes", className="nav-link")),
        dbc.NavItem(dcc.Link("Analisis de datos", href="/analisis-datos", className="nav-link")),
        dbc.NavItem(dcc.Link("Tienda", href="/tienda", className="nav-link")),
        dbc.NavItem(dcc.Link("Agregar citas", href="/versiculos", className="nav-link")),
        dbc.NavItem(dcc.Link("Cerrar sesión", href="/logout", className="nav-link text-danger")),
    ],
    brand="Escuela Bíblica",
    brand_href="/",
    color="primary",
    dark=True,
    className="mb-4"
)
