import requests

from travel_map.utils import time_measure_decorator


class ElevationService:
    # TODO add injector
    def __init__(self, session: requests.Session | None = None) -> None:
        self.session = session or requests.session()

    # TODO make it async
    def close(self):
        self.session.close()

    @time_measure_decorator("Getting elevation took: ")
    def get(self, cords: list[tuple[float, float]]) -> dict[tuple[float, float], int]:
        with self.session as s:
            response = s.post(
                "http://host.docker.internal:8080/api/v1/lookup",
                json={"locations": [{"latitude": x, "longitude": y} for x, y in cords]},
            )
            result = response.json()

        res = {
            (r["latitude"], r["longitude"]): r["elevation"] for r in result["results"]
        }
        return res

    def covert_to_list(self, result: dict[tuple[float, float], int]) -> list[int]:
        return list(result.values())

    def calculate_total_gain_lose(self, elevation: list[int]) -> tuple[int, int]:
        total_gain = 0
        total_lose = 0
        for i, j in zip(elevation[:-1], elevation[1:]):
            diff = j - i

            if diff > 0:
                total_gain += diff
            elif diff < 0:
                total_lose += abs(diff)

        return total_gain, total_lose
