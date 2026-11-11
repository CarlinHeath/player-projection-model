import requests

# Bare API calls with no error handling intentionally

def fetch_player_info(player_id):
    """API call that returns basic player information
    
    A bad ID returns an error dict, not an exception
    """
    return requests.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}").json()

def fetch_hitter_stats(player_id):
    """API call that returns player year by year hitting stats

    Seasons a player was traded are split for each team + one combined row of all teams
    Bad ID returns empty stats, same as if a player had no stats
    """
    return requests.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=yearByYear&group=hitting").json()

def fetch_pitcher_stats(player_id):
    """API call that returns player year by year pitching stats

    Seasons a player was traded are split for each team + one combined row of all teams
    Bad ID returns empty stats, same as if a player had no stats
    """
    return requests.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=yearByYear&group=pitching").json()