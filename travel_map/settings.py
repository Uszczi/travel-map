from pydantic import SecretStr
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

    DB_CONNECTION_STR: str
    DB_ASYNC_CONNECTION_STR: str

    PROMETHEUS_MULTIPROC_DIR: str

    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: SecretStr = SecretStr("")
    MAIL_FROM: str = "app@example.com"
    MAIL_FROM_NAME: str = ""
    MAIL_SERVER: str = ""
    MAIL_PORT: int = 0
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = True
    MAIL_VALIDATE_CERTS: bool = True

    JWT_ACCESS_LIFETIME_S: int = 15 * 60  # 15 minutes
    JWT_REFRESH_LIFETIME_S: int = 30 * 24 * 3600  # 30 days
    JWT_ACCESS_SECRET: SecretStr
    JWT_REFRESH_SECRET: SecretStr

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()  # ty: ignore[missing-argument]
