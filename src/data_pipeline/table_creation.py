import sqlite3
import os
from src.data_pipeline import fetch, clean, insert

# Soto, Witt, Franklin Arias, Cole, Skenes, Kershaw, Ohtani, Miller, J. Ramirez, L. Walker
players = [665742, 677951, 808265, 543037, 694973, 477132, 660271, 695243, 608070, 123833]

if os.path.exists("data/player_projection.db"):
    os.remove("data/player_projection.db")

connection = sqlite3.connect("data/player_projection.db")
connection.execute("PRAGMA foreign_keys = ON")

with open("database/schema.sql", "r") as f:
    schema = f.read()

connection.executescript(schema)
connection.commit()

print("Database created successfully.")

insert.insert_data(connection, "teams", clean.clean_teams_json("data/teams.json"))
connection.commit()

for player in players:
    print(f"Loading player {player}")

    player_info = clean.clean_player_info(fetch.fetch_player_info(player))
    player_hitter_stats = clean.clean_hitter_stats(fetch.fetch_hitter_stats(player))
    player_pitching_stats = clean.clean_pitcher_stats(fetch.fetch_pitcher_stats(player))
    
    insert.insert_player_data(connection, "players", player_info)

    if player_hitter_stats:
        insert.insert_data(connection, "hitting_season_stats", player_hitter_stats)

    if player_pitching_stats:
        insert.insert_data(connection, "pitching_season_stats", player_pitching_stats)

    connection.commit()

connection.close()