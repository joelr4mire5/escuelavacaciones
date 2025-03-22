# auth.py

# Usuarios hardcodeados (puedes mover esto a la BD si quieres)
USERS = {
    "maestro1": "1234",
    "maestra2": "abcd"
}

def validate_login(username, password):
    return USERS.get(username) == password
