import sqlite3

conn = sqlite3.connect("sensors.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS sensors(
id INTEGER PRIMARY KEY AUTOINCREMENT,
temperature REAL,
humidity REAL,
pressure REAL,
time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()
