"""Alembic 迁移环境配置。

该模块读取应用配置并加载 ORM metadata，让 Alembic 能根据模型生成和执行迁移。
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.db.base import Base
from app import models as _models

config = context.config

if config.config_file_name is not None:
    # Alembic 自带日志配置，迁移命令执行时保持输出可读。
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _get_sync_database_url() -> str:
    """获取 Alembic 使用的同步 PostgreSQL 连接地址。"""

    settings = get_settings()
    return settings.database_url.replace("postgresql+asyncpg://", "postgresql+psycopg://")


def run_migrations_offline() -> None:
    """离线模式迁移，用于生成 SQL 脚本。"""

    url = _get_sync_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """在线模式迁移，直接连接数据库执行 schema 变更。"""

    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _get_sync_database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
