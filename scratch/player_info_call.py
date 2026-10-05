import requests
import json

# MLB Stats API - get a player's info by their player ID
# (example: Juan Soto's player ID is 665742, just as a starting point)
player_id = 808265
url = f"https://statsapi.mlb.com/api/v1/people/{player_id}"

response = requests.get(url)
data = response.json()

print(json.dumps(data, indent=2))