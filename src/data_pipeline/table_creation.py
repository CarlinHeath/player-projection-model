import sqlite3
from src.data_pipeline import fetch, clean, insert

# Sota, Witt, Franklin Arias, Cole, Kershaw, Skenes, Ohtani, Miller
players = [665742, 677951, 808265, 543037, 694973, 477132, 660271, 695243]

connection = sqlite3.connect("data/player_projection.db")
with open("database/schema.sql", "r") as f:
    schema = f.read()

connection.executescript(schema)
connection.commit()

print("Database created successfully.")

for player in players:
    insert.insert_player_data(connection, "players", clean.clean_player_info(fetch.fetch_player_info(player)))

connection.close()