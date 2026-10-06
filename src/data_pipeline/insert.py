def insert_data(conn, table_name, data_list):
    cursor = conn.cursor()

    for dictionary in data_list:
        columns = ", ".join(dictionary.keys())
        placeholders = ", ".join(f":{key}" for key in dictionary)

        sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"

        cursor.execute(sql, dictionary)

def insert_player_data(conn, table_name, dictionary):
    cursor = conn.cursor()

    placeholders = ', '.join(['?'] * len(dictionary))

    sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

    cursor.execute(sql, tuple(dictionary.values()))