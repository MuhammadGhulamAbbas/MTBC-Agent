from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


def normalize_database_url(url: str) -> str:
    """Railway/Render use postgres:// or postgresql://; SQLAlchemy async needs postgresql+asyncpg://."""
    u = (url or "").strip()
    if u.startswith("postgres://"):
        return "postgresql+asyncpg://" + u[len("postgres://") :]
    if u.startswith("postgresql://") and not u.startswith("postgresql+asyncpg://"):
        return "postgresql+asyncpg://" + u[len("postgresql://") :]
    return u


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database_url: str = "sqlite+aiosqlite:///./patients.db"
    public_url: str = "http://localhost:8000"
    log_level: str = "info"

    @field_validator("database_url", mode="before")
    @classmethod
    def coerce_async_pg_url(cls, v: str) -> str:
        return normalize_database_url(v)


@lru_cache
def get_settings() -> Settings:
    return Settings()
