import dash

dash.register_page(__name__, path="/visitas")

from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
import psycopg2
import datetime

# Heroku PostgreSQL connection URL
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"

layout = dbc.Container([
    html.H2("Registro de Visitas", className="my-4"),

    dcc.Store(id="selected-visita-id", storage_type="session"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo del Invitador"),
            dcc.Dropdown(id="dropdown-equipo-visita", placeholder="Seleccione un equipo")
        ]),
        dbc.Col([
            dbc.Label("¿Quién lo invitó?"),
            dcc.Dropdown(id="dropdown-invitador-visita", placeholder="Seleccione al estudiante que invitó")
        ])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Nombre de la Visita"),
            dbc.Input(id="input-nombre-visita", type="text", placeholder="Ingrese el nombre")
        ]),
        dbc.Col([
            dbc.Label("¿Es adulto?"),
            dcc.Checklist(
                id="check-adulto-visita",
                options=[{"label": "Sí", "value": "adulto"}],
                value=[],
                inline=True
            )
        ])
    ], className="mb-3"),

    dbc.Button("Registrar", id="btn-registrar-visita", color="primary", className="mb-3"),
    html.Div(id="mensaje-visita", className="text-success"),

    html.Hr(),
    html.H4("Visitas Registradas"),
    html.Div(id="tabla-visitas")
])


# Helper function to establish a PostgreSQL database connection
def get_db_connection():
    """Establishes and returns a PostgreSQL database connection."""
    return psycopg2.connect(DATABASE_URL, sslmode='require')


# Cargar equipos
@callback(
    Output("dropdown-equipo-visita", "options"),
    Input("dropdown-equipo-visita", "id")
)
def cargar_equipos(_):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
    equipos = cursor.fetchall()
    conn.close()
    return [{"label": e[0], "value": e[0]} for e in equipos]


# Cargar estudiantes según equipo seleccionado
@callback(
    Output("dropdown-invitador-visita", "options"),
    Input("dropdown-equipo-visita", "value")
)
def filtrar_estudiantes_por_equipo(equipo):
    if not equipo:
        return []
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes WHERE equipo = %s ORDER BY nombre", (equipo,))
    estudiantes = cursor.fetchall()
    conn.close()
    return [{"label": nombre, "value": id_} for id_, nombre in estudiantes]


# Manejar crear, editar y eliminar
@callback(
    Output("mensaje-visita", "children"),
    Output("tabla-visitas", "children"),
    Output("input-nombre-visita", "value"),
    Output("check-adulto-visita", "value"),
    Output("dropdown-invitador-visita", "value"),
    Output("selected-visita-id", "data"),
    Output("btn-registrar-visita", "children"),
    Input("btn-registrar-visita", "n_clicks"),
    Input({"type": "btn-editar-visita", "index": dash.ALL}, "n_clicks"),
    Input({"type": "btn-eliminar-visita", "index": dash.ALL}, "n_clicks"),
    State("input-nombre-visita", "value"),
    State("check-adulto-visita", "value"),
    State("dropdown-invitador-visita", "value"),
    State("selected-visita-id", "data"),
    prevent_initial_call=True
)
def manejar_visita(n_reg, editar_clicks, eliminar_clicks, nombre, adulto_valor, invitador_id, visita_id):
    triggered_id = ctx.triggered_id
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # Eliminar visita
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-eliminar-visita":
            visita_id = triggered_id["index"]
            cursor.execute("DELETE FROM visitas WHERE id = %s", (visita_id,))
            conn.commit()
            return "Visita eliminada correctamente.", mostrar_visitas(cursor), "", [], None, None, "Registrar"

        # Editar visita (cargar datos)
        if isinstance(triggered_id, dict) and triggered_id.get("type") == "btn-editar-visita":
            visita_id = triggered_id["index"]
            cursor.execute("SELECT nombre, es_adulto, invitador_id FROM visitas WHERE id = %s", (visita_id,))
            row = cursor.fetchone()
            return "", mostrar_visitas(cursor), row[0], ["adulto"] if row[1] else [], row[2], visita_id, "Actualizar"

        # Validar input
        if not nombre or not invitador_id:
            return "Debe ingresar nombre e invitador.", mostrar_visitas(
                cursor), nombre, adulto_valor, invitador_id, visita_id, "Registrar"

        # Determinar si es adulto
        es_adulto = 1 if "adulto" in adulto_valor else 0
        puntaje = 6 if es_adulto else 4

        # Actualizar o Insertar
        if visita_id:
            cursor.execute("""
                UPDATE visitas
                SET nombre = %s, es_adulto = %s, invitador_id = %s, puntaje = %s
                WHERE id = %s
            """, (nombre.strip(), es_adulto, invitador_id, puntaje, visita_id))
            mensaje = "Visita actualizada correctamente."
        else:
            cursor.execute("""
                INSERT INTO visitas (nombre, es_adulto, invitador_id, puntaje)
                VALUES (%s, %s, %s, %s)
            """, (nombre.strip(), es_adulto, invitador_id, puntaje))
            mensaje = "Visita registrada correctamente."

        conn.commit()
        return mensaje, mostrar_visitas(cursor), "", [], None, None, "Registrar"

    finally:
        conn.close()


# Tabla de visitas registradas
def mostrar_visitas(cursor=None):
    if cursor is None:
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True
    else:
        close_conn = False

    cursor.execute("""
        SELECT v.id, v.nombre, v.es_adulto, v.puntaje, e.nombre
        FROM visitas v
        JOIN estudiantes e ON v.invitador_id = e.id
        ORDER BY v.nombre
    """)
    rows = cursor.fetchall()

    if close_conn:
        conn.close()

    if not rows:
        return html.P("No hay visitas registradas.")

    header = html.Thead(html.Tr([
        html.Th("Nombre"), html.Th("Adulto"), html.Th("Invitado por"), html.Th("Puntaje"), html.Th("Acciones")
    ]))
    body = html.Tbody([
        html.Tr([
            html.Td(r[1]),
            html.Td("Sí" if r[2] else "No"),
            html.Td(r[4]),
            html.Td(r[3]),
            html.Td([
                dbc.Button("Editar", id={"type": "btn-editar-visita", "index": r[0]}, size="sm", color="warning",
                           className="me-1"),
                dbc.Button("Eliminar", id={"type": "btn-eliminar-visita", "index": r[0]}, size="sm", color="danger")
            ])
        ]) for r in rows
    ])

    return dbc.Table([header, body], bordered=True, hover=True, responsive=True, striped=True)