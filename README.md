# Plataforma web para visualización de delitos en la ciudad de Málaga

## Base de datos
Creamos una conexión con un usuario en MySQL Workbench
Ejecutamos el archivo create_bbdd.sql de la carpeta config en MySQL Workbench

## Entorno
Creamos un archivo .env en la carpeta del proyecto e introducimos las siguientes entradas

```sh
API_KEY = 'Aj943_sLvTzpse2YFv4FZSC13eoEU4djhgLF5Qdq0CcSVpomrm15eZad759fjYQu'
USUARIO_BBDD = Usuario usado para crear la conexión en MySQL Workbench
PASSWORD_BDDD = Contraseña del usuario usado para crear la conexión en MySQL Workbench
BBDD = 'tfg_felipe_llinares'
```

Abrimos un terminal dentro de Visual Studio Code y ejecutamos el siguiente comando:

```sh
pip install -r requirements.txt
```

## Ejecución  

Entramos en archivos app.ipynb y ejecutamos todas las celdas