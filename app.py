from flask import Flask, flash, render_template, request, redirect
from flask_bcrypt import Bcrypt
from mysql.connector import connect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User

CREDS = {}
app = Flask(__name__)
with open("password.txt", "r") as f:
    CREDS["PASSWORD"] = f.readline()
    CREDS["USERNAME"] = f.readline()
    CREDS["DATABASE"] = f.readline()
    CREDS["SECRET_KEY"] = f.readline()

app.secret_key = CREDS["SECRET_KEY"]
bcrypt = Bcrypt(app)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(userID):
    User.get(userID)


@app.route("/login", method=["GET"])
def login():
    return render_template("login.html")


@app.route("/login", method=["POST"])
def login_post():
    # Get username and password
    username = request.form.get("username")
    password = request.form.get("password")

    # Connect to database
    cnx = connect(user=CREDS["USERNAME"],
                    password=CREDS["PASSWORD"],
                    database=CREDS["DATABASE"])

    # Get cursor
    cursor = cnx.cursor(prepared=True)
    query = "SELECT * FROM users WHERE username = %s"
    cursor.execute(query, [request.form["username"]])
    result = cursor.fetchall()
    cnx.close()
    if len(result) > 0:
        user = result[0]
        if bcrypt.check_password_hash(user[4], request.form['password']):
            user = User(userID=result[0],
                        password_hash=bcrypt.generate_password_hash(result[1]).decode('utf-8'),
                        first_name=result[2],
                        last_name=result[3],
                        admin=result[4],
                        seller=result[5])
            login_user(user, remember=True)
            return redirect("/viewProducts.html")
    flash("Invalid username or password")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/register", method=["GET"])
def register():
    return render_template("register.html")


@app.route("/register", method=["POST"])
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
        return redirect("/login")


@app.route("/", method=["GET"])
@login_required
def index():
    return render_template("viewProducts.html", user=current_user)
