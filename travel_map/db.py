from pymongo import MongoClient

from travel_map.settings import settings

client = MongoClient(settings.MONGO_URL)
mongo_db = client["strava_db"]
