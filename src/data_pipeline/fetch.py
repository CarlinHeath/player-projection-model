import requests

def fetch_player_info(player_id):
    return requests.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}").json()

def fetch_hitter_stats(player_id):
    return requests.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=yearByYear&group=hitting").json()

def fetch_pitcher_stats(player_id):
    return requests.get(f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=yearByYear&group=pitching").json()