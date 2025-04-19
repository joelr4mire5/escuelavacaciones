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

# def create_user_if_not_exists(username, password):
#     try:
#         conn = psycopg2.connect(DATABASE_URL, sslmode="require")
#         cur = conn.cursor()
#
#         # Check if the user already exists
#         cur.execute("SELECT COUNT(*) FROM users WHERE username = %s;", (username,))
#         user_exists = cur.fetchone()[0] > 0
#
#         if not user_exists:
#             cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, password))
#             print(f"User '{username}' created successfully.")
#         else:
#             print(f"User '{username}' already exists.")
#
#         conn.commit()
#         cur.close()
#         conn.close()
#
#     except psycopg2.Error as e:
#         print(f"Database error: {e}")
#     except Exception as e:
#         print(f"An error occurred: {e}")
#
#
#
# # List of users with their passwords
# users = {
#     "sofia": "luna123sol",
#     "meme": "gatorojo45",
#     "elizabeth": "panazul88",
#     "yamileth": "casaverde7",
#     "ana": "nube123flor",
#     "danieska": "perrocafe22",
#     "missy": "solrio89",
#     "mary": "mesablanca3",
#     "andrey": "fuegonoche6",
#     "karina": "tazamiel99",
#     "joel": "dataanalyst",
#     "estefany": "mesablanca4"
# }
#
# # Create all users in the list
# for username, password in users.items():
#     create_user_if_not_exists(username, password)