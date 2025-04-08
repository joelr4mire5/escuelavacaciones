import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation
from werkzeug.security import check_password_hash, generate_password_hash


# URL de conexión a tu base de datos en Heroku
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"  # Reemplaza esto con tu URL real


def get_connection():
    """Establece una conexión con la base de datos."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")


def validate_login(username, password):
    """Valida el inicio de sesión del usuario comparando la contraseña con la base de datos."""
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            # Buscar el usuario en la base de datos
            cur.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cur.fetchone()
            if user:
                # Comparar contraseña hash almacenada con la proporcionada
                return check_password_hash(user['password'], password)
            return False
    finally:
        conn.close()


def add_user(username, password):
    """Agrega un nuevo usuario con la contraseña protegida, manejando errores en caso de duplicados."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            hashed_password = generate_password_hash(password)

            # Intentar agregar el usuario
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed_password)
            )
            conn.commit()
            print(f"Usuario '{username}' agregado con éxito.")
    except UniqueViolation:
        print(f"Error: El usuario '{username}' ya existe.")
    except psycopg2.Error as e:
        # Ocurrió otro error
        print(f"Error inesperado al agregar el usuario: {e}")
    finally:
        conn.close()


# Lista de usuarios existentes
users = {
    "sofia": "luna123sol",
    "meme": "gatorojo45",
    "elizabeth": "panazul88",
    "yamileth": "casaverde7",
    "ana": "nube123flor",
    "danieska": "perrocafe22",
    "missy": "solrio89",
    "mary": "mesablanca3",
    "andrey": "fuegonoche6",
    "karina": "tazamiel99",
    "joel": "dataanalyst",
    "estefany": "mesablanca4"
}

# Agrega cada usuario con su contraseña
for username, password in users.items():
    add_user(username, password)