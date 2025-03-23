# pages/versiculos.py

import dash

dash.register_page(__name__, path="/versiculos")

from dash import html, dcc, Input, Output, State, ctx, callback
import dash_bootstrap_components as dbc
import sqlite3
from database import DB_PATH

TIPOS = ["Versículo", "Capítulo"]

layout = dbc.Container([
    html.H2("Gestión de Versículos y Capítulos", className="my-4"),

    dcc.Store(id="selected-cita-id", storage_type="session"),

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
        ], md=4)
    ], className="mb-3"),

    dbc.Button("Guardar", id="btn-guardar", color="primary", className="mb-3"),
    html.Div(id="mensaje-cita", className="text-success mb-3"),

    html.Hr(),

    html.H4("Listado de Citas"),
    html.Div(id="tabla-citas")
])


@callback(
    Output("mensaje-cita", "children"),
    Output("tabla-citas", "children"),
    Output("input-tipo", "value"),
    Output("input-cita", "value"),
    Output("input-puntaje", "value"),
    Output("selected-cita-id", "data"),
    Output("btn-guardar", "children"),
    Input("btn-guardar", "n_clicks"),
    Input({"type": "btn-eliminar-cita", "index": dash.ALL}, "n_clicks"),
    Input({"type": "btn-editar-cita", "index": dash.ALL}, "n_clicks"),
    State("input-tipo", "value"),
    State("input-cita", "value"),
    State("input-puntaje", "value"),
    State("selected-cita-id", "data"),
    prevent_initial_call=True
)
def manejar_citas(n_guardar, eliminar_clicks, editar_clicks, tipo, cita, puntaje, cita_id):
    triggered = ctx.triggered_id
    mensaje = ""
    tipo_val, cita_val, puntaje_val, cita_id_val, boton_text = None, None, None, None, "Guardar"

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Eliminar
    if isinstance(triggered, dict) and triggered.get("type") == "btn-eliminar-cita":
        cita_id = triggered["index"]
        cursor.execute("DELETE FROM citas WHERE id = ?", (cita_id,))
        conn.commit()
        conn.close()
        return "Cita eliminada.", mostrar_citas(), None, None, None, None, "Guardar"

    # Editar (cargar datos)
    if isinstance(triggered, dict) and triggered.get("type") == "btn-editar-cita":
        cita_id = triggered["index"]
        cursor.execute("SELECT tipo, cita, puntaje FROM citas WHERE id = ?", (cita_id,))
        row = cursor.fetchone()
        conn.close()
        return "", mostrar_citas(), row[0], row[1], row[2], cita_id, "Actualizar"

    # Guardar / Actualizar
    if triggered == "btn-guardar":
        if not tipo or not cita or not puntaje:
            conn.close()
            return "Complete todos los campos.", mostrar_citas(), tipo, cita, puntaje, cita_id, "Guardar"

        if cita_id:
            cursor.execute("UPDATE citas SET tipo = ?, cita = ?, puntaje = ? WHERE id = ?",
                           (tipo, cita.strip(), puntaje, cita_id))
            mensaje = "Cita actualizada correctamente."
        else:
            cursor.execute("INSERT INTO citas (tipo, cita, puntaje) VALUES (?, ?, ?)",
                           (tipo, cita.strip(), puntaje))
            mensaje = "Cita agregada correctamente."

        conn.commit()
        conn.close()
        return mensaje, mostrar_citas(), None, None, None, None, "Guardar"

    conn.close()
    return "", mostrar_citas(), None, None, None, None, "Guardar"

def mostrar_citas():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tipo, cita, puntaje FROM citas ORDER BY tipo, cita")
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return html.P("No hay citas registradas.")

    header = html.Thead(html.Tr([html.Th("Tipo"), html.Th("Cita"), html.Th("Puntaje"), html.Th("Acciones")]))
    body = []

    for r in rows:
        body.append(html.Tr([
            html.Td(r[1]),
            html.Td(r[2]),
            html.Td(r[3]),
            html.Td([
                dbc.Button("Editar", id={"type": "btn-editar-cita", "index": r[0]}, color="warning", size="sm", className="me-1"),
                dbc.Button("Eliminar", id={"type": "btn-eliminar-cita", "index": r[0]}, color="danger", size="sm")
            ])
        ]))

    return dbc.Table([header, html.Tbody(body)], bordered=True, hover=True, responsive=True, striped=True)
