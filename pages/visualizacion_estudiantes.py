import dash
import psycopg2  # PostgreSQL library
import datetime
from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
from dash.dependencies import ALL

dash.register_page(__name__, path="/isualizacion-estudiantes")

DIAS = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]

# Connection URL for Heroku PostgreSQL
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"


# Reusable function to handle PostgreSQL connections
def get_db_connection():
    return psycopg2.connect(DATABASE_URL, sslmode='require')


layout = dbc.Container([
    html.H2("Registro de Asistencia y Puntualidad", className="my-4"),

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

    html.Div(id="lista-asistencia"),
    html.Hr(),
    html.Div(id="tabla-resumen-asistencia")
])


@callback(
    Output("equipo-filtro", "options"),
    Input("equipo-filtro", "id")
)
def cargar_equipos(_):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
        equipos = cursor.fetchall()
        return [{"label": e[0], "value": e[0]} for e in equipos]
    finally:
        conn.close()


@callback(
    Output("estudiante-filtro", "options"),
    Input("equipo-filtro", "value")
)
def cargar_estudiantes_por_equipo(equipo):
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


@callback(
    Output("lista-asistencia", "children"),
    Input("estudiante-filtro", "value")
)
def mostrar_asistencia_estudiante(estudiante_id):
    if not estudiante_id:
        return html.P("Seleccione un estudiante para registrar asistencia.")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nombre FROM estudiantes WHERE id = %s", (estudiante_id,))
        nombre = cursor.fetchone()[0]

        cursor.execute("SELECT dia, presente, puntual FROM asistencia WHERE estudiante_id = %s", (estudiante_id,))
        registros = cursor.fetchall()

        dias_asistencia = [r[0] for r in registros if r[1] == 1]
        dias_puntualidad = [r[0] for r in registros if r[2] == 1]

        return html.Div([
            html.H5(nombre),
            dbc.Row([
                dbc.Col([
                    html.Label("Asistencia"),
                    dcc.Checklist(
                        id={"type": "asistencia", "estudiante": estudiante_id},
                        options=[{"label": d, "value": i} for i, d in enumerate(DIAS)],
                        value=dias_asistencia,
                        inline=True
                    )
                ], md=6),
                dbc.Col([
                    html.Label("Puntualidad"),
                    dcc.Checklist(
                        id={"type": "puntualidad", "estudiante": estudiante_id},
                        options=[{"label": d, "value": i} for i, d in enumerate(DIAS)],
                        value=dias_puntualidad,
                        inline=True
                    )
                ], md=6)
            ]),
            html.Hr(),
            dbc.Button("Guardar Asistencia", id="guardar-asistencia", color="primary", className="mt-3"),
            html.Div(id="mensaje-asistencia", className="text-success mt-2")
        ])
    finally:
        conn.close()


@callback(
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
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Create asistencia table if it does not exist
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencia (
                estudiante_id INTEGER,
                dia INTEGER,
                presente INTEGER DEFAULT 0,
                puntual INTEGER DEFAULT 0,
                puntaje_asistencia INTEGER DEFAULT 0,
                puntaje_puntual INTEGER DEFAULT 0,
                PRIMARY KEY(estudiante_id, dia)
            )
        """)

        for i, estado_asistencia in enumerate(lista_asistencia):
            estudiante_id = ids[i]["estudiante"]
            estado_puntualidad = lista_puntualidad[i]

            for dia in range(len(DIAS)):
                presente = dia in estado_asistencia
                puntual = dia in estado_puntualidad

                if puntual and not presente:
                    return f"Error: No se puede marcar puntualidad en {DIAS[dia]} sin asistencia."

                cursor.execute("""
                    INSERT INTO asistencia (estudiante_id, dia, presente, puntual, puntaje_asistencia, puntaje_puntual)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT (estudiante_id, dia) DO UPDATE SET
                        presente = EXCLUDED.presente,
                        puntual = EXCLUDED.puntual,
                        puntaje_asistencia = EXCLUDED.puntaje_asistencia,
                        puntaje_puntual = EXCLUDED.puntaje_puntual
                """, (
                    estudiante_id,
                    dia,
                    int(presente),
                    int(puntual),
                    2 if presente else 0,
                    2 if puntual else 0
                ))

        conn.commit()
        cursor.execute("""
            SELECT SUM(puntaje_asistencia), SUM(puntaje_puntual)
            FROM asistencia
            WHERE estudiante_id = %s
        """, (estudiante_id,))
        resumen = cursor.fetchone()

        tabla = dbc.Table([
            html.Thead(html.Tr([html.Th("Total Asistencia"), html.Th("Total Puntualidad")])),
            html.Tbody([
                html.Tr([html.Td(resumen[0] or 0), html.Td(resumen[1] or 0)])
            ])
        ], bordered=True, hover=True, responsive=True)

        return "Datos guardados correctamente.", tabla
    finally:
        conn.close()