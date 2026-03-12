import sqlite3

conn = sqlite3.connect("create_db.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT UNIQUE,
password TEXT
)
""")

conn.commit()
conn.close()

print("Database created")