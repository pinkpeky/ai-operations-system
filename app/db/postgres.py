"""PostgreSQL 连接管理模块。

该模块负责初始化、健康检查和关闭 PostgreSQL 异步连接池。
"""

import logging
import asyncio
from collections.abc import AsyncIterator
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import Settings

logger = logging.getLogger(__name__)

engine: Optional[AsyncEngine] = None
async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


async def init_postgres(settings: Settings) -> None:
    global engine, async_session_factory

    try:
        # 使用 SQLAlchemy 异步引擎，后续业务模块可复用统一连接池。
        engine = create_async_engine(
            settings.database_url,
            pool_size=settings.postgres_pool_size,
            max_overflow=settings.postgres_max_overflow,
            pool_pre_ping=True,
        )
        async_session_factory = async_sessionmaker(engine, expire_on_commit=False)
        # 容器启动时数据库可能还在初始化，增加重试可以提升启动稳定性。
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
        # SELECT 1 是轻量级探活语句，不依赖任何业务表结构。
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
            # 应用关闭时释放连接池，避免连接泄漏。
            await engine.dispose()
            logger.info("PostgreSQL connection closed")
    except Exception as exc:
        logger.exception("Failed to close PostgreSQL connection")
        raise RuntimeError("PostgreSQL shutdown failed") from exc
    finally:
        engine = None
        async_session_factory = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """获取全局数据库会话工厂。"""

    try:
        if async_session_factory is None:
            raise RuntimeError("PostgreSQL session factory is not initialized")
        return async_session_factory
    except Exception as exc:
        logger.exception("Failed to get PostgreSQL session factory")
        raise RuntimeError("PostgreSQL session factory is unavailable") from exc


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI 依赖项：为每个请求提供独立数据库会话。"""

    session_factory = get_session_factory()
    async with session_factory() as session:
        try:
            yield session
        except Exception:
            # 保留上层异常类型，只在这里补充数据库会话上下文日志。
            logger.exception("PostgreSQL session scope failed")
            raise
