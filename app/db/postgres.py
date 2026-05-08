import logging
import asyncio
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.config import Settings

logger = logging.getLogger(__name__)

engine: Optional[AsyncEngine] = None
async_session_factory: Optional[async_sessionmaker] = None


async def init_postgres(settings: Settings) -> None:
    global engine, async_session_factory

    try:
        engine = create_async_engine(
            settings.database_url,
            pool_size=settings.postgres_pool_size,
            max_overflow=settings.postgres_max_overflow,
            pool_pre_ping=True,
        )
        async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
        for attempt in range(1, 11):
            try:
                await check_postgres()
                break
            except Exception:
                if attempt == 10:
                    raise
                logger.warning("PostgreSQL not ready, retrying", extra={"attempt": attempt})
                await asyncio.sleep(2)
        logger.info("PostgreSQL connection initialized")
    except Exception as exc:
        logger.exception("Failed to initialize PostgreSQL connection")
        await close_postgres()
        raise RuntimeError("PostgreSQL initialization failed") from exc


async def check_postgres() -> bool:
    try:
        if engine is None:
            raise RuntimeError("PostgreSQL engine is not initialized")
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
        logger.debug("PostgreSQL health check passed")
        return True
    except Exception as exc:
        logger.exception("PostgreSQL health check failed")
        raise RuntimeError("PostgreSQL health check failed") from exc


async def close_postgres() -> None:
    global engine, async_session_factory

    try:
        if engine is not None:
            await engine.dispose()
            logger.info("PostgreSQL connection closed")
    except Exception as exc:
        logger.exception("Failed to close PostgreSQL connection")
        raise RuntimeError("PostgreSQL shutdown failed") from exc
    finally:
        engine = None
        async_session_factory = None
