import sqlite3

def insert_player_data(conn, table_name, dictionary):
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(dictionary))

    sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

    cursor.execute(sql, tuple(dictionary.values()))
    conn.commit()