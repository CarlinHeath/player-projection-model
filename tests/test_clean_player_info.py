from datetime import date

import pytest

from src.data_pipeline.clean import clean_player_info


def make_raw_player(**overrides):
    """A hand-built player record shaped like the /people/{id} response."""
    person = {
        "id": 677951,
        "firstName": "Robert",
        "useName": "Bobby",
        "useLastName": "Witt Jr.",
        "nameFirstLast": "Bobby Witt Jr.",
        "birthDate": "2000-06-14",
        "batSide": {"code": "R"},
        "pitchHand": {"code": "R"},
        "primaryPosition": {"abbreviation": "SS"},
        "active": True,
        "mlbDebutDate": "2022-04-07",
        "height": "6' 1\"",
        "weight": 200,
    }
    person.update(overrides)
    return {"people": [person]}


def test_player_info_returns_the_twelve_columns_in_table_order():
    # insert_player_data has no column list, so key order must match the players table.
    expected = [
        "player_id", "last_name", "first_name", "full_name", "birth_date", "bats",
        "throws", "position", "active", "debut_date", "height_in_inches", "weight_in_pounds",
    ]
    assert list(clean_player_info(make_raw_player()).keys()) == expected


def test_player_info_uses_preferred_names_not_legal_names():
    # Witt's legal first name is Robert; we store the name he goes by and keep the suffix.
    player = clean_player_info(make_raw_player())
    assert player["first_name"] == "Bobby"
    assert player["last_name"] == "Witt Jr."


def test_player_info_converts_nested_fields_dates_and_height():
    player = clean_player_info(make_raw_player())
    assert player["bats"] == "R"
    assert player["position"] == "SS"
    assert player["birth_date"] == date(2000, 6, 14)
    assert player["height_in_inches"] == 73


def test_player_info_prospect_without_debut_gets_none():
    # Arias case: the key is simply absent for players who have not debuted.
    raw = make_raw_player()
    del raw["people"][0]["mlbDebutDate"]
    assert clean_player_info(raw)["debut_date"] is None


def test_player_info_bad_id_raises_key_error():
    # Observed: a fake ID returns an error dict with no "people" key.
    error_response = {"messageNumber": 10, "message": "Object not found", "traceId": "abc"}
    with pytest.raises(KeyError):
        clean_player_info(error_response)


def test_player_info_empty_people_raises_index_error():
    with pytest.raises(IndexError):
        clean_player_info({"people": []})
