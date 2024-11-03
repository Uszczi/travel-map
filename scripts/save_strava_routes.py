import requests
from pymongo import MongoClient

from travel_map.models import StravaRoute

client = MongoClient("mongodb://localhost:27017/")
db = client["strava_db"]
collection = db["routes"]


def fetch_activities(access_token):
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": 30, "page": 1}

    activities = []
    page = 1
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            print(f"Błąd: {response.status_code}")
            print(response.json())
            break

        data = response.json()
        if not data:
            break

        activities.extend(data)
        page += 1
    return activities


def save_route(activity, access_token):
    if activity["type"] not in ("Walk", "Ride", "Run"):
        print(activity["type"], "skipping")
        return

    url = (
        f"https://www.strava.com/api/v3/activities/{activity['id']}/streams?keys=latlng"
    )
    headers = {"Authorization": f"Bearer { access_token }"}
    response = requests.get(url, headers=headers)
    route_json = response.json()
    for r in route_json:
        try:
            if r["type"] == "latlng":
                points = r["data"]
                break
        except Exception as e:
            print("type failed")
            print(route_json)
            raise e

    try:
        route_data = StravaRoute(
            id=activity["id"],
            xy=points,
            type=activity["type"],
            name=activity["name"],
        )
        collection.insert_one(route_data.dict())
        print(f"Zapisano trasę {route_data.name} do MongoDB.")
    except KeyError as e:
        print(f"Błąd podczas przetwarzania aktywności: {e}")


def main():
    access_token = ""

    saved = list(collection.find({}, {"id": 1, "_id": 0}))
    saved = [s["id"] for s in saved]

    activities = fetch_activities(access_token)
    for activity in activities:
        if activity["id"] in saved:
            print("Activity already saved.")
            continue
        save_route(activity, access_token)


if __name__ == "__main__":
    main()
