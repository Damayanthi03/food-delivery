import sqlite3

db = sqlite3.connect("food.db")
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS food (
    id INTEGER PRIMARY KEY,
    name TEXT,
    price INTEGER
)
""")

foods = [
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

cur.executemany("INSERT OR IGNORE INTO food VALUES (?,?,?)", foods)

db.commit()
db.close()

print("10 food items added successfully")
