from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URL: str = ""
    NOMINATIM_USER_AGENT: str = ""
    NOMINATIM_URL: str = ""
    NOMINATIM_REVERSE_URL: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
