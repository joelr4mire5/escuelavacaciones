# navbar.py

from dash import html, dcc
import dash_bootstrap_components as dbc

navbar = dbc.Navbar(
    dbc.Container([
        html.Div([
            html.Span("Escuela Bíblica", className="navbar-brand medieval-title"),
        ], className="d-flex align-items-center"),

        dbc.Nav([
            dbc.NavItem(dcc.Link("🏰 Inicio", href="/", className="nav-link medieval-link")),
            dbc.NavItem(dcc.Link("📜 Registro Estudiantes", href="/registro-estudiantes", className="nav-link medieval-link")),
            dbc.NavItem(dcc.Link("📖 Registro de Puntajes", href="/registro-puntajes", className="nav-link medieval-link")),
            dbc.NavItem(dcc.Link("🔍 Análisis de Datos", href="/analisis-datos", className="nav-link medieval-link")),
            dbc.NavItem(dcc.Link("🛒 Tienda", href="/tienda", className="nav-link medieval-link")),
            dbc.NavItem(dcc.Link("📚 Agregar Citas", href="/versiculos", className="nav-link medieval-link")),
            dbc.NavItem(dcc.Link("🚪 Cerrar Sesión", href="/logout", className="nav-link text-danger")),
        ], className="ms-auto", navbar=True)
    ]),
    color="#4B2E2B",
    dark=True,
    className="mb-4 medieval-navbar"
)

