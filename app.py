from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

# ----------------------------
# DATABASE CREATION SECTION
# ----------------------------

db = sqlite3.connect("food.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    name TEXT,
    email TEXT,
    password TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS food (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price INTEGER
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    address TEXT,
    food_id INTEGER,
    payment TEXT
)
""")

db.commit()
db.close()

# ----------------------------
# ROUTES START HERE
# ----------------------------
# Home Page - Show Menu
@app.route("/")
def home():
    db = sqlite3.connect("food.db")
    cur = db.cursor()
    cur.execute("SELECT * FROM food")
    foods = cur.fetchall()
    db.close()
    return render_template("index.html", foods=foods)


# Order Page
@app.route("/order/<int:food_id>")
def order(food_id):
    return render_template("order.html", food_id=food_id)


# Save Order
@app.route("/submit_order", methods=["POST"])
def submit_order():
    name = request.form["name"]
    phone = request.form["phone"]
    address = request.form["address"]
    food_id = request.form["food_id"]
    payment = request.form["payment"]

    db = sqlite3.connect("food.db")
    cur = db.cursor()

    cur.execute("""
        INSERT INTO orders (name, phone, address, food_id, payment)
        VALUES (?, ?, ?, ?, ?)
    """, (name, phone, address, food_id, payment))

    db.commit()
    db.close()

    return "<h2>Order Placed Successfully 🎉</h2><a href='/'>Go Back</a>"
@app.route("/view_orders")
def view_orders():
    db = sqlite3.connect("food.db")
    cur = db.cursor()

    cur.execute("""
        SELECT orders.id, orders.name, orders.phone, orders.address, 
               food.name, orders.payment
        FROM orders
        JOIN food ON orders.food_id = food.id
    """)

    orders = cur.fetchall()
    db.close()

    return render_template("view_orders.html", orders=orders)


if __name__ == "__main__":
    app.run(debug=True)
 