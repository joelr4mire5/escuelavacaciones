import os
import psycopg2

DATABASE_URL = os.environ.get("postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub")  # Heroku DATABASE_URL


def init_db():
    try:
        # Connect to the Heroku PostgreSQL database
        connection = psycopg2.connect(DATABASE_URL)
        cursor = connection.cursor()

        # Define a trigger function for automatic `updated_at` updates
        cursor.execute('''
            CREATE OR REPLACE FUNCTION update_updated_at_column()
            RETURNS TRIGGER AS $$
            BEGIN
                NEW.updated_at = NOW();
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        ''')

        # Check whether the table already exists and create if it doesn't

        # Create table `estudiantes`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS estudiantes (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                edad INTEGER,
                equipo TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS set_updated_at_estudiantes
            BEFORE UPDATE ON estudiantes
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        # Create table `compras`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id SERIAL PRIMARY KEY,
                estudiante_id INTEGER,
                descripcion TEXT,
                puntos_gastados INTEGER,
                fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
            )
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS set_updated_at_compras
            BEFORE UPDATE ON compras
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        # Create table `citas`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                id SERIAL PRIMARY KEY,
                tipo TEXT CHECK(tipo IN ('Versículo', 'Capítulo')),
                cita TEXT NOT NULL,
                puntaje INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS set_updated_at_citas
            BEFORE UPDATE ON citas
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        # Create table `citas_completadas`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas_completadas (
                estudiante_id INTEGER NOT NULL,
                cita_id INTEGER NOT NULL,
                completado INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (estudiante_id, cita_id),
                FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id),
                FOREIGN KEY(cita_id) REFERENCES citas(id)
            )
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS set_updated_at_citas_completadas
            BEFORE UPDATE ON citas_completadas
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        # Create table `asistencia`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS asistencia (
                estudiante_id INTEGER,
                dia INTEGER,
                presente INTEGER DEFAULT 0,
                puntual INTEGER DEFAULT 0,
                puntaje_asistencia INTEGER DEFAULT 0,
                puntaje_puntual INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(estudiante_id, dia),
                FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
            )
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS set_updated_at_asistencia
            BEFORE UPDATE ON asistencia
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        # Create table `visitas`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS visitas (
                id SERIAL PRIMARY KEY,
                nombre TEXT NOT NULL,
                es_adulto INTEGER DEFAULT 0,
                invitador_id INTEGER,
                puntaje INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(invitador_id) REFERENCES estudiantes(id)
            )
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS set_updated_at_visitas
            BEFORE UPDATE ON visitas
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        # Create table `materiales`
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS materiales (
                estudiante_id INTEGER,
                dia INTEGER,
                biblia INTEGER DEFAULT 0,
                folder INTEGER DEFAULT 0,
                completo INTEGER DEFAULT 0,
                puntos_biblia INTEGER DEFAULT 0,
                puntos_folder INTEGER DEFAULT 0,
                puntos_completo INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY(estudiante_id, dia),
                FOREIGN KEY(estudiante_id) REFERENCES estudiantes(id)
            )
        """)
        cursor.execute("""
            CREATE TRIGGER IF NOT EXISTS set_updated_at_materiales
            BEFORE UPDATE ON materiales
            FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
        """)

        cursor.execute(""" 
        CREATE TABLE users (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL  -- Se recomienda guardar contraseñas encriptadas
);
        """)



        # Commit the changes
        connection.commit()

        # Close communication with the database
        cursor.close()
        connection.close()
        print("Database tables and triggers initialized successfully.")

    except Exception as e:
        print("An error occurred while initializing the database:")
        print(e)


def get_connection():
    try:
        # Return a new connection to the PostgreSQL database
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("An error occurred while attempting to connect to the database:")
        print(e)
        return None