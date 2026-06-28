from unittest.mock import AsyncMock, patch

import pytest

from app.serializers.geocode import BoundingBox, GeocodeItem


@pytest.fixture
def mock_nominatim():
    with patch("app.api.geocode.NominatimService") as mock_cls:
        mock_instance = mock_cls.return_value

        berlin_item = GeocodeItem(
            id=65478,
            label="Berlin, Germany",
            lat=52.520008,
            lng=13.404954,
            type="city",
            boundingbox=BoundingBox(
                south=52.3389, north=52.6755, west=13.0883, east=13.761
            ),
        )

        mock_instance.search = AsyncMock(return_value=[berlin_item])
        mock_instance.reverse = AsyncMock(return_value=berlin_item)
        yield


@pytest.mark.asyncio
async def test_geocode(client, mock_nominatim):
    res = await client.get("/api/geocode?q=berlin")
    assert res.status_code == 200, res.json()
    assert res.json() == {
        "items": [
            {
                "id": 65478,
                "label": "Berlin, Germany",
                "lat": 52.520008,
                "lng": 13.404954,
                "type": "city",
                "boundingbox": {
                    "south": 52.3389,
                    "north": 52.6755,
                    "west": 13.0883,
                    "east": 13.761,
                },
            }
        ]
    }

    res = await client.get("/api/geocode?q=berlin&tag=place")
    assert res.status_code == 200, res.json()
    assert res.json() == {
        "items": [
            {
                "id": 65478,
                "label": "Berlin, Germany",
                "lat": 52.520008,
                "lng": 13.404954,
                "type": "city",
                "boundingbox": {
                    "south": 52.3389,
                    "north": 52.6755,
                    "west": 13.0883,
                    "east": 13.761,
                },
            }
        ]
    }

    res = await client.get("/api/geocode?lat=52.520008&lng=13.404954")
    assert res.status_code == 200, res.json()
    assert res.json() == {
        "id": 65478,
        "label": "Berlin, Germany",
        "lat": 52.520008,
        "lng": 13.404954,
        "type": "city",
        "boundingbox": {
            "south": 52.3389,
            "north": 52.6755,
            "west": 13.0883,
            "east": 13.761,
        },
    }
