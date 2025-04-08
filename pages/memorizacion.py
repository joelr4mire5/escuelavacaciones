import dash
import psycopg2  # PostgreSQL library
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/memorizacion")

# Connection string for Heroku PostgreSQL
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"

DIAS = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]
layout = dbc.Container([
    html.H2("Registro de Memorización", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(id="equipo-mem", placeholder="Seleccione un equipo")
        ], md=4),
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="estudiante-mem", placeholder="Seleccione un estudiante")
        ], md=4),
        dbc.Col([
            dbc.Label("Tipo"),
            dcc.Dropdown(
                id="tipo-cita-mem",
                options=[
                    {"label": "Versículo", "value": "Versículo"},
                    {"label": "Capítulo", "value": "Capítulo"}
                ],
                placeholder="Seleccione tipo"
            )
        ], md=4)
    ], className="mb-3"),

    html.Div(id="seccion-citas-mem"),
    html.Div(id="mensaje-mem", className="text-success mt-3"),
    html.Hr(),
    html.Div(id="tabla-citas-completadas")
])

# Helper function to get a database connection
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


@callback(
    Output("estudiante-mem", "options"),
    Input("estudiante-mem", "id")
)
def cargar_estudiantes(_):
    """Load the list of students from the database."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre FROM estudiantes ORDER BY nombre")
        estudiantes = cursor.fetchall()
        return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]
    finally:
        conn.close()


@callback(
    Output("tipo-cita-mem", "options"),
    Input("tipo-cita-mem", "id")
)
def cargar_tipos_cita(_):
    """Load the list of available cita types."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT tipo FROM citas ORDER BY tipo")
        tipos = cursor.fetchall()
        return [{"label": tipo[0], "value": tipo[0]} for tipo in tipos]
    finally:
        conn.close()


@callback(
    Output("dropdown-citas", "options"),
    Input("tipo-cita-mem", "value")
)
def cargar_citas_por_tipo(tipo):
    """Load the citas by their type."""
    if not tipo:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, cita FROM citas WHERE tipo = %s ORDER BY cita", (tipo,))
        citas = cursor.fetchall()
        return [{"label": cita[1], "value": cita[0]} for cita in citas]
    finally:
        conn.close()


@callback(
    Output("mensaje-mem", "children"),
    Output("tabla-citas-completadas", "children"),
    Input("btn-guardar-mem", "n_clicks"),
    State("estudiante-mem", "value"),
    State("dropdown-citas", "value"),
    State("tipo-cita-mem", "value"),
    prevent_initial_call=True
)
def guardar_memorizacion(n, estudiante_id, seleccionados, tipo):
    """Save or update student's completed citas."""
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Get all cita IDs for the selected type
        cursor.execute("SELECT id FROM citas WHERE tipo = %s", (tipo,))
        todos = [row[0] for row in cursor.fetchall()]

        # Insert or delete cita records for the student based on selection
        for cita_id in todos:
            if cita_id in seleccionados:
                # Check if the record already exists in `citas_completadas`
                cursor.execute(
                    "SELECT COUNT(*) FROM citas_completadas WHERE estudiante_id = %s AND cita_id = %s",
                    (estudiante_id, cita_id)
                )
                exists = cursor.fetchone()[0]
                if exists:
                    continue  # Skip if already exists
                cursor.execute("""
                    INSERT INTO citas_completadas (estudiante_id, cita_id, completado)
                    VALUES (%s, %s, 1)
                """, (estudiante_id, cita_id))
            else:
                # Remove from `citas_completadas` if not selected
                cursor.execute(
                    "DELETE FROM citas_completadas WHERE estudiante_id = %s AND cita_id = %s",
                    (estudiante_id, cita_id)
                )

        # Commit the changes
        conn.commit()

        # Fetch updated completed citas
        cursor.execute("""
            SELECT c.tipo, c.cita, c.puntaje
            FROM citas_completadas cc
            JOIN citas c ON cc.cita_id = c.id
            WHERE cc.estudiante_id = %s
        """, (estudiante_id,))
        rows = cursor.fetchall()

        # Build the output table
        if not rows:
            tabla = html.P("No hay citas completadas.")
        else:
            total = sum(r[2] for r in rows)  # Sum up the puntajes
            tabla = html.Div([
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Tipo"), html.Th("Cita"), html.Th("Puntaje")])),
                    html.Tbody([
                        html.Tr([html.Td(r[0]), html.Td(r[1]), html.Td(r[2])]) for r in rows
                    ])
                ], bordered=True, hover=True, responsive=True),
                html.P(f"Puntaje total: {total} puntos", className="fw-bold mt-2")
            ])

        return "Citas actualizadas correctamente.", tabla

    finally:
        # Close the database connection
        conn.close()