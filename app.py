import sys
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_bcrypt import Bcrypt
from mysql.connector import connect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from user import User
import base64

app = Flask(__name__)
DB_USERNAME = 'micah'
DB_PASSWORD = 'password'
DB_NAME = 'wpmb'

app.secret_key = "super secret key"
bcrypt = Bcrypt(app)

login_manager = LoginManager()
# redirect to login page if user is not logged in
login_manager.login_view = "/flask/login"
login_manager.init_app(app)


class Product:
    def __init__(self,
                 productID,
                 name,
                 price,
                 expiration,
                 category,
                 author=None,
                 for_class=None,
                 time=None,
                 departureFrom=None,
                 seatsAvailable=None):
        self.productID = productID
        self.name = name
        self.price = price
        self.expiration = expiration
        self.category = category
        self.author = author
        self.for_class = for_class
        self.time = time
        self.departureFrom = departureFrom
        self.seatsAvailable = seatsAvailable


def process_products(products):
    data = []
    for product in products:
        product = list(product)
        new_product = None
        productID = product[0]
        name = product[1]
        price = product[2]
        expiration = product[3]

        if product[4] is None:
            category = "Book"
            author = product[7]
            for_class = product[8]
            new_product = Product(productID=productID,
                                  name=name,
                                  price=price,
                                  expiration=expiration,
                                  category=category,
                                  author=author,
                                  for_class=for_class)
                                  
        elif product[7] is None:
            category = "Ride"
            time = product[6]
            departureFrom = product[4]
            seatsAvailable = product[5]
            new_product = Product(productID=productID,
                                  name=name,
                                  price=price,
                                  expiration=expiration,
                                  category=category,
                                  time=time,
                                  departureFrom=departureFrom,
                                  seatsAvailable=seatsAvailable)
        data.append(new_product)
    return data


def get_user_by_id(userID):
    # Connect to database
    try:
        cnx = connect(user=DB_USERNAME,
                      password=DB_PASSWORD,
                      database=DB_NAME)
    except Exception as e:
        print(f"Error: failed to connect to database due to {e}")
        raise e
    try:
        cursor = cnx.cursor(prepared=True)
        query = "SELECT * FROM Users WHERE userID = %s;"
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
        query = "SELECT * FROM Users WHERE userID = %s;"
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


@app.route("/", methods=["GET"])
@login_required
def index():
    # Connect to database
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL ViewAllProducts();"
    cursor.execute(query)
    result = cursor.fetchall()
    data = process_products(result)
    cnx.close()
    return render_template("viewProducts.html",
                           user=current_user,
                           products=data)


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    username = request.form.get("username")
    first_name = request.form.get("first_name")
    last_name = request.form.get("last_name")
    password = request.form.get("password")
    password2 = request.form.get("password2")

    if password != password2:
        flash("Passwords do not match")
        return render_template("register.html")

    # Check if username already exists
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    
    cursor = cnx.cursor(prepared=True)
    query = "SELECT * FROM Users WHERE userID = %s;"
    result = []
    try:
        cursor.execute(query, [username])
        result = cursor.fetchall()
    except Exception:
        return redirect(url_for("login"))
    cnx.close()
    if len(result) > 0:
        flash("Username already exists")
        return render_template("register.html")
    else:
        # Connect to database
        cnx = connect(user=DB_USERNAME,
                      password=DB_PASSWORD,
                      database=DB_NAME)
        cursor = cnx.cursor(prepared=True)
        query = "INSERT INTO Users (userID, password_hash, first_name, last_name, admin, seller) VALUES (%s, %s, %s, %s, %s, %s);"
        try:
            cursor.execute(query,
                           (username,
                               base64.b64encode(bcrypt.generate_password_hash(password).decode('utf-8')),
                               first_name,
                               last_name,
                               0,
                               0))
            cnx.commit()
            cnx.close()
        except Exception:
            return redirect(url_for("login"))
        flash("Account created")
        return redirect(url_for("login"))


@app.route("/updateAccount", methods=["GET"])
@login_required
def updateAccount():
    return render_template("updateAccount.html", user=current_user)


@app.route("/updateAccount", methods=["POST"])
@login_required
def updateAccount_post():
    form_name = request.form.get("form_name")
    if form_name == "creditCardForm":
        cardNumber = request.form.get("cardNumber")
        epirationDate = request.form.get("epirationDate")
        cvv = request.form.get("cvv")
        # Connect to database
        cnx = connect(user=DB_USERNAME,
                      password=DB_PASSWORD,
                      database=DB_NAME)
        cursor = cnx.cursor(prepared=True)
        query = "CALL UpdateCreditCard(%s, %s, %s, %s);"
        cursor.execute(query,
                       (cardNumber,
                        epirationDate,
                        cvv,
                        current_user.userID))
        cnx.commit()
        cnx.close()

    elif form_name == "addressForm":
        street = request.form.get("street")
        city = request.form.get("city")
        state = request.form.get("state")
        zipCode = request.form.get("zipCode")
        # Connect to database
        cnx = connect(user=DB_USERNAME,
                      password=DB_PASSWORD,
                      database=DB_NAME)
        cursor = cnx.cursor(prepared=True)
        query = "CALL UpdateAddress(%s, %s, %s, %s, %s);"
        cursor.execute(query,
                       (street,
                        city,
                        state,
                        zipCode,
                        current_user.userID))
        cnx.commit()
        cnx.close()

    flash("Account updated")
    return redirect(url_for("index"))


@app.route("/viewProducts", methods=["GET"])
def viewProducts():
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL ViewAllProducts();"
    cursor.execute(query)
    result = cursor.fetchall()
    data = process_products(result)
    cnx.close()
    return render_template("viewProducts.html",
                           user=current_user,
                           products=data)


@app.route("/productDetail/<string:productID>/<string:category>", methods=["GET", "POST"])
def product_detail(productID, category):
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    product = None
    if category == "Book":
        query = "CALL ViewBook(%s);"
        cursor.execute(query, [productID])
        result = list(cursor.fetchall()[0])
        product = Product(productID=result[1],
                          name=result[5],
                          price=result[6],
                          expiration=result[7],
                          category=category,
                          author=result[2],
                          for_class=result[3])

    elif category == "Ride":
        query = "CALL ViewRide(%s);"
        cursor.execute(query, [productID])
        result = list(cursor.fetchall()[0])
        product = Product(productID=result[1],
                          time=result[2],
                          departureFrom=result[3],
                          seatsAvailable=result[4],
                          category=category,
                          name=result[6],
                          price=result[7],
                          expiration=result[8])
    cnx.close()
    return render_template("productDetail.html",
                           user=current_user,
                           product=product)


# route for books
@app.route("/books", methods=["GET"])
def books():
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL ViewAllBooks();"
    cursor.execute(query)
    result = cursor.fetchall()
    data = process_products(result)
    cnx.close()
    return render_template("books.html",
                           user=current_user,
                           products=data)


if __name__ == "__main__":
    app.run(debug=True)
