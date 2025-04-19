import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.errors import UniqueViolation
from werkzeug.security import check_password_hash, generate_password_hash

# URL de conexión a tu base de datos en Heroku
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"  # Reemplaza esto con tu URL real


def get_connection():
    """Establece una conexión con la base de datos."""
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def create_user_if_not_exists(username, password):
    try:
        hashed_password = generate_password_hash(password)

        conn = psycopg2.connect(DATABASE_URL, sslmode="require")
        cur = conn.cursor()

        # Check if the user already exists
        cur.execute("SELECT COUNT(*) FROM users WHERE username = %s;", (username,))
        user_exists = cur.fetchone()[0] > 0

        if not user_exists:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s);", (username, hashed_password))
            print(f"User '{username}' created successfully.")
        else:
            print(f"User '{username}' already exists.")

        conn.commit()
        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")


# List of users with their passwords
users = {
    "raquel": "escuelablanca",

}

# Create all users in the list
for username, password in users.items():
    create_user_if_not_exists(username, password)