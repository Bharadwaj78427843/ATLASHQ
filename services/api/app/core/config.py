"""
app/core/config.py

Application settings loaded from environment variables.
All secrets have safe defaults for local development only.
In production, override via environment or a .env file.
"""
from functools import lru_cache
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Database
    DATABASE_URL: str = (
        "postgresql+asyncpg://atlas:atlas_secret@localhost:5432/atlas_db"
    )

    # JWT
    SECRET_KEY: str = "CHANGE_ME_IN_PRODUCTION_USE_AT_LEAST_32_CHARS"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # App
    APP_NAME: str = "Atlas API"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    STORAGE_BASE_PATH: str = "storage"

    @field_validator("DEBUG", mode="before")
    @classmethod
    def _parse_debug(cls, value):
        if isinstance(value, str):
            lowered = value.strip().lower()
            if lowered in {"1", "true", "yes", "on", "debug", "development"}:
                return True
            if lowered in {"0", "false", "no", "off", "release", "production", "prod"}:
                return False
        return value


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance (evaluated once per process)."""
    return Settings()