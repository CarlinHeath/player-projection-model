import pytest

from src.data_pipeline.clean import clean_hitter_stats, clean_pitcher_stats, clean_teams_json
from tests.conftest import load_fixture


def find_rows(rows, season, team_id=None):
    return [r for r in rows if r["season"] == season and (team_id is None or r["team_id"] == team_id)]


# Soto hitting

def test_soto_skips_the_combined_2022_row():
    # 11 raw splits include one multi-team total; storing it would double-count 2022.
    rows = clean_hitter_stats(load_fixture("soto_hitting.json"))
    assert len(rows) == 10


def test_soto_2022_keeps_both_team_rows():
    # Traded mid-season: one row for Washington (120), one for San Diego (135).
    rows = clean_hitter_stats(load_fixture("soto_hitting.json"))
    assert find_rows(rows, "2022", 120)[0]["games_played"] == 101
    assert find_rows(rows, "2022", 135)[0]["games_played"] == 52
    assert len(find_rows(rows, "2022")) == 2


def test_soto_2025_matches_known_values():
    # Checked by hand against the real response.
    rows = clean_hitter_stats(load_fixture("soto_hitting.json"))
    row = find_rows(rows, "2025")[0]
    assert row["games_played"] == 160
    assert row["home_runs"] == 43
    assert row["stolen_bases"] == 38
    assert row["at_bats"] == 577


def test_soto_rows_have_no_none_values():
    # A None here means a misspelled API key (like the strikeoutsPer9Inn bug).
    for row in clean_hitter_stats(load_fixture("soto_hitting.json")):
        assert None not in row.values(), row["season"]


def test_soto_rows_all_have_the_same_30_keys():
    rows = clean_hitter_stats(load_fixture("soto_hitting.json"))
    assert len(rows[0]) == 30
    assert all(row.keys() == rows[0].keys() for row in rows)


# Skenes pitching

def test_skenes_2024_matches_known_values():
    rows = clean_pitcher_stats(load_fixture("skenes_pitching.json"))
    row = find_rows(rows, "2024")[0]
    assert row["games_played"] == 23
    assert row["games_started"] == 23
    assert row["strike_outs"] == 170
    assert (row["wins"], row["losses"]) == (11, 3)
    assert row["outs"] == 399
    assert row["batters_faced"] == 514
    assert row["earned_run_average"] == 1.96


def test_skenes_outs_are_stored_as_integers():
    # Outs replace "innings pitched" text like "133.0", which adds wrongly as floats.
    rows = clean_pitcher_stats(load_fixture("skenes_pitching.json"))
    assert [row["outs"] for row in rows] == [399, 563, 523]
    assert all(isinstance(row["outs"], int) for row in rows)


def test_skenes_rows_have_44_keys_and_no_none_values():
    rows = clean_pitcher_stats(load_fixture("skenes_pitching.json"))
    assert len(rows) == 3
    for row in rows:
        assert len(row) == 44
        assert None not in row.values(), row["season"]


# Miller pitching

def test_miller_skips_the_combined_2025_row():
    rows = clean_pitcher_stats(load_fixture("miller_pitching.json"))
    assert len(rows) == 5
    assert {r["team_id"] for r in find_rows(rows, "2025")} == {133, 135}


def test_miller_2025_team_rows_sum_to_the_combined_row():
    # This is what lets us skip the combined row without losing season totals.
    raw = load_fixture("miller_pitching.json")
    combined = next(s["stat"] for s in raw["stats"][0]["splits"] if s.get("numTeams"))
    rows = find_rows(clean_pitcher_stats(raw), "2025")
    pairs = {
        "outs": "outs", "games_played": "gamesPlayed", "batters_faced": "battersFaced",
        "strike_outs": "strikeOuts", "saves": "saves", "holds": "holds",
    }
    for column, api_key in pairs.items():
        assert sum(r[column] for r in rows) == combined[api_key], column


def test_miller_role_change_shows_in_the_rows():
    # 2023 he started some games; 2024 he was a closer.
    rows = clean_pitcher_stats(load_fixture("miller_pitching.json"))
    assert find_rows(rows, "2023")[0]["games_started"] == 6
    row_2024 = find_rows(rows, "2024")[0]
    assert (row_2024["saves"], row_2024["save_opportunities"]) == (28, 31)


# Empty and bad responses

def test_stats_empty_response_is_falsy_so_the_pipeline_skips_it():
    # The pipeline uses a plain `if`, so None and [] both work; this test allows either.
    assert not clean_hitter_stats({"stats": []})
    assert not clean_pitcher_stats({"stats": []})


def test_stats_bad_id_response_is_falsy():
    # Observed: the fake-ID error dict has no "stats" key.
    error_response = {"messageNumber": 10, "message": "Object not found", "traceId": "abc"}
    assert not clean_hitter_stats(error_response)


def test_stats_block_with_empty_splits_raises_index_error():
    # Not seen from the real API yet, but this is what would happen today.
    with pytest.raises(IndexError):
        clean_hitter_stats({"stats": [{"splits": []}]})


# Teams

def test_teams_file_gives_30_unique_teams_with_no_none(teams_path):
    teams = clean_teams_json(teams_path)
    assert len(teams) == 30
    assert len({t["team_id"] for t in teams}) == 30
    for team in teams:
        assert None not in team.values(), team["team_id"]


def test_teams_known_values(teams_path):
    teams = {t["team_id"]: t for t in clean_teams_json(teams_path)}
    assert teams[120] == {
        "team_id": 120, "name": "Washington Nationals",
        "league": "National League", "division": "National League East",
    }
    assert teams[133]["name"] == "Athletics"
    assert teams[133]["division"] == "American League West"


def test_teams_split_into_2_leagues_and_6_divisions_of_5(teams_path):
    teams = clean_teams_json(teams_path)
    assert len({t["league"] for t in teams}) == 2
    divisions = [t["division"] for t in teams]
    assert len(set(divisions)) == 6
    assert all(divisions.count(d) == 5 for d in set(divisions))


def test_missing_teams_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        clean_teams_json(tmp_path / "missing.json")


def test_teams_error_response_raises_key_error(tmp_path):
    # If team_refresh ever saved an error response, the load should fail loudly.
    bad_file = tmp_path / "teams.json"
    bad_file.write_text('{"messageNumber": 10, "message": "error"}')
    with pytest.raises(KeyError):
        clean_teams_json(bad_file)
