from datetime import date

from src.data_pipeline.clean import (
    _convert_float,
    _convert_height,
    _create_date,
    _get_nested_data,
)


# _convert_height

def test_height_converts_feet_and_inches_to_total_inches():
    # Normal API format; every player's height goes through this.
    assert _convert_height("6'1\"") == 73
    assert _convert_height("6'10\"") == 82
    assert _convert_height("5'5\"") == 65


def test_height_handles_space_and_zero_inches():
    # The API writes Devers as 6' 0"; the space and the 0 must not break it.
    assert _convert_height("6' 0\"") == 72


def test_height_returns_none_for_missing_value():
    # A player with no height on file should not crash the load.
    assert _convert_height(None) is None
    assert _convert_height("") is None


def test_height_returns_none_for_wrong_format():
    # Metric or half-written heights are bad data, not a crash.
    assert _convert_height("183 cm") is None
    assert _convert_height("6'") is None


# _create_date

def test_date_parses_valid_iso_string():
    # Birth and debut dates arrive as "YYYY-MM-DD" text.
    assert _create_date({"mlbDebutDate": "2018-05-20"}, "mlbDebutDate") == date(2018, 5, 20)


def test_date_returns_none_when_key_missing():
    # Prospects like Arias have no debut date key at all.
    assert _create_date({}, "mlbDebutDate") is None


def test_date_returns_none_when_value_is_none():
    # A key present with a null value must behave like a missing key.
    assert _create_date({"mlbDebutDate": None}, "mlbDebutDate") is None


def test_date_returns_none_for_garbled_string():
    # Decided: an impossible date becomes None instead of crashing.
    assert _create_date({"mlbDebutDate": "2018-13-45"}, "mlbDebutDate") is None
    assert _create_date({"mlbDebutDate": ""}, "mlbDebutDate") is None


# _get_nested_data

def test_nested_returns_inner_value():
    # Normal case: batSide.code gives "L".
    assert _get_nested_data({"batSide": {"code": "L"}}, "batSide", "code") == "L"


def test_nested_returns_none_when_outer_key_missing():
    # A player record without the block should not crash.
    assert _get_nested_data({}, "batSide", "code") is None


def test_nested_returns_none_when_outer_value_is_none():
    assert _get_nested_data({"batSide": None}, "batSide", "code") is None


def test_nested_returns_none_when_inner_key_missing():
    assert _get_nested_data({"batSide": {}}, "batSide", "code") is None


def test_nested_returns_none_when_outer_value_is_not_a_dict():
    # If the API ever flattens the block to a plain string, we get None, not a crash.
    assert _get_nested_data({"batSide": "L"}, "batSide", "code") is None


# _convert_float

def test_float_converts_api_rate_strings():
    # The API sends rates like batting average and ERA as text.
    assert _convert_float(".263") == 0.263
    assert _convert_float("2.60") == 2.6


def test_float_accepts_an_int():
    assert _convert_float(263) == 263.0


def test_float_returns_none_for_placeholder():
    # ".---" is the API's "no value" marker for rates with a zero denominator.
    assert _convert_float(".---") is None


def test_float_returns_none_for_missing_or_junk():
    assert _convert_float(None) is None
    assert _convert_float("") is None
    assert _convert_float("abc") is None
