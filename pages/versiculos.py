# pages/versiculos.py
# pages/versiculos.py

import dash
dash.register_page(__name__, path="/versiculos")

from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
import psycopg2

# IMPORTANT: Import ALL from dash (or dash.dependencies)
from dash.dependencies import ALL

# Connection URL for Heroku PostgreSQL
DATABASE_URL = (
    "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd"
    "@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"
)

EDAD_CLASES = {
    "0-3": (0, 3),
    "4-5": (4, 5),
    "6-8": (6, 8),
    "9-11": (9, 11),
    "12+": (12, 99)
}
TIPOS = ["Versículo", "Capítulo"]

layout = dbc.Container([
    html.H2("Gestión de Versículos y Capítulos", className="my-4"),
    dcc.Store(id="selected-cita-id", storage_type="session"),

    # Row 1: Tipo, Cita, Puntaje
    dbc.Row([
        dbc.Col([
            dbc.Label("Tipo"),
            dcc.Dropdown(
                id="input-tipo",
                options=[{"label": t, "value": t} for t in TIPOS],
                placeholder="Seleccione tipo"
            )
        ], md=4),
        dbc.Col([
            dbc.Label("Cita Bíblica"),
            dbc.Input(id="input-cita", type="text", placeholder="Ej: Juan 3:16")
        ], md=4),
        dbc.Col([
            dbc.Label("Puntaje"),
            dbc.Input(id="input-puntaje", type="number", min=1, placeholder="Ej: 5")
        ], md=4),
    ], className="mb-3"),

    # Row 2: Clase
    dbc.Row([
        dbc.Col([
            dbc.Label("Clase"),
            dcc.Dropdown(
                id="input-clase",
                options=[
                    {"label": label, "value": label} for label in EDAD_CLASES.keys()
                ],
                placeholder="Seleccione la clase"
            )
        ], md=4),
    ], className="mb-3"),

    dbc.Button("Guardar", id="btn-guardar", color="primary", className="mb-3"),
    html.Div(id="mensaje-cita", className="text-success mb-3"),

    html.Hr(),

    html.H4("Listado de Citas"),
    html.Div(id="tabla-citas")
])


def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")


