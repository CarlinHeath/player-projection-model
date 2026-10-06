import requests
import json
import os

if os.path.exists("data/teams.json"):
    os.remove("data/teams.json")

response = requests.get("https://statsapi.mlb.com/api/v1/teams?sportId=1")
data = response.json()

with open("data/teams.json", "w", encoding="utf-8") as file:
    json.dump(data, file, indent=2)