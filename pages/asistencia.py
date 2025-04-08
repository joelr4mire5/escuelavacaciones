import dash
from dash import Dash, html, dcc, Input, Output, State
import dash_bootstrap_components as dbc
import psycopg2
from dash.dependencies import ALL

dash.register_page(__name__, path="/asistencia")

# Mock Days
DIAS = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]

# Connection URL for Heroku PostgreSQL (just for illustration)
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"


def get_db_connection():
    """Reusable function to handle PostgreSQL connections."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')


layout = dbc.Container([
    html.H2("Registro de Asistencia y Puntualidad", className="my-4"),

    # --- Filters ---
    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(id="equipo-filtro", placeholder="Seleccione un equipo")
        ], md=6),
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="estudiante-filtro", placeholder="Seleccione un estudiante")
        ], md=6),
    ], className="mb-4"),

    # --- Where we show the checklists and "Guardar" button ---
    html.Div(id="lista-asistencia"),

    html.Hr(),
    # --- Where we show the summary table ---
    html.Div(id="tabla-resumen-asistencia")
])


# ------------------------------------------------------------------------------
# 1) Callback to load equipos (unique Output: "equipo-filtro.options")
# ------------------------------------------------------------------------------
@dash.callback(
    Output("equipo-filtro", "options"),
    Input("equipo-filtro", "id")  # <== Could also be a dummy input, see note below
)
def cargar_equipos(_):
    """
    Loads the distinct 'equipos' from the DB.
    We use 'Input("equipo-filtro", "id")' as a trivial trigger so it executes once.
    Alternatively, you could use Input("url", "pathname") or a dummy Interval component.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
    equipos = cursor.fetchall()
    conn.close()

    return [
        {"label": e[0], "value": e[0]}
        for e in equipos
        if e[0] is not None
    ]


# ------------------------------------------------------------------------------
# 2) Callback to load estudiantes given equipo (unique Output: "estudiante-filtro.options")
# ------------------------------------------------------------------------------
@dash.callback(
    Output("estudiante-filtro", "options"),
    Input("equipo-filtro", "value")
)
def cargar_estudiantes_por_equipo(equipo):
    if not equipo:
        return []
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, nombre FROM estudiantes WHERE equipo = %s ORDER BY nombre",
        (equipo,)
    )
    estudiantes = cursor.fetchall()
    conn.close()
    return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]


# ------------------------------------------------------------------------------
# 3) Callback to display the checklists for Asistencia/Puntualidad
#    (unique Output: "lista-asistencia.children")
# ------------------------------------------------------------------------------
@dash.callback(
    Output("lista-asistencia", "children"),
    Input("estudiante-filtro", "value")
)
def mostrar_asistencia_estudiante(estudiante_id):
    if not estudiante_id:
        return html.P("Seleccione un estudiante para registrar asistencia.")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get the name of the student
    cursor.execute("SELECT nombre FROM estudiantes WHERE id = %s", (estudiante_id,))
    row = cursor.fetchone()
    nombre = row[0] if row else "(Desconocido)"

    # Get existing attendance
    cursor.execute(
        "SELECT dia, presente, puntual FROM asistencia WHERE estudiante_id = %s",
        (estudiante_id,)
    )
    registros = cursor.fetchall()
    conn.close()

    # Extract which days are present/puntual
    dias_asistencia = [r[0] for r in registros if r[1] == 1]
    dias_puntualidad = [r[0] for r in registros if r[2] == 1]

    return html.Div([
        html.H5(nombre),

        dbc.Row([
            dbc.Col([
                html.Label("Asistencia"),
                dcc.Checklist(
                    id={"type": "asistencia", "estudiante": estudiante_id},
                    options=[
                        {"label": d, "value": i}
                        for i, d in enumerate(DIAS)
                    ],
                    value=dias_asistencia,
                    inline=True
                )
            ], md=6),

            dbc.Col([
                html.Label("Puntualidad"),
                dcc.Checklist(
                    id={"type": "puntualidad", "estudiante": estudiante_id},
                    options=[
                        {"label": d, "value": i}
                        for i, d in enumerate(DIAS)
                    ],
                    value=dias_puntualidad,
                    inline=True
                )
            ], md=6),
        ]),

        html.Hr(),
        dbc.Button(
            "Guardar Asistencia",
            id="guardar-asistencia",
            color="primary",
            className="mt-3"
        ),
        # We'll show a success or error message here
        html.Div(id="mensaje-asistencia", className="text-success mt-2"),
    ])


# ------------------------------------------------------------------------------
# 4) Callback to handle the "Guardar Asistencia" button
#    (unique Outputs: "mensaje-asistencia.children" & "tabla-resumen-asistencia.children")
# ------------------------------------------------------------------------------
@dash.callback(
    Output("mensaje-asistencia", "children"),
    Output("tabla-resumen-asistencia", "children"),
    Input("guardar-asistencia", "n_clicks"),
    State("estudiante-filtro", "value"),
    State({"type": "asistencia", "estudiante": ALL}, "value"),
    State({"type": "puntualidad", "estudiante": ALL}, "value"),
    State({"type": "asistencia", "estudiante": ALL}, "id"),
    prevent_initial_call=True
)
def guardar_asistencia(n, estudiante_id, lista_asistencia, lista_puntualidad, ids):
    # Safeguard in case no student selected
    if not estudiante_id:
        return (
            "Error: Debe seleccionar un estudiante antes de guardar.",
            dash.no_update
        )

    conn = get_db_connection()
    cursor = conn.cursor()

    # Iterate over each set of checklist values (since we used pattern-matching)
    for i, estado_asistencia in enumerate(lista_asistencia):
        e_id = ids[i]["estudiante"]
        estado_puntualidad = lista_puntualidad[i]

        for dia in range(len(DIAS)):
            presente = (dia in estado_asistencia)
            puntual = (dia in estado_puntualidad)

            if puntual and not presente:
                conn.close()
                return (
                    f"Error: No se puede marcar puntualidad en {DIAS[dia]} sin asistencia.",
                    dash.no_update
                )

            cursor.execute("""
                INSERT INTO asistencia (estudiante_id, dia, presente, puntual, 
                                        puntaje_asistencia, puntaje_puntual)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT(estudiante_id, dia) 
                DO UPDATE SET 
                  presente=excluded.presente,
                  puntual=excluded.puntual,
                  puntaje_asistencia=excluded.puntaje_asistencia,
                  puntaje_puntual=excluded.puntaje_puntual
            """, (
                e_id,
                dia,
                int(presente),
                int(puntual),
                2 if presente else 0,
                2 if puntual else 0
            ))

    conn.commit()

    # Build the summary table
    cursor.execute("""
        SELECT SUM(puntaje_asistencia), SUM(puntaje_puntual)
        FROM asistencia
        WHERE estudiante_id = %s
    """, (estudiante_id,))
    resumen = cursor.fetchone()
    conn.close()

    total_asistencia = resumen[0] or 0
    total_puntualidad = resumen[1] or 0

    tabla = dbc.Table(
        [
            html.Thead(
                html.Tr([html.Th("Total Asistencia"), html.Th("Total Puntualidad")])
            ),
            html.Tbody(
                html.Tr([html.Td(total_asistencia), html.Td(total_puntualidad)])
            ),
        ],
        bordered=True, hover=True, responsive=True
    )

    return "Datos guardados correctamente.", tabla
