import os
from collections.abc import AsyncGenerator
from urllib.parse import urlparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import get_settings

settings = get_settings()


def _postgres_connect_args(url: str) -> dict:
    if "sqlite" in url:
        return {}
    if not url.startswith("postgresql+asyncpg"):
        return {}
    timeout = float(os.getenv("DATABASE_CONNECT_TIMEOUT", "25"))
    args: dict = {"timeout": timeout}
    if os.getenv("DATABASE_SSL", "").lower() in ("0", "false", "no", "off"):
        return args
    host = urlparse(url.split("?", maxsplit=1)[0]).hostname or ""
    if host in ("localhost", "127.0.0.1", "::1", "host.docker.internal"):
        return args
    # Hosted Postgres (Railway, Neon, etc.) expects TLS.
    args["ssl"] = True
    return args


engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level.lower() == "debug",
    connect_args=_postgres_connect_args(settings.database_url),
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
