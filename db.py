import sqlite3

# Connect to database
conn = sqlite3.connect("food.db")
cur = conn.cursor()

# -----------------------------
# Create Tables
# -----------------------------

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

# -----------------------------
# Insert 10 Food Items
# -----------------------------

food_items = [
    (1, "Pizza", 199),
    (2, "Burger", 99),
    (3, "Biryani", 249),
    (4, "Pasta", 179),
    (5, "Sandwich", 89),
    (6, "FriedRice", 149),
    (7, "Noodles", 139),
    (8, "ChickenRoll", 129),
    (9, "FrenchFries", 79),
    (10, "IceCream", 69)
]

cur.executemany("INSERT OR IGNORE INTO food VALUES (?, ?, ?)", food_items)

# Save & Close
conn.commit()
conn.close()

print("Database created and 10 food items inserted successfully ✅")
