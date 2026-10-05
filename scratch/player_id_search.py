import requests
url = "https://statsapi.mlb.com/api/v1/people/search?names=Franklin Arias"
print(requests.get(url).json())