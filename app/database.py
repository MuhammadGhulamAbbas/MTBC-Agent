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
    parsed = urlparse(url.split("?", maxsplit=1)[0])
    host = (parsed.hostname or "").lower()
    if host in ("localhost", "127.0.0.1", "::1", "host.docker.internal"):
        return args
    # Railway service-to-Postgres private DNS is not set up for client TLS the same
    # way as public URLs; asyncpg with ssl=True often fails with EOF / handshake errors.
    if host.endswith(".railway.internal"):
        return args
    # Hosted Postgres (public hostname: Neon, Supabase, Railway public URL, etc.).
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
