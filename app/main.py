"""FastAPI 应用入口模块。

该模块负责创建应用、注册路由、配置异常处理，并管理启动和关闭生命周期。
"""

import asyncio
import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import create_api_router
from app.core.config import get_settings
from app.core.errors import AppError, app_error_handler, unhandled_error_handler
from app.core.logging import setup_logging
from app.db.postgres import close_postgres, get_session_factory, init_postgres
from app.db.qdrant import close_qdrant, init_qdrant
from app.db.redis import close_redis, init_redis
from app.middleware.workspace_middleware import WorkspaceContextMiddleware
from app.services.queue import RedisQueue
from app.services.scheduler import TaskScheduler, run_scheduler_loop
from app.workers.handlers.agentic_rag_handler import AgenticRAGHandler
from app.workers.handlers.content_generation_handler import ContentGenerationHandler
from app.workers.task_executor import TaskExecutor, run_task_executor_loop

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    """应用生命周期管理器。"""

    settings = get_settings()
    setup_logging(settings.log_level)
    logger.info("Application startup started", extra={"app_env": settings.app_env})
    scheduler_task: asyncio.Task[None] | None = None
    task_executor_task: asyncio.Task[None] | None = None

    try:
        # 应用启动时统一初始化外部依赖，失败时阻止服务进入半可用状态。
        await init_postgres(settings)
        await init_redis(settings)
        await init_qdrant(settings)

        if settings.scheduler_enabled:
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

        if settings.task_executor_enabled:
            # TaskExecutor 只消费 Scheduler 已经推入 Redis 的任务，不改变 Scheduler 的扫描和入队职责。
            task_executor = TaskExecutor(
                queue=RedisQueue(settings.redis_queue_name),
                handlers=[
                    AgenticRAGHandler(settings=settings),
                    ContentGenerationHandler(),
                ],
                dequeue_timeout_seconds=settings.task_executor_dequeue_timeout_seconds,
            )
            task_executor_task = asyncio.create_task(
                run_task_executor_loop(
                    get_session_factory(),
                    task_executor,
                )
            )
            logger.info("Task executor background task started")

        logger.info("Application startup completed")
        yield
    except Exception as exc:
        logger.exception("Application startup failed")
        raise RuntimeError("Application startup failed") from exc
    finally:
        if task_executor_task is not None:
            task_executor_task.cancel()
            try:
                await task_executor_task
            except asyncio.CancelledError:
                logger.info("Task executor background task stopped")

        if scheduler_task is not None:
            scheduler_task.cancel()
            try:
                await scheduler_task
            except asyncio.CancelledError:
                logger.info("Scheduler background task stopped")

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
    """创建 FastAPI 应用实例。"""

    try:
        settings = get_settings()
        app = FastAPI(
            title=settings.app_name,
            version="0.1.0",
            lifespan=lifespan,
        )
        app.add_middleware(WorkspaceContextMiddleware)
        app.include_router(create_api_router())
        app.add_exception_handler(AppError, app_error_handler)
        app.add_exception_handler(Exception, unhandled_error_handler)
        logger.info("FastAPI application configured")
        return app
    except Exception as exc:
        logger.exception("Failed to create FastAPI application")
        raise RuntimeError("FastAPI application creation failed") from exc


app = create_app()
