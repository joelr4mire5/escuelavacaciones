import dash
import psycopg2  # PostgreSQL library for database interaction
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/registro_estudiantes")

# Connection URL for Heroku PostgreSQL
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"

layout = dbc.Container([
    html.H2("Registro de Estudiantes", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Nombre del estudiante"),
            dbc.Input(id="nombre-estudiante", placeholder="Ingrese el nombre del estudiante")
        ], md=6),
        dbc.Col([
            dbc.Label("Equipo"),
            dbc.Input(id="equipo-estudiante", placeholder="Ingrese el equipo del estudiante")
        ], md=6)
    ], className="mb-4"),

    dbc.Button("Registrar", id="btn-registrar", color="primary", className="mt-3"),

    html.Div(id="mensaje-registro", className="text-success mt-3"),

    html.Hr(),

    html.Div(id="tabla-estudiantes", className="mt-4")
])


# Helper function to get a database connection
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')


@callback(
    Output("mensaje-registro", "children"),
    Output("tabla-estudiantes", "children"),
    Input("btn-registrar", "n_clicks"),
    State("nombre-estudiante", "value"),
    State("equipo-estudiante", "value"),
    prevent_initial_call=True
)
def registrar_estudiante(n, nombre, equipo):
    """Registers a new student in the database."""
    if not nombre or not equipo:
        return "Por favor, ingrese toda la información requerida.", None

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Insert new student into the database
        cursor.execute("""
            INSERT INTO estudiantes (nombre, equipo)
            VALUES (%s, %s)
        """, (nombre, equipo))
        conn.commit()

        # Fetch the updated list of students
        cursor.execute("SELECT id, nombre, equipo FROM estudiantes ORDER BY nombre")
        estudiantes = cursor.fetchall()

        # Build the students' table
        tabla = dbc.Table([
            html.Thead(html.Tr([html.Th("ID"), html.Th("Nombre"), html.Th("Equipo")])),
            html.Tbody([
                html.Tr([html.Td(e[0]), html.Td(e[1]), html.Td(e[2])]) for e in estudiantes
            ])
        ], bordered=True, hover=True, responsive=True)

        return "Estudiante registrado correctamente.", tabla

    except psycopg2.Error as e:
        return f"Error al registrar al estudiante: {str(e)}", None

    finally:
        # Always close the database connection
        conn.close()


@callback(
    Output("tabla-estudiantes", "children"),
    Input("tabla-estudiantes", "id"),
    prevent_initial_call=False
)
def cargar_estudiantes(_):
    """Fetches and displays the list of students from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, nombre, equipo FROM estudiantes ORDER BY nombre")
        estudiantes = cursor.fetchall()

        # Build the students' table
        if not estudiantes:
            return html.P("No hay estudiantes registrados.")

        tabla = dbc.Table([
            html.Thead(html.Tr([html.Th("ID"), html.Th("Nombre"), html.Th("Equipo")])),
            html.Tbody([
                html.Tr([html.Td(e[0]), html.Td(e[1]), html.Td(e[2])]) for e in estudiantes
            ])
        ], bordered=True, hover=True, responsive=True)

        return tabla

    finally:
        # Always close the database connection
        conn.close()