import json

filename = "credentials.json"
dataStructure = {
    "credentials": {
        "username": "",
        "password": ""
    },
    "additional_info":{
        "url_login": ""
    }
}

# Crear un archivo JSON
def create_json(filename, dataStructure):
    with open(filename, 'w') as file:
        json.dump(dataStructure, file, indent=4)
    print(f'Archivo {filename} creado con éxito.')

# Leer el archivo JSON
def load_credentials(filename):
    with open(filename, 'r') as file:
        credentials = json.load(file)
    return credentials

# Actualizar las credenciales en el archivo JSON
def update_credentials(filename, new_username, new_password):
    credentials = load_credentials(filename)
    credentials['credentials']['username'] = new_username
    credentials['credentials']['password'] = new_password

    with open(filename, 'w') as file:
        json.dump(credentials, file, indent=4)
    print('Archivo JSON actualizado con éxito.')

# Solicitar datos del usuario
def data_request():
    print("Ingrese el usuario para iniciar sesión en netsuite: ")
    username = input()
    print("Ingrese su contraseña para iniciar sesión en netsuite: ")
    password = input()
    # Crear el archivo JSON si no existe
    try:
        load_credentials(filename)
    except FileNotFoundError:
        create_json(filename, dataStructure)

    # Actualizar las credenciales
    update_credentials(filename, username, password)
# Llamar a la función para solicitar datos del usuario
data_request()
with open('selenyum.py') as f:
    code = f.read()
    exec(code)