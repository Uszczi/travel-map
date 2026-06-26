from app import settings as app_settings
from app.settings import settings as direct_settings


def test_mock_settings():
    assert app_settings.settings.ENV == "TEST"
    assert direct_settings.ENV == "TEST"
