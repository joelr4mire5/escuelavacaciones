import dash
import psycopg2
from psycopg2.extras import RealDictCursor
from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
from dash.dependencies import ALL
import os  # Para acceder a DATABASE_URL

# Obtener la URL de conexión desde las variables de entorno de Heroku
DATABASE_URL = os.getenv("postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub")

dash.register_page(__name__, path="/materiales")

DIAS = ["Día 1", "Día 2", "Día 3", "Día 4", "Día 5"]

layout = dbc.Container([
    html.H2("Registro de Materiales (Biblia y Folder)", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(id="equipo-materiales", placeholder="Seleccione un equipo")
        ], md=6),
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="estudiante-materiales", placeholder="Seleccione un estudiante")
        ], md=6),
    ], className="mb-4"),

    html.Div(id="seccion-materiales"),
    html.Hr(),
    html.Div(id="resumen-materiales")
])


def get_connection():
    """Establece una conexión a la base de datos de PostgreSQL."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@callback(
    Output("equipo-materiales", "options"),
    Input("equipo-materiales", "id")
)
def cargar_equipos_materiales(_):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
            equipos = cursor.fetchall()
        return [{"label": e[0], "value": e[0]} for e in equipos]
    finally:
        conn.close()


@callback(
    Output("estudiante-materiales", "options"),
    Input("equipo-materiales", "value")
)
def cargar_estudiantes_materiales(equipo):
    if not equipo:
        return []
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, nombre FROM estudiantes WHERE equipo = %s ORDER BY nombre", (equipo,))
            estudiantes = cursor.fetchall()
        return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]
    finally:
        conn.close()


@callback(
    Output("seccion-materiales", "children"),
    Input("estudiante-materiales", "value")
)
def mostrar_checkboxes_materiales(estudiante_id):
    if not estudiante_id:
        return html.P("Seleccione un estudiante para registrar materiales.")

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT dia, biblia, folder, completo FROM materiales WHERE estudiante_id = %s",
                (estudiante_id,)
            )
            registros = cursor.fetchall()
    finally:
        conn.close()

    biblia_dias = [r[0] for r in registros if r[1]]
    folder_dias = [r[0] for r in registros if r[2]]
    completo = any(r[3] for r in registros)

    return html.Div([
        dbc.Row([
            dbc.Col([
                dbc.Label("Biblia"),
                dcc.Checklist(
                    id={"type": "biblia", "estudiante": estudiante_id},
                    options=[{"label": d, "value": i} for i, d in enumerate(DIAS)],
                    value=biblia_dias,
                    inline=True
                )
            ], md=6),
            dbc.Col([
                dbc.Label("Folder"),
                dcc.Checklist(
                    id={"type": "folder", "estudiante": estudiante_id},
                    options=[{"label": d, "value": i} for i, d in enumerate(DIAS)],
                    value=folder_dias,
                    inline=True
                )
            ], md=6)
        ]),
        dbc.Checkbox(
            id={"type": "completo", "estudiante": estudiante_id},
            value=completo,
            label="Folder completo",
            className="mt-3"
        ),
        dbc.Button("Guardar Materiales", id="guardar-materiales", color="primary", className="mt-3"),
        html.Div(id="mensaje-materiales", className="text-success mt-2")
    ])


@callback(
    Output("mensaje-materiales", "children"),
    Output("resumen-materiales", "children"),
    Input("guardar-materiales", "n_clicks"),
    State("estudiante-materiales", "value"),
    State({"type": "biblia", "estudiante": ALL}, "value"),
    State({"type": "folder", "estudiante": ALL}, "value"),
    State({"type": "completo", "estudiante": ALL}, "value"),
    State({"type": "biblia", "estudiante": ALL}, "id"),
    prevent_initial_call=True
)
def guardar_materiales(n, estudiante_id, biblia_val, folder_val, completo_val, ids):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            for i, biblia_dias in enumerate(biblia_val):
                folder_dias = folder_val[i]
                completo = completo_val[i]
                estudiante = ids[i]["estudiante"]

                for dia in range(len(DIAS)):
                    tiene_biblia = dia in biblia_dias
                    tiene_folder = dia in folder_dias

                    puntos_biblia = 5 if tiene_biblia else 0
                    puntos_folder = 1 if tiene_folder else 0
                    puntos_completo = 2 if completo and all(d in folder_dias for d in range(len(DIAS))) else 0

                    # Actualización o inserción con PostgreSQL
                    cursor.execute("""
                        INSERT INTO materiales (estudiante_id, dia, biblia, folder, completo, puntos_biblia, puntos_folder, puntos_completo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (estudiante_id, dia) DO UPDATE SET
                            biblia = EXCLUDED.biblia,
                            folder = EXCLUDED.folder,
                            completo = EXCLUDED.completo,
                            puntos_biblia = EXCLUDED.puntos_biblia,
                            puntos_folder = EXCLUDED.puntos_folder,
                            puntos_completo = EXCLUDED.puntos_completo
                    """, (
                        estudiante, dia, tiene_biblia, tiene_folder, completo, puntos_biblia, puntos_folder,
                        puntos_completo
                    ))

            conn.commit()

            cursor.execute("""
                SELECT SUM(puntos_biblia), SUM(puntos_folder), SUM(puntos_completo)
                FROM materiales
                WHERE estudiante_id = %s
            """, (estudiante_id,))
            resumen = cursor.fetchone()
    finally:
        conn.close()

    tabla = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Biblia"), html.Th("Folder"), html.Th("Folder Completo")
        ])),
        html.Tbody([
            html.Tr([html.Td(resumen[0] or 0), html.Td(resumen[1] or 0), html.Td(resumen[2] or 0)])
        ])
    ], bordered=True, hover=True, responsive=True)

    return "Datos de materiales guardados correctamente.", tabla