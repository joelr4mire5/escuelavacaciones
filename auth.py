# auth.py

# Usuarios hardcodeados (puedes mover esto a la BD si quieres)
USERS = {
    "maestro1": "1234",
    "maestro2": "1234",
    "maestro3": "1234",
    "maestro4": "1234",
    "maestro5": "1234",
    "maestro6": "1234",
    "maestro7": "1234",
    "maestro8": "1234",
    "maestro9": "1234",
    "maestro10": "1234",
    "maestro11": "1234",
    "maestro12": "1234",
    "maestro13": "1234",
    "maestro14": "1234",
    "maestro15": "1234",
    "maestro16": "1234",
    "maestro17": "1234",
    "maestro18": "1234",
    "maestro19": "1234",
    "maestro20": "1234"

}

def validate_login(username, password):
    return USERS.get(username) == password
