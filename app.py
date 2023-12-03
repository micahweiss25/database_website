import sys
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
from mysql.connector import connect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
import base64

CREDS = {}
app = Flask(__name__)
with open("/var/www/flask/password.txt", "r") as f:
    CREDS["PASSWORD"] = f.readline()
    CREDS["USERNAME"] = f.readline()
    CREDS["DATABASE"] = f.readline()
    CREDS["SECRET_KEY"] = f.readline()

app.secret_key = CREDS["SECRET_KEY"]
bcrypt = Bcrypt(app)

login_manager = LoginManager()
# redirect to login page if user is not logged in
login_manager.login_view = "/flask/login"
login_manager.init_app(app)


def get_user_by_id(userID):
    # Connect to database
    try:
        cnx = connect(user='micah',
                      password='password',
                      database='wpmb')
    except Exception as e:
        print(f"Error: failed to connect to database due to {e}")
        raise e
    try:
        cursor = cnx.cursor(prepared=True)
        query = "SELECT * FROM Users WHERE userID = %s"
        cursor.execute(query, [userID])
        result = cursor.fetchall()[0]
        cnx.close()
    except Exception as e:
        print(f"Error: failed to query database due to {e}")
        raise e
    if len(result) > 0:
        try:
            user = User(userID=result[0],
                        password_hash=result[1],
                        first_name=result[2],
                        last_name=result[3],
                        admin=result[4],
                        seller=result[5])
            return user
        except Exception as e:
            print(f"Error: failed to create user due to {e}")
            raise e
    else:
        return None


@login_manager.user_loader
def load_user(userID):
    return get_user_by_id(userID)


@app.route("/login", methods=["GET"])
def login():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    # Get username and password
    username = request.form.get("username")
    password = request.form.get("password")

    # Connect to database
    cnx = connect(user='micah',
                  password='password',
                  database='wpmb')

    # Get cursor
    try:
        cursor = cnx.cursor(prepared=True)
    except Exception as e:
        print(f"Error: failed to create cursor due to {e}")
        raise e

    # query database for username
    try:
        query = "SELECT * FROM Users WHERE userID = %s"
        cursor.execute(query, [username])
        result = list(cursor.fetchall()[0])
        cnx.close()
    except Exception as e:
        print(f"Error: failed to query database due to {e}")
        raise e
    
    # check if username exists
    if len(result) > 0:
        user = None
        try:
            if bcrypt.check_password_hash(base64.b64decode(result[1]),
                                          password):
                user = User(userID=result[0],
                            password_hash=result[1],
                            first_name=result[2],
                            last_name=result[3],
                            admin=result[4],
                            seller=result[5])
            login_user(user, remember=True)
            flash("loggin sucessful")
            return redirect(url_for("index"))
        except Exception as e:
            print(f"Error: failed to login due to {e}")
            raise e
        
    flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/register", methods=["GET"])
def register():
    logout_user()
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    # Get username and password
    username = request.form.get("username")
    password = request.form.get("password")

    # Check if username already exists
    cnx = connect(user=CREDS["USERNAME"],
                  password=CREDS["PASSWORD"],
                  database=CREDS["DATABASE"])
    cursor = cnx.cursor(prepared=True)
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, [request.form["username"]])
    result = cursor.fetchall()
    cnx.close()
    if len(result) > 0:
        flash("Username already exists")
        return render_template("register.html")
    else:
        # Connect to database
        cnx = connect(user=CREDS["USERNAME"],
                      password=CREDS["PASSWORD"],
                      database=CREDS["DATABASE"])
        cursor = cnx.cursor(prepared=True)
        query = "INSERT INTO users (username, password_hash, first_name, last_name, admin, seller) VALUES (%s, %s, %s, %s, %s, %s)"
        cursor.execute(query,
                       (username,
                        bcrypt.generate_password_hash(password).decode('utf-8'),
                        request.form["first_name"],
                        request.form["last_name"],
                        0,
                        0))
        cnx.commit()
        cnx.close()
        flash("Account created")
        return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@login_required
def index():
    return render_template("viewProducts.html", user=current_user)


if __name__ == "__main__":
    app.run(debug=True)
