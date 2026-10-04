import requests
import json

player_id = 665742
url = f"https://statsapi.mlb.com/api/v1/people/{player_id}/stats?stats=season&group=hitting&season=2025"

response = requests.get(url)
data = response.json()

print(json.dumps(data, indent=2))