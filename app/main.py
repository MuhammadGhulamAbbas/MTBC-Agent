import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.routes import patients, webhook
from app.config import get_settings
from app.database import engine
from app.models import Base

settings = get_settings()

logging.basicConfig(
    level=getattr(logging, settings.log_level.upper(), logging.INFO),
    format="%(levelname)s %(name)s %(message)s",
)


async def _create_db_schema() -> None:
    """Runs after the server is accepting traffic so Railway healthchecks are not blocked."""
    log = logging.getLogger(__name__)
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        log.info("Database schema ready")
    except Exception:
        log.exception(
            "Database schema init failed — check DATABASE_URL, TLS, and that Postgres is reachable "
            "from this service. /health will still work; data routes will error until DB is fixed."
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    log = logging.getLogger(__name__)
    log.info("API process starting; binding HTTP before database schema init")
    init_task = asyncio.create_task(_create_db_schema())
    try:
        yield
    finally:
        init_task.cancel()
        try:
            await init_task
        except (asyncio.CancelledError, Exception):
            pass
        await engine.dispose()


app = FastAPI(
    title="Voice AI Patient Registration API",
    description="REST API for patient demographics (voice intake demo).",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(patients.router)
app.include_router(webhook.router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException,
) -> JSONResponse:
    detail = exc.detail
    message = detail if isinstance(detail, str) else str(detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "error": {"message": message, "details": detail}},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "data": None,
            "error": {"message": "Validation error", "details": exc.errors()},
        },
    )


@app.get("/health", tags=["health"])
async def health() -> dict:
    return {"status": "ok"}


@app.get("/", tags=["health"])
async def root() -> dict:
    return {"service": "voice-patient-api", "docs": "/docs"}


def main() -> None:
    import uvicorn

    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
