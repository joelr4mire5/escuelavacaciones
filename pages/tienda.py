import dash
import psycopg2  # For PostgreSQL connection
import pandas as pd  # For working with SQL query results
from dash import html, Input, Output, State, callback, ctx, dcc
import dash_bootstrap_components as dbc

dash.register_page(__name__, path="/tienda")

# Connection URL for Heroku PostgreSQL
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"

layout = dbc.Container([
    dbc.Row([
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="dropdown-estudiante-tienda", placeholder="Seleccione un estudiante")
        ], md=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Descripción de compra"),
            dbc.Input(id="input-descripcion", placeholder="Ingrese la descripción de la compra")
        ], md=6),
        dbc.Col([
            dbc.Label("Puntos a usar"),
            dbc.Input(id="input-puntos", type="number", placeholder="Ingrese los puntos a gastar")
        ], md=3),
    ], className="mb-4"),

    dbc.Button("Registrar", id="btn-comprar", color="primary", className="mt-3"),

    dbc.Alert(id="mensaje-compra", is_open=False, duration=4000, className="mt-3"),

    html.Div(id="puntos-disponibles", className="text-center mt-3 text-primary fw-bold"),

    html.Hr(),
    html.Div(id="tabla-compras", className="mt-4"),

    dcc.Store(id="transaccion-id"),
])


# Helper function to get a database connection
def get_db_connection():
    """Establishes a connection to the PostgreSQL database."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def calcular_disponibles(estudiante_id):
    """Calculate the available points for a student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            WITH resumen_puntaje AS (
                SELECT estudiante_id, SUM(puntaje) AS total_puntos
                FROM (
                    SELECT e.id AS estudiante_id,
                           (a.puntaje_asistencia + a.puntaje_puntual) AS puntaje
                    FROM asistencia a
                    JOIN estudiantes e ON e.id = a.estudiante_id
                    UNION ALL
                    SELECT e.id AS estudiante_id,
                           (m.puntos_biblia + m.puntos_folder + m.puntos_completo) AS puntaje
                    FROM materiales m
                    JOIN estudiantes e ON e.id = m.estudiante_id
                    UNION ALL
                    SELECT e.id AS estudiante_id,
                           v.puntaje
                    FROM visitas v
                    JOIN estudiantes e ON e.id = v.invitador_id
                    UNION ALL
                    SELECT e.id AS estudiante_id,
                           c.puntaje
                    FROM citas_completadas cc
                    JOIN citas c ON c.id = cc.cita_id
                    JOIN estudiantes e ON e.id = cc.estudiante_id
                ) AS puntos
                GROUP BY estudiante_id
            )
            SELECT COALESCE(r.total_puntos, 0) - COALESCE(c.sum_gastado, 0) AS puntos_disponibles
            FROM resumen_puntaje r
            LEFT JOIN (
                SELECT estudiante_id, SUM(puntos_gastados) AS sum_gastado
                FROM compras
                GROUP BY estudiante_id
            ) c ON r.estudiante_id = c.estudiante_id
            WHERE r.estudiante_id = %s
        """, (estudiante_id,))
        result = cursor.fetchone()
        return result[0] if result else 0
    finally:
        conn.close()


def mostrar_tabla_compras(estudiante_id):
    """Display the table of purchases for a specific student."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, descripcion, puntos_gastados
            FROM compras
            WHERE estudiante_id = %s
            ORDER BY id
        """, (estudiante_id,))
        compras = cursor.fetchall()
        if not compras:
            return html.P("No hay compras registradas.")

        table = dbc.Table([
            html.Thead(html.Tr([html.Th("ID"), html.Th("Descripción"), html.Th("Puntos"), html.Th("Acciones")])),
            html.Tbody([
                html.Tr([
                    html.Td(compra[0]),
                    html.Td(compra[1]),
                    html.Td(compra[2]),
                    html.Td([
                        dbc.Button("Editar", id={"type": "btn-editar-compra", "index": compra[0]}, size="sm",
                                   className="me-1"),
                        dbc.Button("Eliminar", id={"type": "btn-eliminar-compra", "index": compra[0]}, size="sm",
                                   color="danger")
                    ])
                ]) for compra in compras
            ])
        ], bordered=True, hover=True, responsive=True)

        return table
    finally:
        conn.close()


@callback(
    Output("tabla-compras", "children"),
    Output("mensaje-compra", "children"),
    Output("puntos-disponibles", "children"),
    Output("input-descripcion", "value"),
    Output("input-puntos", "value"),
    Output("transaccion-id", "data"),
    Output("btn-comprar", "children"),
    Input("dropdown-estudiante-tienda", "value"),
    Input("btn-comprar", "n_clicks"),
    Input({"type": "btn-editar-compra", "index": dash.ALL}, "n_clicks"),
    Input({"type": "btn-eliminar-compra", "index": dash.ALL}, "n_clicks"),
    State("input-descripcion", "value"),
    State("input-puntos", "value"),
    State("transaccion-id", "data"),
    prevent_initial_call=True
)
def manejar_compras(estudiante_id, n_comprar, editar_clicks, eliminar_clicks, descripcion, puntos, compra_id):
    if not estudiante_id:
        return "", "", "", None, None, None, "Registrar"

    triggered_id = ctx.triggered_id
    conn = get_db_connection()
    cursor = conn.cursor()
    mensaje = ""

    try:
        if isinstance(triggered_id, dict) and triggered_id["type"] == "btn-eliminar-compra":
            compra_id = triggered_id["index"]
            cursor.execute("DELETE FROM compras WHERE id = %s", (compra_id,))
            conn.commit()
            mensaje = dbc.Alert("Compra eliminada.", color="info")

        elif isinstance(triggered_id, dict) and triggered_id["type"] == "btn-editar-compra":
            compra_id = triggered_id["index"]
            cursor.execute("SELECT descripcion, puntos_gastados FROM compras WHERE id = %s", (compra_id,))
            row = cursor.fetchone()
            return mostrar_tabla_compras(
                estudiante_id), "", f"{calcular_disponibles(estudiante_id)} puntos disponibles", \
                row[0], row[1], compra_id, "Actualizar"

        elif triggered_id == "btn-comprar":
            if not descripcion or puntos is None:
                return mostrar_tabla_compras(estudiante_id), dbc.Alert("Complete todos los campos.", color="warning"), \
                    f"{calcular_disponibles(estudiante_id)} puntos disponibles", descripcion, puntos, compra_id, \
                    "Registrar"

            disponibles = calcular_disponibles(estudiante_id)
            if puntos > disponibles and not compra_id:
                return mostrar_tabla_compras(estudiante_id), dbc.Alert("Puntos insuficientes.", color="danger"), \
                    f"{disponibles} puntos disponibles", descripcion, puntos, compra_id, "Registrar"

            if compra_id:
                cursor.execute("UPDATE compras SET descripcion = %s, puntos_gastados = %s WHERE id = %s",
                               (descripcion.strip(), puntos, compra_id))
                mensaje = dbc.Alert("Compra actualizada correctamente.", color="success")
            else:
                cursor.execute("INSERT INTO compras (estudiante_id, descripcion, puntos_gastados) VALUES (%s, %s, %s)",
                               (estudiante_id, descripcion.strip(), puntos))
                mensaje = dbc.Alert("Compra registrada correctamente.", color="success")

            conn.commit()

        nuevos_disponibles = calcular_disponibles(estudiante_id)
        return mostrar_tabla_compras(
            estudiante_id), mensaje, f"{nuevos_disponibles} puntos disponibles", "", None, None, "Registrar"

    finally:
        conn.close()