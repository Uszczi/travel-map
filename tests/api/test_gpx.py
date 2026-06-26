import pytest


@pytest.mark.asyncio
async def test_route_to_gpx(client):
    res = await client.post(
        "/route-to-gpx",
        json={
            "points": [[48.8566, 2.3522], [52.5200, 13.4050]],
            "title": "Test Track",
        },
    )
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/gpx+xml"
    assert res.headers["content-disposition"] == "attachment; filename=Test Track.gpx"

    xml = res.text
    assert '<?xml version="1.0" encoding="UTF-8"' in xml
    assert "<gpx" in xml
    assert "<trk>" in xml
    assert "<name>Test Track</name>" in xml
    assert '<trkpt lat="48.8566" lon="2.3522">' in xml
    assert '<trkpt lat="52.52" lon="13.405">' in xml