@callback(
    Output("mensaje-cita", "children"),   # success/error message
    Output("tabla-citas", "children"),    # updated table
    Output("input-tipo", "value"),        # reset or load 'tipo'
    Output("input-cita", "value"),        # reset or load 'cita'
    Output("input-puntaje", "value"),     # reset or load 'puntaje'
    Output("input-clase", "value"),       # reset or load 'clase'
    Output("selected-cita-id", "data"),   # store the edited row ID
    Output("btn-guardar", "children"),    # change button text
    Input("btn-guardar", "n_clicks"),
    # Use ALL from dash, not dbc.ALL
    Input({"type": "btn-eliminar-cita", "index": ALL}, "n_clicks"),
    Input({"type": "btn-editar-cita", "index": ALL}, "n_clicks"),
    State("input-tipo", "value"),
    State("input-cita", "value"),
    State("input-puntaje", "value"),
    State("input-clase", "value"),
    State("selected-cita-id", "data"),
    prevent_initial_call=True
)
def manejar_citas(n_guardar, eliminar_clicks, editar_clicks,
                  tipo, cita, puntaje, clase, cita_id):
    triggered = ctx.triggered_id
    mensaje = ""

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        # -----------------------------------------------------------
        # 1) ELIMINAR CITA
        # -----------------------------------------------------------
        if isinstance(triggered, dict) and triggered.get("type") == "btn-eliminar-cita":
            cita_id = triggered["index"]  # ID of row to delete
            cursor.execute("DELETE FROM citas WHERE id = %s", (cita_id,))
            conn.commit()
            return (
                "Cita eliminada.",
                mostrar_citas(cursor=cursor),
                None, None, None, None, None,
                "Guardar"
            )

        # -----------------------------------------------------------
        # 2) EDITAR CITA (load data into form)
        # -----------------------------------------------------------
        if isinstance(triggered, dict) and triggered.get("type") == "btn-editar-cita":
            cita_id = triggered["index"]
            cursor.execute("""
                SELECT tipo, cita, puntaje, clase 
                FROM citas
                WHERE id = %s
            """, (cita_id,))
            row = cursor.fetchone()
            if row:
                return (
                    "",
                    mostrar_citas(cursor=cursor),
                    row[0],  # tipo
                    row[1],  # cita
                    row[2],  # puntaje
                    row[3],  # clase
                    cita_id, # store ID for updates
                    "Actualizar"
                )
            else:
                return (
                    f"No se encontró la cita con ID {cita_id}.",
                    mostrar_citas(cursor=cursor),
                    None, None, None, None, None,
                    "Guardar"
                )

        # -----------------------------------------------------------
        # 3) GUARDAR / ACTUALIZAR CITA
        # -----------------------------------------------------------
        if triggered == "btn-guardar":
            if not tipo or not cita or not puntaje or not clase:
                return (
                    "Complete todos los campos.",
                    mostrar_citas(cursor=cursor),
                    tipo, cita, puntaje, clase, cita_id,
                    "Guardar"
                )

            if cita_id:
                # Update existing row
                cursor.execute("""
                    UPDATE citas
                    SET tipo = %s, cita = %s, puntaje = %s, clase = %s
                    WHERE id = %s
                """, (tipo, cita.strip(), puntaje, clase, cita_id))
                mensaje = "Cita actualizada correctamente."
            else:
                # Insert new
                cursor.execute("""
                    INSERT INTO citas (tipo, cita, puntaje, clase)
                    VALUES (%s, %s, %s, %s)
                """, (tipo, cita.strip(), puntaje, clase))
                mensaje = "Cita agregada correctamente."

            conn.commit()
            return (
                mensaje,
                mostrar_citas(cursor=cursor),
                None, None, None, None, None,
                "Guardar"
            )

    except psycopg2.Error as e:
        return (
            f"Error: {e}",
            mostrar_citas(cursor=cursor),
            tipo, cita, puntaje, clase, cita_id,
            "Guardar"
        )
    finally:
        conn.close()


def mostrar_citas(selected_clase=None, cursor=None):
    """
    Fetch and display the list of registered citas (including 'clase').
    If selected_clase is provided, only rows matching that 'clase' are shown.
    """
    if cursor is None:
        conn = get_db_connection()
        cursor = conn.cursor()
        close_conn = True
    else:
        close_conn = False

    if selected_clase:
        query = """
            SELECT id, tipo, cita, puntaje, clase
            FROM citas
            WHERE clase = %s
            ORDER BY tipo, cita
        """
        cursor.execute(query, (selected_clase,))
    else:
        query = """
            SELECT id, tipo, cita, puntaje, clase
            FROM citas
            ORDER BY tipo, cita
        """
        cursor.execute(query)

    rows = cursor.fetchall()
    if close_conn:
        conn.close()

    if not rows:
        return html.P("No hay citas registradas.")

    header = html.Thead(html.Tr([
        html.Th("Tipo"),
        html.Th("Cita"),
        html.Th("Puntaje"),
        html.Th("Clase"),
        html.Th("Acciones")
    ]))

    body = []
    for (cita_id, tipo, cita_text, punt, clase_text) in rows:
        body.append(html.Tr([
            html.Td(tipo),
            html.Td(cita_text),
            html.Td(punt),
            html.Td(clase_text),
            html.Td([
                dbc.Button(
                    "Editar",
                    id={"type": "btn-editar-cita", "index": cita_id},
                    color="warning", size="sm", className="me-1"
                ),
                dbc.Button(
                    "Eliminar",
                    id={"type": "btn-eliminar-cita", "index": cita_id},
                    color="danger", size="sm"
                )
            ])
        ]))

    return dbc.Table(
        [header, html.Tbody(body)],
        bordered=True, hover=True, responsive=True, striped=True
    )
