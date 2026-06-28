import datetime
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_get_version():
    with patch("app.api.main.get_version", return_value="abc1234") as mock:
        yield mock


@pytest.mark.asyncio
async def test_read_root(client):
    res = await client.get("/api/")

    assert res.status_code == 200, res.json()
    assert res.json() == {"Hello": "World"}


@pytest.mark.asyncio
async def test_version(mock_get_version, client):
    res = await client.get("/api/version")

    assert res.status_code == 200, res.json()
    assert res.json() == {"version": "abc1234"}


@pytest.mark.asyncio
@pytest.mark.freeze_time("2026-06-26T13:00:00")
async def test_info(mock_get_version, client):
    frozen_start = datetime.datetime(
        2026, 6, 26, 12, 0, 0, tzinfo=datetime.timezone.utc
    )
    with patch("app.api.main.start_time", frozen_start):
        res = await client.get("/api/info")

        assert res.status_code == 200, res.json()
        assert res.json() == {
            "start_time": "2026-06-26T12:00:00+00:00",
            "uptime_seconds": 3600.0,
            "version": "abc1234",
        }
