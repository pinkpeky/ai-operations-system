# 导入必要的模块
"""FastAPI 应用入口模块。

该模块负责创建应用实例、注册路由、配置异常处理，并管理启动/关闭生命周期。
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI

from app.api.router import create_api_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.core.logging import setup_logging
from app.db.postgres import close_postgres, get_session_factory, init_postgres
from app.db.qdrant import close_qdrant, init_qdrant
from app.db.redis import close_redis, init_redis
from app.services.queue import RedisQueue
from app.services.scheduler import TaskScheduler, run_scheduler_loop

logger = logging.getLogger(__name__)


# 应用生命周期管理器，用于启动和关闭时的操作
@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Application startup started", extra={"app_env": settings.app_env})
    scheduler_task: asyncio.Task[None] | None = None

    try:
        # 初始化数据库连接
        # 应用启动时统一初始化外部依赖，失败时阻止服务进入半可用状态。
        await init_postgres(settings)
        await init_redis(settings)
        await init_qdrant(settings)
        if settings.scheduler_enabled:
            # Scheduler 复用 Redis Queue 和数据库会话工厂，以后台任务形式持续运行。
            scheduler = TaskScheduler(
                queue=RedisQueue(settings.redis_queue_name),
                batch_size=settings.scheduler_batch_size,
                running_timeout_seconds=settings.scheduler_running_timeout_seconds,
            )
            scheduler_task = asyncio.create_task(
                run_scheduler_loop(
                    get_session_factory(),
                    scheduler,
                    settings.scheduler_interval_seconds,
                )
            )
            logger.info("Scheduler background task started")
        logger.info("Application startup completed")
        yield
    except Exception as exc:
        logger.exception("Application startup failed")
        raise RuntimeError("Application startup failed") from exc
    finally:
        # 关闭数据库连接
        if scheduler_task is not None:
            # 服务关闭时先取消调度循环，避免关闭数据库连接后后台任务继续访问。
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                logger.info("Scheduler background task stopped")
        shutdown_errors: list[str] = []
        # 按依赖使用顺序反向释放资源，降低关闭阶段的连接残留风险。
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


# 创建 FastAPI 应用实例
def create_app() -> FastAPI:
    try:
        settings = get_settings()
        # 创建 FastAPI 实例，生命周期函数负责连接外部基础设施。
        app = FastAPI(
            title=settings.app_name,
            version="0.1.0",
            lifespan=lifespan,
        )
        # 注册业务路由和统一异常处理器。
        app.include_router(create_api_router())
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(Exception, unhandled_error_handler)
        logger.info("FastAPI application configured")
        return app
    except Exception as exc:
        logger.exception("Failed to create FastAPI application")
        raise RuntimeError("FastAPI application creation failed") from exc


# 创建应用实例
app = create_app()
