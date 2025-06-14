from pymongo import MongoClient

from travel_map.settings import settings

client = MongoClient(settings.MONGO_URL)
strava_db = client["strava_db"]
