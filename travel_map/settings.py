from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ALLOWED_ORIGINS: list[str]
    URL_PREFIX: str
    SENTRY_SDK: str
    MONGO_URL: str
    NOMINATIM_USER_AGENT: str
    NOMINATIM_URL: str
    NOMINATIM_REVERSE_URL: str
    NOMINATIM_ACCESS_TOKEN: str

    REDIS_HOST: str
    REDIS_PORT: int = 0
    REDIS_URL: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # ty: ignore[missing-argument]
