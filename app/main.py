import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.router import create_api_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.core.logging import setup_logging
from app.db.postgres import close_postgres, init_postgres
from app.db.qdrant import close_qdrant, init_qdrant
from app.db.redis import close_redis, init_redis

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Application startup started", extra={"app_env": settings.app_env})

    try:
        await init_postgres(settings)
        await init_redis(settings)
        await init_qdrant(settings)
        logger.info("Application startup completed")
        yield
    except Exception as exc:
        logger.exception("Application startup failed")
        raise RuntimeError("Application startup failed") from exc
    finally:
        shutdown_errors: list[str] = []
        for name, closer in (
            ("qdrant", close_qdrant),
            ("redis", close_redis),
            ("postgres", close_postgres),
        ):
            try:
                await closer()
            except Exception as exc:
                logger.exception("Application shutdown step failed", extra={"component": name})
                shutdown_errors.append(f"{name}: {exc}")
        if shutdown_errors:
            logger.error("Application shutdown completed with errors", extra={"errors": shutdown_errors})
        else:
            logger.info("Application shutdown completed")


def create_app() -> FastAPI:
    try:
        settings = get_settings()
        app = FastAPI(
            title=settings.app_name,
            version="0.1.0",
            lifespan=lifespan,
        )
        app.include_router(create_api_router())
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(Exception, unhandled_error_handler)
        logger.info("FastAPI application configured")
        return app
    except Exception as exc:
        logger.exception("Failed to create FastAPI application")
        raise RuntimeError("FastAPI application creation failed") from exc


app = create_app()
