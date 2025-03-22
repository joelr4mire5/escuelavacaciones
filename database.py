import sqlite3
import os

DB_PATH = os.path.join("data", "db.sqlite3")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER,
            equipo TEXT NOT NULL
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS puntajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER,
            actividad TEXT,
            puntos INTEGER,
            fecha DATE DEFAULT (datetime('now')),
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            estudiante_id INTEGER,
            descripcion TEXT,
            puntos_gastados INTEGER,
            fecha DATE DEFAULT (datetime('now')),
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
        )
    ''')

    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)
