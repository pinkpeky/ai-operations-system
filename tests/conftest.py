"""测试公共夹具模块。

该模块提供内存数据库会话，让 ORM、Repository、Scheduler 可以脱离真实 PostgreSQL 单独测试。
"""

from collections.abc import AsyncIterator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.db.base import Base
from app.models import Account, PublishLog, Task


@pytest_asyncio.fixture
async def session() -> AsyncIterator[AsyncSession]:
    """创建 SQLite 内存数据库会话。"""

    # 显式引用模型，确保 metadata 注册完整。
    _ = (Account, PublishLog, Task)
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as test_session:
        yield test_session

    await engine.dispose()
