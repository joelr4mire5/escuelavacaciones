import dash
import psycopg2  # PostgreSQL library
from dash import html, dcc, Input, Output, State, callback
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/memorizacion")

# Conexión a la base de datos (Heroku PostgreSQL)
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"

# Layout de la página de registro de memorización
layout = dbc.Container([
    html.H2("Registro de Memorización", className="my-4"),

    # Selección de equipo, estudiante y tipo de cita
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

    # Sección donde se mostrarán las citas disponibles para selección
    html.Div(id="seccion-citas-mem"),

    # Botón para guardar cambios
    dbc.Button("Guardar Progreso", id="btn-guardar-mem", color="primary", className="mt-3"),

    # Mensaje de confirmación / error
    html.Div(id="mensaje-mem", className="text-success mt-3"),

    # Divider y tabla de reportes
    html.Hr(),
    html.Div(id="tabla-citas-completadas")
])


# Función auxiliar para realizar la conexión a la base de datos
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


# Callback para cargar la lista de equipos
@callback(
    Output("equipo-mem", "options"),
    Input("equipo-mem", "id")
)
def cargar_equipos(_):
    """Carga la lista de equipos desde la base de datos."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT(equipo) FROM estudiantes ORDER BY equipo")
        equipos = cursor.fetchall()
        return [{"label": equipo, "value": equipo} for (equipo,) in equipos]
    finally:
        conn.close()


# Callback para cargar los estudiantes del equipo seleccionado
@callback(
    Output("estudiante-mem", "options"),
    Input("equipo-mem", "value")
)
def cargar_estudiantes_por_equipo(equipo):
    """Carga los estudiantes que pertenecen al equipo seleccionado."""
    if not equipo:
        return []

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, nombre FROM estudiantes WHERE equipo = %s ORDER BY nombre", (equipo,))
        estudiantes = cursor.fetchall()
        return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]
    finally:
        conn.close()


# Callback para mostrar las citas según la clase del estudiante
@callback(
    Output("seccion-citas-mem", "children"),
    [Input("estudiante-mem", "value"), Input("tipo-cita-mem", "value")]
)
def mostrar_citas(estudiante_id, tipo):
    """Muestra las citas según la clase del estudiante (determinada por su edad)."""
    if not estudiante_id or not tipo:
        return ""

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Obtener la edad del estudiante desde la base de datos
        cursor.execute("SELECT edad FROM estudiantes WHERE id = %s", (estudiante_id,))
        resultado = cursor.fetchone()
        if not resultado:
            return html.P("No se encontró información del estudiante seleccionado.", className="text-danger")

        edad = resultado[0]

        # Determinar la clase del estudiante según su edad
        if 0 <= edad < 4:
            clase = "0-3"
        elif 4 <= edad < 6:
            clase = "4-5"
        elif 6 <= edad < 9:
            clase = "6-8"
        elif 9 <= edad < 12:
            clase = "9-11"
        else:
            clase = "12+"

        # Consultar las citas según la clase y el tipo
        cursor.execute("SELECT id, cita FROM citas WHERE clase = %s AND tipo = %s ORDER BY cita", (clase, tipo))
        citas = cursor.fetchall()

        if not citas:
            return html.P("No hay citas disponibles para la clase del estudiante.", className="text-warning")

        # Opciones de citas para el checklist
        opciones = [{"label": cita, "value": id_} for id_, cita in citas]

        # Componente Checklist para marcar como completadas las citas
        return dcc.Checklist(
            id="dropdown-citas",
            options=opciones,
            value=[],  # Aquí se cargarán posibles citas ya completadas del estudiante
            labelStyle={"display": "block"}
        )
    finally:
        conn.close()


# Callback para guardar las citas completadas en la base de datos
@callback(
    Output("mensaje-mem", "children"),
    Output("tabla-citas-completadas", "children"),
    Input("btn-guardar-mem", "n_clicks"),
    State("estudiante-mem", "value"),
    State("dropdown-citas", "value"),
    prevent_initial_call=True
)
def guardar_citas_completadas(n_clicks, estudiante_id, seleccionados):
    """Guarda el progreso del estudiante actualizando la base de datos."""
    if not estudiante_id or seleccionados is None:
        return "Por favor, seleccione un estudiante y las citas completadas.", None

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Eliminar citas previamente guardadas para este estudiante
        cursor.execute("DELETE FROM citas_completadas WHERE estudiante_id = %s", (estudiante_id,))
        # Insertar las citas seleccionadas como completadas
        for cita_id in seleccionados:
            cursor.execute("""
                INSERT INTO citas_completadas (estudiante_id, cita_id, completado) VALUES (%s, %s, 1)
            """, (estudiante_id, cita_id))
        conn.commit()

        # Consultar progreso actualizado
        cursor.execute("""
            SELECT c.tipo, c.cita, c.puntaje
            FROM citas_completadas cc
            JOIN citas c ON cc.cita_id = c.id
            WHERE cc.estudiante_id = %s
        """, (estudiante_id,))
        rows = cursor.fetchall()

        if not rows:
            tabla = html.P("No hay citas completadas.")
        else:
            total = sum(r[2] for r in rows)
            tabla = html.Div([
                dbc.Table([
                    html.Thead(html.Tr([html.Th("Tipo"), html.Th("Cita"), html.Th("Puntaje")])),
                    html.Tbody([html.Tr([html.Td(r[0]), html.Td(r[1]), html.Td(r[2])]) for r in rows])
                ], bordered=True, hover=True, responsive=True),
                html.P(f"Puntaje total: {total} puntos", className="fw-bold mt-2")
            ])

        return "Progreso guardado correctamente.", tabla

    finally:
        conn.close()