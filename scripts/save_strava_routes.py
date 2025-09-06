import requests
from loguru import logger
from pymongo import MongoClient

client = MongoClient("mongodb://mongodb:27017/")
db = client["strava_db"]
collection = db["routes"]


def fetch_activities(access_token):
    logger.info("Starting fetch_activities.")

    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {"per_page": 30, "page": 1}

    activities = []
    page = 1
    while True:
        params["page"] = page
        response = requests.get(url, headers=headers, params=params)

        if response.status_code != 200:
            logger.error(f"Błąd: {response.status_code}")
            logger.info(response.json())
            break

        logger.info(f"Got activities for {page=}")

        data = response.json()
        if not data:
            break

        activities.extend(data)
        page += 1
    return activities


def save_route(activity, access_token):
    if activity["type"] not in ("Walk", "Ride", "Run"):
        logger.info(f"Skipping activity: {activity["type"]}")
        return

    url = (
        f"https://www.strava.com/api/v3/activities/{activity['id']}/streams?keys=latlng"
    )
    headers = {"Authorization": f"Bearer { access_token }"}
    response = requests.get(url, headers=headers)
    route_json = response.json()
    points = None
    for r in route_json:
        try:
            if r["type"] == "latlng":
                points = r["data"]
                break
        except Exception as e:
            print("type failed")
            print(route_json)
            raise e

    if not points:
        logger.error("Missing points.")
        return

    # TODO fix
    # try:
    #     route_data = StravaRoute(
    #         id=activity["id"],
    #         xy=points,
    #         type=activity["type"],
    #         name=activity["name"],
    #     )
    #     collection.insert_one(route_data.model_dump())
    #     logger.info(f"Zapisano trasę {route_data.name} do MongoDB.")
    # except KeyError as e:
    #     logger.error(f"Błąd podczas przetwarzania aktywności: {e}")


def main():
    access_token = ""
    if not access_token:
        raise Exception("Access token is required.")

    saved = list(collection.find({}, {"id": 1, "_id": 0}))
    saved = [s["id"] for s in saved]

    activities = fetch_activities(access_token)
    for activity in activities:
        if activity["id"] in saved:
            logger.info("Activity already saved.")
            continue

        logger.info(f"Saving activities {activity['id']}")
        save_route(activity, access_token)


if __name__ == "__main__":
    logger.info("Starting main")
    main()
