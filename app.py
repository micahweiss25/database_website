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


class Bid:
    def __init__(self,
                 productID,
                 amount,
                 bidder):
        self.productID = productID
        self.amount = amount
        self.bidder = bidder


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
        result = cursor.fetchall()
        cnx.close()
    except Exception as e:
        print(f"Error: failed to query database due to {e}")
        raise e
    if len(result) > 0:
        result = result[0]
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
                           current_user=current_user,
                           products=data)


@app.route("/register", methods=["GET"])
def register():
    return render_template("register.html")


@app.route("/register", methods=["POST"])
def register_post():
    userID = request.form.get("username")
    password = request.form.get("password")
    password2 = request.form.get("password2")
    firstName = request.form.get("first_name")
    lastName = request.form.get("last_name")
    admin = 0
    seller = 0
    creditCard = request.form.get("creditCard")
    expirationDate = request.form.get("expirationDate")
    securityCode = request.form.get("securityCode")
    street = request.form.get("street")
    city = request.form.get("city")
    state = request.form.get("state")
    _zip = request.form.get("zip")

    if password != password2:
        flash("Passwords do not match")
        return render_template("register.html")

    # Check if username already exists
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    
    cursor = cnx.cursor(prepared=True)
    query = "CALL AddUser(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);"
    data = [userID,
            base64.b64encode(bcrypt.generate_password_hash(password)),
            firstName,
            lastName,
            admin,
            seller,
            creditCard,
            expirationDate,
            securityCode,
            street,
            city,
            state,
            _zip]
    cursor.execute(query,
                    data)
    cnx.commit()
    cnx.close()
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
    if category == 'Book':
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
        # raise Exception(result)
        product = Product(productID=result[1],
                          time=result[2],
                          departureFrom=result[3],
                          seatsAvailable=result[4],
                          category=category,
                          name=result[6],
                          price=result[7],
                          expiration=result[8])
    # raise Exception(productID)
    query = "CALL GetBidsForProduct(%s);"
    cnx.close()
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    cursor.execute(query, [productID])
    results = cursor.fetchall()
    bids = []
    for bid in results:
        new_bid = Bid(productID=bid[2],
                      amount=bid[3],
                      bidder=bid[1])
        bids.append(new_bid)

    cnx.close()
    return render_template("productDetail.html",
                           user=current_user,
                           product=product,
                           bids=bids)


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
    products = []
    for product in result:
        new_product = Product(productID=product[1],
                          name=product[5],
                          price=product[6],
                          expiration=product[7],
                          category='Book',
                          author=product[2],
                          for_class=product[3])
        products.append(new_product)
    cnx.close()
    return render_template("books.html",
                           user=current_user,
                           products=products)


# route for rides
@app.route("/rides", methods=["GET"])
def rides():
    cnx = connect(user=DB_USERNAME,
                  password=DB_PASSWORD,
                  database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL ViewAllRides();"
    cursor.execute(query)
    result = cursor.fetchall()
    products = []
    for product in result:
        new_product = Product(productID=product[1],
                          time=product[2],
                          departureFrom=product[3],
                          seatsAvailable=product[4],
                          category='Ride',
                          name=product[6],
                          price=product[7],
                          expiration=product[8])
        products.append(new_product)
    cnx.close()
    return render_template("rides.html",
                           user=current_user,
                           products=products)


@app.route("/listProduct", methods=["GET"])
def listProduct():
    return render_template("listProduct.html",
                           user=current_user)


@app.route("/create_book", methods=["POST"])
def create_book():
    name = request.form.get("name")
    startingPrice = request.form.get("startingPrice")
    nltDate = request.form.get("nltDate")
    author = request.form.get("author")
    for_class = request.form.get("class")
    # Connect to database
    cnx = connect(user=DB_USERNAME,
                    password=DB_PASSWORD,
                    database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL ListBook(%s, %s, %s, %s, %s, %s);"
    cursor.execute(query,
                   (name,
                    startingPrice,
                    nltDate,
                    author,
                    for_class,
                    current_user.get_id()))
    cnx.commit()
    cnx.close()
    flash("Book listed")
    return redirect(url_for("index"))


@app.route("/create_ride", methods=["POST"])
def create_ride():
    name = request.form.get("name")
    startingPrice = request.form.get("startingPrice")
    nltDate = request.form.get("nltDate")
    time = request.form.get("time")
    departureFrom = request.form.get("departureFrom")
    seatsAvailable = request.form.get("seatsAvailable")
    # Connect to database
    cnx = connect(user=DB_USERNAME,
                    password=DB_PASSWORD,
                    database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL ListRide(%s, %s, %s, %s, %s, %s, %s);"
    cursor.execute(query,
                    (name,
                    startingPrice,
                    nltDate,
                    time,
                    departureFrom,
                    seatsAvailable,
                    current_user.get_id()))
    cnx.commit()
    cnx.close()
    flash("Ride listed")
    return redirect(url_for("index"))


@app.route("/bid", methods=["GET"])
def bid():
    # productID = request.form.get("productID")
    productID = request.args.get("productID")

    bidAmount = request.args.get("bid")
    # Connect to database
    cnx = connect(user=DB_USERNAME,
                    password=DB_PASSWORD,
                    database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL BidOnProduct(%s, %s, %s);"
    cursor.execute(query,
                    (current_user.get_id(),
                    productID,
                    bidAmount))
    result = cursor.fetchall()

    cnx.close()
    flash("Bid placed")
    return redirect(url_for("index"))


@app.route("/bid", methods=["POST"])
def bid_post():
    raise Exception("should not have posted")


@app.route("/removeUser", methods=["GET"])
def removeUser():
    cnx = connect(user=DB_USERNAME,
                password=DB_PASSWORD,
                database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "SELECT * FROM Users;"
    cursor.execute(query)
    result = cursor.fetchall()
    users = []
    for user in result:
        users.append(user[0])

    cnx.close()

    return render_template("removeUser.html",
                           user=current_user,
                           users=users)


@app.route("/removeUser", methods=["POST"])
def removeUser_post():
    userID = request.form.get("userID")
    # Connect to database
    cnx = connect(user=DB_USERNAME,
                    password=DB_PASSWORD,
                    database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL RemoveUser(%s);"
    cursor.execute(query,
                    [userID])
    cnx.commit()
    cnx.close()
    flash("User removed")
    return redirect(url_for("index"))


@app.route("/removeProduct", methods=["GET"])
def removeProduct():
    cnx = connect(user=DB_USERNAME,
                password=DB_PASSWORD,
                database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    query = "CALL ViewAllProducts();"
    cursor.execute(query)
    result = cursor.fetchall()
    data = process_products(result)
    cnx.close()
    return render_template("removeProduct.html",
                           user=current_user,
                           products=data)


@app.route("/removeProduct/<string:productID>/<string:category>", methods=["POST", "GET"])
def removeProduct_post(productID, category):
    # Connect to database
    cnx = connect(user=DB_USERNAME,
                    password=DB_PASSWORD,
                    database=DB_NAME)
    cursor = cnx.cursor(prepared=True)
    if category == 'Book':
        query = "CALL RemoveBook(%s);"
    elif category == 'Ride':
        query = "CALL RemoveRide(%s)"
    cursor.execute(query,
                    [productID])
    cnx.commit()
    cnx.close()
    flash("Product removed")
    return redirect(url_for("index"))



if __name__ == "__main__":
    app.run(debug=True)
