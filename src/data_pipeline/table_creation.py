import sqlite3
import os
from src.data_pipeline import fetch, clean, insert

# Sota, Witt, Franklin Arias, Cole, Skenes, Kershaw, Ohtani, Miller, J. Ramirez, L. Walker
players = [665742, 677951, 808265, 543037, 694973, 477132, 660271, 695243, 608070, 123833]

if os.path.exists("data/player_projection.db"):
    os.remove("data/player_projection.db")

connection = sqlite3.connect("data/player_projection.db")
with open("database/schema.sql", "r") as f:
    schema = f.read()

connection.executescript(schema)
connection.commit()

print("Database created successfully.")

for player in players:
    insert.insert_player_data(connection, "players", clean.clean_player_info(fetch.fetch_player_info(player)))
    clean.clean_hitter_stats(fetch.fetch_hitter_stats(player))

connection.close()