from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "postgresql+asyncpg://lyrics:lyrics@localhost:5432/lyricsmanager"
    redis_url: str = "redis://localhost:6379"
    secret_key: str = "dev-secret-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    refresh_token_expire_days: int = 30

    first_admin_email: str = "admin@example.com"
    first_admin_password: str = "changeme123"

    storage_path: str = "/app/storage"
    max_storage_mb: int = 2048

    app_name: str = "LyricsManager"
    app_version: str = "1.0.0"


@lru_cache
def get_settings() -> Settings:
    return Settings()
