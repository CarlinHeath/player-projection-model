from datetime import date

def clean_player_info(original_data):
    dirty_data = original_data["people"][0]

    return {
        "player_id": dirty_data.get("id"),
        "last_name": dirty_data.get("useLastName"),
        "first_name": dirty_data.get("useName"),
        "full_name": dirty_data.get("nameFirstLast"),
        "birth_date": _create_date(dirty_data, "birthDate"),
        "bats": _get_nested_data(dirty_data, "batSide", "code"),
        "throws": _get_nested_data(dirty_data, "pitchHand", "code"),
        "position": _get_nested_data(dirty_data, "primaryPosition", "abbreviation"),
        "active": dirty_data.get("active"),
        "debut_date": _create_date(dirty_data, "mlbDebutDate"),
        "height_in_inches": _convert_height(dirty_data.get("height")),
        "weight_in_pounds": dirty_data.get("weight")
    }

def clean_hitter_stats(original_data):
    dirty_data = original_data
    clean_data = {}

    return clean_data

def clean_pitcher_stats(original_data):
    dirty_data = original_data
    clean_data = {}

    return clean_data

def _create_date(dictionary, key):
    try:
        return date.fromisoformat(dictionary.get(key))
    except TypeError:
        return None
    except ValueError:
        return None

def _get_nested_data(dictionary, outer_key, inner_key):
    try:
        return dictionary.get(outer_key).get(inner_key)
    except:
        return None


def _convert_height(height):
    try:
        feet, inches = height.replace('"', '').split("'")
    except:
        return None
    try:    
        return (int(feet) * 12) + int(inches)
    except:
        return None