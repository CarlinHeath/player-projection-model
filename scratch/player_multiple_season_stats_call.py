import requests
import json

player_id = 808265
url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=yearByYear&group=hitting"

response = requests.get(url)
data = response.json()

print(json.dumps(data, indent=2))