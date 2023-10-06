import hashlib
from config.db import mydb

def comprobar_constraseña(username, password):
    cursor = mydb.cursor()

    select_query = "SELECT salt, contraseña, administrador from usuario WHERE usuario.usuario = %s;"
    values_query = (username)
    cursor.execute(select_query, values_query)
    result = cursor.fetchone()

    salt = result[0]
    contraseña = result[1]
    administrador = result[2]  

    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    sha256_hash.update((salt + password).encode())

    # Get the hexadecimal representation of the hash
    hex_digest = sha256_hash.hexdigest()
    
    mydb.commit()
    cursor.close()

    if (contraseña == hex_digest):
        return administrador
    else:
        return -1