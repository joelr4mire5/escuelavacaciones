import sqlite3
import os

DB_PATH = os.path.join("data", "db.sqlite3")

def init_db():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Tabla de estudiantes
    c.execute('''
        CREATE TABLE IF NOT EXISTS estudiantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            edad INTEGER,
            equipo TEXT NOT NULL
        )
    ''')

    # Tabla de compras
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

    # Tabla de citas (versículos/capítulos)
    c.execute('''
        CREATE TABLE IF NOT EXISTS citas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tipo TEXT CHECK(tipo IN ('Versículo', 'Capítulo')),
            cita TEXT NOT NULL,
            puntaje INTEGER NOT NULL
        )
    ''')

    # Citas completadas por estudiantes
    c.execute('''
        CREATE TABLE IF NOT EXISTS citas_completadas (
            estudiante_id INTEGER NOT NULL,
            cita_id INTEGER NOT NULL,
            completado INTEGER DEFAULT 1,
            PRIMARY KEY (estudiante_id, cita_id),
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id),
            FOREIGN KEY(cita_id) REFERENCES citas(id)
        )
    ''')

    # Tabla de asistencia (1 fila por estudiante y día)
    c.execute('''
        CREATE TABLE IF NOT EXISTS asistencia (
            estudiante_id INTEGER,
            dia INTEGER,
            presente INTEGER DEFAULT 0,
            puntual INTEGER DEFAULT 0,
            puntaje_asistencia INTEGER DEFAULT 0,
            puntaje_puntual INTEGER DEFAULT 0,
            PRIMARY KEY(estudiante_id, dia),
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
        )
    ''')
    # Tabla de visitas
    c.execute('''
          CREATE TABLE IF NOT EXISTS visitas (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              nombre TEXT NOT NULL,
              es_adulto INTEGER DEFAULT 0,
              invitador_id INTEGER,
              puntaje INTEGER DEFAULT 0,
              FOREIGN KEY(invitador_id) REFERENCES estudiantes(id)
          )
      ''')

    c.execute('''
          CREATE TABLE IF NOT EXISTS materiales (
            estudiante_id INTEGER,
            dia INTEGER,
            biblia INTEGER DEFAULT 0,
            folder INTEGER DEFAULT 0,
            completo INTEGER DEFAULT 0,
            puntos_biblia INTEGER DEFAULT 0,
            puntos_folder INTEGER DEFAULT 0,
            puntos_completo INTEGER DEFAULT 0,
            PRIMARY KEY(estudiante_id, dia),
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
        )
      ''')

    c.execute('''
              CREATE TABLE IF NOT EXISTS citas_completadas (
            estudiante_id INTEGER NOT NULL,
            cita_id INTEGER NOT NULL,
            completado INTEGER DEFAULT 1,
            PRIMARY KEY (estudiante_id, cita_id),
            FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id),
            FOREIGN KEY(cita_id) REFERENCES citas(id)
        )
         ''')



    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect(DB_PATH)
