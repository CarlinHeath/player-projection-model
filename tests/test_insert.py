import sqlite3

import pytest

from src.data_pipeline.clean import (
    clean_hitter_stats,
    clean_pitcher_stats,
    clean_player_info,
    clean_teams_json,
)
from src.data_pipeline.insert import insert_data, insert_player_data
from tests.conftest import SCHEMA, build_database, load_fixture
from tests.test_clean_player_info import make_raw_player

SOTO = {
    "player_id": 665742, "last_name": "Soto", "first_name": "Juan", "full_name": "Juan Soto",
    "birth_date": "1998-10-25", "bats": "L", "throws": "L", "position": "LF", "active": True,
    "debut_date": "2018-05-20", "height_in_inches": 73, "weight_in_pounds": 224,
}


def count_rows(conn, table):
    return conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]


def table_columns(conn, table):
    return [row[1] for row in conn.execute(f"PRAGMA table_info({table})")]


# Cleaner keys must match table columns

def test_player_info_keys_match_players_columns_in_order(db):
    # insert_player_data is positional, so order matters here, not just the names.
    cleaned = clean_player_info(make_raw_player())
    assert list(cleaned.keys()) == table_columns(db, "players")


def test_hitter_keys_match_hitting_table_columns(db):
    # insert_data builds SQL from the keys; any mismatch is a crash or a lost stat.
    row = clean_hitter_stats(load_fixture("soto_hitting.json"))[0]
    columns = [c for c in table_columns(db, "hitting_season_stats") if c != "stat_id"]
    assert sorted(row.keys()) == sorted(columns)


def test_pitcher_keys_match_pitching_table_columns(db):
    row = clean_pitcher_stats(load_fixture("skenes_pitching.json"))[0]
    columns = [c for c in table_columns(db, "pitching_season_stats") if c != "stat_id"]
    assert sorted(row.keys()) == sorted(columns)


def test_team_keys_match_teams_table_columns(db, teams_path):
    assert list(clean_teams_json(teams_path)[0].keys()) == table_columns(db, "teams")


# insert_data

def test_teams_insert_gives_30_rows(db, teams_path):
    insert_data(db, "teams", clean_teams_json(teams_path))
    assert count_rows(db, "teams") == 30


def test_row_count_equals_list_length_after_stat_insert(db, teams_path):
    # Catches the old bug where a loop around executemany turned 10 rows into 100.
    insert_data(db, "teams", clean_teams_json(teams_path))
    insert_player_data(db, "players", SOTO)
    rows = clean_hitter_stats(load_fixture("soto_hitting.json"))
    insert_data(db, "hitting_season_stats", rows)
    assert count_rows(db, "hitting_season_stats") == len(rows)


def test_empty_list_inserts_nothing_and_raises_nothing(db):
    insert_data(db, "teams", [])
    assert count_rows(db, "teams") == 0


def test_second_teams_insert_raises_integrity_error(db, teams_path):
    # team_id is the primary key, so loading teams twice must fail, not duplicate.
    teams = clean_teams_json(teams_path)
    insert_data(db, "teams", teams)
    with pytest.raises(sqlite3.IntegrityError):
        insert_data(db, "teams", teams)


# insert_player_data

def test_player_values_land_in_the_right_columns(db):
    # Positional insert: if the dict order drifted, height could land in weight.
    insert_player_data(db, "players", SOTO)
    db.row_factory = sqlite3.Row
    stored = dict(db.execute("SELECT * FROM players").fetchone())
    assert stored["last_name"] == "Soto"
    assert stored["position"] == "LF"
    assert stored["height_in_inches"] == 73
    assert stored["weight_in_pounds"] == 224


def test_duplicate_player_raises_integrity_error(db):
    insert_player_data(db, "players", SOTO)
    with pytest.raises(sqlite3.IntegrityError):
        insert_player_data(db, "players", SOTO)


# Foreign keys

def test_stat_row_with_unknown_team_is_rejected_when_pragma_on(db):
    # The pragma is what stops a stat row pointing at a team that does not exist.
    insert_player_data(db, "players", SOTO)
    with pytest.raises(sqlite3.IntegrityError):
        insert_data(db, "hitting_season_stats", [{"season": "2025", "player_id": 665742, "team_id": 9999}])


def test_stat_row_with_unknown_team_is_accepted_when_pragma_off():
    # Shows why every connection needs the pragma: without it, SQLite does not check.
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA.read_text())
    insert_data(conn, "hitting_season_stats", [{"season": "2025", "player_id": 1, "team_id": 9999}])
    assert count_rows(conn, "hitting_season_stats") == 1
    conn.close()


# Commits

def test_insert_functions_do_not_commit(tmp_path):
    # The pipeline owns commits; a second connection must not see uncommitted rows.
    path = tmp_path / "test.db"
    writer = build_database(sqlite3.connect(path))
    writer.commit()
    insert_player_data(writer, "players", SOTO)
    reader = sqlite3.connect(path)
    assert count_rows(reader, "players") == 0
    reader.close()
    writer.close()


def test_rows_persist_through_a_fresh_connection_after_commit(tmp_path):
    path = tmp_path / "test.db"
    writer = build_database(sqlite3.connect(path))
    insert_player_data(writer, "players", SOTO)
    writer.commit()
    writer.close()
    reader = sqlite3.connect(path)
    assert count_rows(reader, "players") == 1
    reader.close()
