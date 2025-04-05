# auth.py

# Usuarios hardcodeados (puedes mover esto a la BD si quieres)
USERS = {
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
    "joel": "dataanalyst"
}

def validate_login(username, password):
    return USERS.get(username) == password
