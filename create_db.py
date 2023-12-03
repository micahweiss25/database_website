from mysql.connector import connect


CREDS = {}
app = Flask(__name__)
with open("/var/www/flask/password.txt", "r") as f:
    CREDS["PASSWORD"] = f.readline()
    CREDS["USERNAME"] = f.readline()
    CREDS["DATABASE"] = f.readline()
    CREDS["SECRET_KEY"] = f.readline()

def create_db(name):
    cnx = connect(user=CREDS["USERNAME"],
                  password=CREDS["PASSWORD"],
                  database=CREDS["DATABASE"])
    cursor = cnx.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS " + name)
    cnx.close()

def create_table(name, columns):