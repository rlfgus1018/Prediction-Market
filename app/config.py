from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./local.db"
    app_env: str = "local"
    naver_client_id: str | None = None
    naver_client_secret: str | None = None
    public_data_service_key: str | None = None
    market_cutoff_time: str = "15:30:00"
    timezone: str = "Asia/Seoul"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
