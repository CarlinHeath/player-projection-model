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
    if not original_data.get("stats"):
        return

    dirty_data = original_data["stats"][0]["splits"]
    player_id = dirty_data[0].get("player").get("id")
    season_stats = []

    for season in dirty_data:
        if season.get("numTeams"):
            continue

        season_stats += [{
            "age": _get_nested_data(season, "stat", "age"),
            "season": season.get("season"),
            "games_played": _get_nested_data(season, "stat", "gamesPlayed"),
            "plate_appearances": _get_nested_data(season, "stat", "plateAppearances"),
            "ground_outs": _get_nested_data(season, "stat", "groundOuts"),
            "air_outs": _get_nested_data(season, "stat", "airOuts"),
            "runs": _get_nested_data(season, "stat", "runs"),
            "doubles":_get_nested_data(season, "stat", "doubles"),
            "triples": _get_nested_data(season, "stat", "triples"),
            "home_runs": _get_nested_data(season, "stat", "homeRuns"),
            "strike_outs": _get_nested_data(season, "stat", "strikeOuts"),
            "base_on_balls": _get_nested_data(season, "stat", "baseOnBalls"),
            "intentional_walks": _get_nested_data(season, "stat", "intentionalWalks"),
            "hit_by_pitch": _get_nested_data(season, "stat", "hitByPitch"),
            "hits": _get_nested_data(season, "stat", "hits"),
            "at_bats": _get_nested_data(season, "stat", "atBats"),
            "batting_average": _convert_float(_get_nested_data(season, "stat", "avg")),
            "on_base_percentage": _convert_float(_get_nested_data(season, "stat", "obp")),
            "slugging": _convert_float(_get_nested_data(season, "stat", "slg")),
            "on_base_plus_slugging": _convert_float(_get_nested_data(season, "stat", "ops")),
            "stolen_bases": _get_nested_data(season, "stat", "stolenBases"),
            "caught_stealing": _get_nested_data(season, "stat", "caughtStealing"),
            "number_of_pitches": _get_nested_data(season, "stat", "numberOfPitches"),
            "runs_batted_in": _get_nested_data(season, "stat", "rbi"),
            "batting_average_on_balls_in_play": _convert_float(_get_nested_data(season, "stat", "babip")),
            "sacrifice_bunts": _get_nested_data(season, "stat", "sacBunts"),
            "sacrifice_flies": _get_nested_data(season, "stat", "sacFlies"),
            "catcher_interference": _get_nested_data(season, "stat", "catchersInterference"),
            "player_id": player_id,
            "team_id": season.get("team").get("id")
        }]

    return season_stats

def clean_pitcher_stats(original_data):
    if not original_data.get("stats"):
        return

    dirty_data = original_data["stats"][0]["splits"]
    player_id = dirty_data[0].get("player").get("id")
    season_stats = []

    for season in dirty_data:
        if season.get("numTeams"):
            continue

        season_stats += [{
            "age": _get_nested_data(season, "stat", "age"),
            "season": season.get("season"),
            "games_played": _get_nested_data(season, "stat", "gamesPlayed"),
            "games_started": _get_nested_data(season, "stat", "gamesStarted"),
            "ground_outs": _get_nested_data(season, "stat", "groundOuts"),
            "air_outs": _get_nested_data(season, "stat", "airOuts"),
            "runs": _get_nested_data(season, "stat", "runs"),
            "home_runs": _get_nested_data(season, "stat", "homeRuns"),
            "strike_outs": _get_nested_data(season, "stat", "strikeOuts"),
            "base_on_balls": _get_nested_data(season, "stat", "baseOnBalls"),
            "intentional_walks": _get_nested_data(season, "stat", "intentionalWalks"),
            "hit_batsmen": _get_nested_data(season, "stat", "hitByPitch"),
            "hits_allowed": _get_nested_data(season, "stat", "hits"),
            "batting_average_against": _convert_float(_get_nested_data(season, "stat", "avg")),
            "batters_faced": _get_nested_data(season, "stat", "battersFaced"),
            "on_base_percentage": _convert_float(_get_nested_data(season, "stat", "obp")),
            "slugging": _convert_float(_get_nested_data(season, "stat", "slg")),
            "on_base_plus_slugging": _convert_float(_get_nested_data(season, "stat", "ops")),
            "caught_stealing": _get_nested_data(season, "stat", "caughtStealing"),
            "stolen_bases": _get_nested_data(season, "stat", "stolenBases"),
            "ground_into_double_play": _get_nested_data(season, "stat", "groundIntoDoublePlay"),
            "number_of_pitches": _get_nested_data(season, "stat", "numberOfPitches"),
            "earned_run_average": _convert_float(_get_nested_data(season, "stat", "era")),
            "outs": _get_nested_data(season, "stat", "outs"),
            "wins": _get_nested_data(season, "stat", "wins"),
            "losses": _get_nested_data(season, "stat", "losses"),
            "saves": _get_nested_data(season, "stat", "saves"),
            "save_opportunities": _get_nested_data(season, "stat", "saveOpportunities"),
            "blown_saves": _get_nested_data(season, "stat", "blownSaves"),
            "holds": _get_nested_data(season, "stat", "holds"),
            "earned_runs": _get_nested_data(season, "stat", "earnedRuns"),
            "walks_plus_hits_per_inning_pitched": _convert_float(_get_nested_data(season, "stat", "whip")),
            "complete_games": _get_nested_data(season, "stat", "completeGames"),
            "shutouts": _get_nested_data(season, "stat", "shutouts"),
            "strike_percentage": _convert_float(_get_nested_data(season, "stat", "strikePercentage")),
            "pitches_per_inning": _convert_float(_get_nested_data(season, "stat", "pitchesPerInning")),
            "strike_outs_per_9": _convert_float(_get_nested_data(season, "stat", "strikeoutsPer9Inn")),
            "base_on_balls_per_9": _convert_float(_get_nested_data(season, "stat", "walksPer9Inn")),
            "hits_per_9": _convert_float(_get_nested_data(season, "stat", "hitsPer9Inn")),
            "home_runs_per_9": _convert_float(_get_nested_data(season, "stat", "homeRunsPer9")),
            "inherited_runners": _get_nested_data(season, "stat", "inheritedRunners"),
            "inherited_runners_scored": _get_nested_data(season, "stat", "inheritedRunnersScored"),
            "player_id": player_id,
            "team_id": season.get("team").get("id")
        }]

    return season_stats

def _get_nested_data(dictionary, outer_key, inner_key):
    try:
        return dictionary.get(outer_key).get(inner_key)
    except:
        return None

def _create_date(dictionary, key):
    try:
        return date.fromisoformat(dictionary.get(key))
    except TypeError:
        return None
    except ValueError:
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

def _convert_float(number):
    try:
        return float(number)
    except:
        return None