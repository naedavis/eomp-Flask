import hmac
import sqlite3
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_jwt import JWT, jwt_required, current_identity
from flask_cors import CORS


# OOP
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


# function that fetches all the users from the user table in the Products Database
def fetch_users():
    with sqlite3.connect('product_api.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        new_data = []
        #       for loop
        for data in users:
            new_data.append(User(data[0], data[3], data[4]))
    return new_data


# Function that creates the Table that will contain all the users and their information in the Database if it hasn't
# been created yet
def init_user_table():
    conn = sqlite3.connect('product_api.db')
    #   table users that will hold the first name, last name, username and password of the users
    conn.execute("CREATE TABLE IF NOT EXISTS users(user_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                 "first_name TEXT NOT NULL,"
                 "last_name TEXT NOT NULL,"
                 "username TEXT NOT NULL,"
                 "password TEXT NOT NULL)")


# Function that creates the Table that will contain all the products and their description in the Database if it hasn't
# been created yet
def init_post_table():
    with sqlite3.connect('product_api.db') as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS product(product_id INTEGER PRIMARY KEY AUTOINCREMENT,"
                     "product_name TEXT NOT NULL,"
                     "description TEXT NOT NULL,"
                     "category TEXT NOT NULL,"
                     "price TEXT NOT NULL)")
    conn.close()


# functions being called to create the User and Product tables in the database
init_user_table()
init_post_table()

# function that fetches the user for login purposes stored in a variable
users = fetch_users()

# variable that are getting the username and id of the users
username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

app = Flask(__name__)
CORS(app)
# cors = CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:5500/"}})
# ?app.config['CORS_HEADERS'] = 'Content-Type'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'lottogirl92@gmail.com'
app.config['MAIL_PASSWORD'] = 'loahdtTvc473!&'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)
app.config['SECRET_KEY'] = 'super-secret'

jwt = JWT(app, authenticate, identity)


@app.route('/protected/')
@jwt_required()
def protected():
    return '%s' % current_identity


@app.route('/registration/', methods=['POST'])
def add_user():
    response = {}

    #   when the user registers, the http method in the form is post so it will send the names, username,
    #   password to the database
    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        #       the email entered will not be added to the database because it is only being used to inform
        #       the user of their successful registration
        email = request.form['email']
        #       using the database created  to insert the input values from the user
        with sqlite3.connect("product_api.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users VALUES(null,"
                           "'" + first_name + "',"
                                              "'" + last_name + "',"
                                                                "'" + username + "',"
                                                                                 "'" + password + "')")
            conn.commit()
            response["status_code"] = 201
            response["message"] = " registration success"
            if response["status_code"] == 201:
                msg = Message('Registration Successful', sender='lottogirl92@gmail.com', recipients=[email])
                msg.body = "Welcome '" + str(first_name) + "', You have Successfully Registered as a user of this app"
                mail.send(msg)
                return "Sent email"


@app.route('/add_products/', methods=['POST'])
@jwt_required()
def add_products():
    response = {}

    if request.method == "POST":
        product_name = request.form['product_name']
        description = request.form['description']
        category = request.form['category']
        price = request.form['price']

        with sqlite3.connect("product_api.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO product VALUES(null,"
                           "'" + product_name + "',"
                                                "'" + description + "',"
                                                                    "'" + category + "',"
                                                                                     "'" + price + "')")
            conn.commit()
            response["status_code"] = 201
            response["message"] = "Product added successfully"
        return response


@app.route('/view_products/')
def view_products():
    response = {}

    with sqlite3.connect("product_api.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product")
        product = cursor.fetchall()

    response['status_code'] = 200
    response['data'] = product
    return jsonify(response)


@app.route('/view_product/<int:product_id>/')
def view_product(product_id):
    response = {}
    with sqlite3.connect("product_api.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM product WHERE product_id='" + str(product_id) + "'")
        product = cursor.fetchone()

    response['status_code'] = 200
    response['data'] = product
    return jsonify(response)


@app.route('/delete/<int:product_id>/')
def delete_product(product_id):
    response = {}

    with sqlite3.connect('product_api.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE product_id='" + str(product_id) + "'")

        conn.commit()
        response['status_code'] = 200
        response['message'] = "product deleted successfully."
    return response


@app.route('/edit/<int:product_id>/', methods=['PUT'])
# update function which allows the user to update a product and it's information
def edit_products(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('product_api.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}
            # Conditional Statement
            # if the user chooses to change the product name
            if incoming_data.get("product_name") is not None:
                put_data["product_name"] = incoming_data.get("product_name")
                # in the database table
                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    # update the product name to the name the user chooses
                    cursor.execute(
                        "UPDATE product SET product_name ='" + (
                            put_data["product_name"]) + "' WHERE product_id='" + str(
                            product_id) + "'")
                    conn.commit()
                    response['status_code'] = 200
                    response['message'] = " Product Name updated successfully"
            # if the user chooses to update the description
            elif incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')
                #
                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE product SET description ='" + (
                            put_data["description"]) + "' WHERE product_id='" + str(
                            product_id) + "'")
                    conn.commit()

                    response["status_code"] = 200
                    response["message"] = "Description updated successfully"

            elif incoming_data.get("category") is not None:
                put_data['category'] = incoming_data.get('category')

                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE product SET category ='" + (
                            put_data["category"]) + "' WHERE product_id='" + str(
                            product_id) + "'")
                    conn.commit()
                    response["status_code"] = 200
                    response["message"] = "Category updated successfully"

            elif incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE product SET price ='"+(
                            put_data["price"])+"'WHERE product_id='"+str(product_id)+"'" )
                    conn.commit()

                    response["status_code"] = 200
                    response["message"] = "Price updated successfully"
    return response


if __name__ == "__main__":
    app.run(debug=True)