import pymysql

from dotenv import load_dotenv
import os  # Import the os module

load_dotenv()
USUARIO_BBDD = os.environ.get("USUARIO_BBDD")
PASSWORD_BDDD = os.environ.get("PASSWORD_BDDD")
BBDD = os.environ.get("BBDD")

mydb = pymysql.connect(
            host='localhost',
            user=USUARIO_BBDD,
            passwd=PASSWORD_BDDD,
            db=BBDD
        )