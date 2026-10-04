import requests
import json

player_id = 543037  # example: a known pitcher's ID — swap in whoever you want
url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=yearByYear&group=pitching"

response = requests.get(url)
data = response.json()

print(json.dumps(data, indent=2))