# pages/tienda.py

import dash
dash.register_page(__name__, path="/tienda")

from dash import html, dcc, Input, Output, State, callback, ctx
import dash_bootstrap_components as dbc
import sqlite3
import pandas as pd
from database import DB_PATH

layout = dbc.Container([
    html.H2("Tienda de Recompensas", className="my-4"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Equipo"),
            dcc.Dropdown(id="filtro-equipo-tienda", placeholder="Seleccione un equipo")
        ]),
        dbc.Col([
            dbc.Label("Estudiante"),
            dcc.Dropdown(id="dropdown-estudiante-tienda", placeholder="Seleccione un estudiante")
        ])
    ], className="mb-3"),

    dbc.Row([
        dbc.Col([
            dbc.Label("Puntos Disponibles"),
            html.Div(id="puntos-disponibles", className="lead")
        ])
    ]),

    html.Hr(),

    dbc.Row([
        dbc.Col([
            dbc.Label("Descripción del Artículo"),
            dbc.Input(id="input-descripcion", type="text", placeholder="Ej: Pelota")
        ]),
        dbc.Col([
            dbc.Label("Puntos a Descontar"),
            dbc.Input(id="input-puntos", type="number", min=1)
        ])
    ], className="mb-3"),

    dcc.Store(id="transaccion-id", storage_type="session"),

    dbc.Button("Registrar Compra", id="btn-comprar", color="primary", className="mb-3"),
    html.Div(id="mensaje-compra", className="mb-3"),

    html.Hr(),

    html.H4("Historial de Compras"),
    html.Div(id="tabla-compras")
])

@callback(
    Output("filtro-equipo-tienda", "options"),
    Input("filtro-equipo-tienda", "id")
)
def cargar_equipos(_):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT equipo FROM estudiantes ORDER BY equipo")
    equipos = cursor.fetchall()
    conn.close()
    return [{"label": e[0], "value": e[0]} for e in equipos]

@callback(
    Output("dropdown-estudiante-tienda", "options"),
    Input("filtro-equipo-tienda", "value")
)
def filtrar_estudiantes(equipo):
    if not equipo:
        return []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM estudiantes WHERE equipo = ? ORDER BY nombre", (equipo,))
    rows = cursor.fetchall()
    conn.close()
    return [{"label": r[1], "value": r[0]} for r in rows]

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
    mensaje = ""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TEMP VIEW IF NOT EXISTS resumen_puntaje AS
        SELECT e.id, e.nombre, e.equipo,
               (a.puntaje_asistencia + a.puntaje_puntual) AS puntaje,
               'Asistencia' AS categoria
        FROM asistencia a
        JOIN estudiantes e ON e.id = a.estudiante_id
        UNION ALL
        SELECT e.id, e.nombre, e.equipo,
               (m.puntos_biblia + m.puntos_folder + m.puntos_completo) AS puntaje,
               'Materiales' AS categoria
        FROM materiales m
        JOIN estudiantes e ON e.id = m.estudiante_id
        UNION ALL
        SELECT e.id, e.nombre, e.equipo,
               v.puntaje,
               'Visitas' AS categoria
        FROM visitas v
        JOIN estudiantes e ON e.id = v.invitador_id
        UNION ALL
        SELECT e.id, e.nombre, e.equipo,
               c.puntaje,
               'Memorización' AS categoria
        FROM citas_completadas cc
        JOIN citas c ON c.id = cc.cita_id
        JOIN estudiantes e ON e.id = cc.estudiante_id;
    """)

    df = pd.read_sql_query("SELECT SUM(puntaje) AS total FROM resumen_puntaje WHERE id = ?", conn, params=(estudiante_id,))
    total_ganado = df["total"].iloc[0] if not df.empty and df["total"].iloc[0] else 0

    cursor.execute("SELECT COALESCE(SUM(puntos_gastados), 0) FROM compras WHERE estudiante_id = ?", (estudiante_id,))
    gastados = cursor.fetchone()[0]
    disponibles = total_ganado - gastados

    if isinstance(triggered_id, dict) and triggered_id["type"] == "btn-eliminar-compra":
        compra_id = triggered_id["index"]
        cursor.execute("DELETE FROM compras WHERE id = ?", (compra_id,))
        conn.commit()
        conn.close()
        return manejar_compras(estudiante_id, None, None, None, "", None, None)

    if isinstance(triggered_id, dict) and triggered_id["type"] == "btn-editar-compra":
        compra_id = triggered_id["index"]
        cursor.execute("SELECT descripcion, puntos_gastados FROM compras WHERE id = ?", (compra_id,))
        row = cursor.fetchone()
        return (
            mostrar_tabla_compras(estudiante_id),
            "",
            f"{disponibles} puntos disponibles",
            row[0],
            row[1],
            compra_id,
            "Actualizar"
        )

    if triggered_id == "btn-comprar":
        if not descripcion or puntos is None:
            conn.close()
            return mostrar_tabla_compras(estudiante_id), dbc.Alert("Complete todos los campos", color="warning"), f"{disponibles} puntos disponibles", descripcion, puntos, compra_id, "Registrar"

        if puntos > disponibles and not compra_id:
            conn.close()
            return mostrar_tabla_compras(estudiante_id), dbc.Alert("Puntos insuficientes", color="danger"), f"{disponibles} puntos disponibles", descripcion, puntos, compra_id, "Registrar"

        if compra_id:
            cursor.execute("UPDATE compras SET descripcion = ?, puntos_gastados = ? WHERE id = ?",
                           (descripcion.strip(), puntos, compra_id))
            mensaje = dbc.Alert("Compra actualizada correctamente.", color="success")
        else:
            cursor.execute("INSERT INTO compras (estudiante_id, descripcion, puntos_gastados) VALUES (?, ?, ?)",
                           (estudiante_id, descripcion.strip(), puntos))
            mensaje = dbc.Alert("Compra registrada correctamente.", color="success")

        conn.commit()

    descuento = puntos if not compra_id and puntos is not None else 0
    conn.close()
    return (
        mostrar_tabla_compras(estudiante_id),
        mensaje,
        f"{disponibles - descuento} puntos disponibles",
        "", None, None, "Registrar"
    )

def mostrar_tabla_compras(estudiante_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(
        "SELECT id, descripcion, puntos_gastados, fecha FROM compras WHERE estudiante_id = ? ORDER BY fecha DESC",
        conn, params=(estudiante_id,))
    conn.close()

    if df.empty:
        return html.P("Este estudiante no ha realizado compras.")

    return dbc.Table([
        html.Thead(html.Tr([html.Th("Artículo"), html.Th("Puntos"), html.Th("Fecha"), html.Th("Acciones")])),
        html.Tbody([
            html.Tr([
                html.Td(row["descripcion"]),
                html.Td(row["puntos_gastados"]),
                html.Td(row["fecha"]),
                html.Td([
                    dbc.Button("Editar", id={"type": "btn-editar-compra", "index": row["id"]}, size="sm", color="warning", className="me-1"),
                    dbc.Button("Eliminar", id={"type": "btn-eliminar-compra", "index": row["id"]}, size="sm", color="danger")
                ])
            ]) for _, row in df.iterrows()
        ])
    ], bordered=True, hover=True, responsive=True, striped=True)