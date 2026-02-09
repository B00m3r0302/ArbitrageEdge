import httpx
import json

from src.app.config import settings

sports = settings.sports
api_key = settings.odds_api_key
url = "https://api.the-odds-api.com/v4/"


bookmakers = [

]
def get_in_season_sports():
    response = httpx.get(url + "sports/?apiKey=" + api_key)
    for sport in response.json():
        if sport["key"] in sports:
             print(sport["key"])

def get_sport_events():
