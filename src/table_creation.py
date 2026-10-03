import sqlite3

connection = sqlite3.connect("data/player_projection.db")
with open("database/schema.sql", "r") as f:
    schema = f.read()

connection.executescript(schema)
connection.commit()
connection.close()

print("Database created successfully.")