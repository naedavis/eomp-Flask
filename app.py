import hmac
import sqlite3
from flask import Flask, request, jsonify
from flask_mail import Mail, Message
from flask_jwt import JWT, jwt_required, current_identity


# OOP
class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password


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


def identity(payload):
    user_id = payload['identity']
    return userid_table.get(user_id, None)


def authenticate(username, password):
    user = username_table.get(username, None)
    if user and hmac.compare_digest(user.password.encode('utf-8'), password.encode('utf-8')):
        return user


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


init_user_table()
init_post_table()

users = fetch_users()

username_table = {u.username: u for u in users}
userid_table = {u.id: u for u in users}

app = Flask(__name__)
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

    if request.method == "POST":
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        with sqlite3.connect("product_api.db") as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users VALUES(null,"
                           "'"+first_name+"',"
                           "'"+last_name+"',"
                           "'"+username+"',"
                           "'"+password+"')")
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
            if response["status_code"] == 201:
                msg = Message('Registration Successful', sender='lottogirl92@gmail.com', recipients=[email])
                msg.body = "Welcome '"+ str(first_name)+"', You have Successfully Registered as a user of this app"
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
                           "'"+product_name+"',"
                           "'"+description+"',"
                           "'"+category+"',"
                           "'"+price+"')")
            conn.commit()
            response["message"] = "success"
            response["status_code"] = 201
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
        cursor.execute("SELECT * FROM product WHERE product_id='"+str(product_id)+"'")
        product = cursor.fetchone()

    response['status_code'] = 200
    response['data'] = product
    return jsonify(response)


@app.route('/delete/<int:product_id>/')
def delete_product(product_id):
    response = {}

    with sqlite3.connect('product_api.db') as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE product_id='"+str(product_id)+"'")

        conn.commit()
        response['status_code'] = 200
        response['message'] = "product deleted successfully."
    return response


@app.route('/edit/<int:product_id>/', methods=['PUT'])
def edit_products(product_id):
    response = {}

    if request.method == "PUT":
        with sqlite3.connect('product_api.db') as conn:
            incoming_data = dict(request.json)
            put_data = {}

            if incoming_data.get("product_name") is not None:
                put_data["product_name"] = incoming_data.get("product_name")
                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET product_name =? WHERE product_id=?", (put_data["product_name"], product_id))

                    conn.commit()
                    response['message'] = "Update was successfully"
                    response['status_code'] = 200

            elif incoming_data.get("description") is not None:
                put_data['description'] = incoming_data.get('description')

                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET description =? WHERE product_id=?", (put_data["description"], product_id))
                    conn.commit()

                    response["message"] = "Description updated successfully"
                    response["status_code"] = 200

            elif incoming_data.get("category") is not None:
                put_data['category'] = incoming_data.get('category')

                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET category =? WHERE product_id=?", (put_data["category"], product_id))
                    conn.commit()

                    response["message"] = "Category updated successfully"
                    response["status_code"] = 200

            elif incoming_data.get("price") is not None:
                put_data['price'] = incoming_data.get('price')

                with sqlite3.connect('product_api.db') as conn:
                    cursor = conn.cursor()
                    cursor.execute("UPDATE product SET price =? WHERE product_id=?", (put_data["price"], product_id))
                    conn.commit()

                    response["message"] = "Price updated successfully"
                    response["status_code"] = 200
    return response


if __name__ == "__main__":
    app.run(debug=True)
