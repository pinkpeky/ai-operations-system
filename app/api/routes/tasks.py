"""任务 API 路由模块。

该模块提供中央任务系统的基础 HTTP 接口，用于创建任务和按状态查询任务。
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.postgres import get_session
from app.models.enums import TaskStatus
from app.repositories.task_repository import TaskRepository
from app.schemas.task import TaskCreateRequest, TaskListResponse, TaskResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    request: TaskCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """创建中央任务。"""

    try:
        repository = TaskRepository(session)
        task = await repository.create_task(
            title=request.title,
            task_type=request.task_type,
            payload=request.payload,
            account_id=request.account_id,
            scheduled_at=request.scheduled_at,
            max_retries=request.max_retries,
        )
        logger.info("Task API created task", extra={"task_id": str(task.id)})
        return TaskResponse.model_validate(task)
    except Exception as exc:
        logger.exception("Task API failed to create task")
        raise AppError("Failed to create task", status_code=500) from exc


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: TaskStatus = Query(default=TaskStatus.PENDING, description="任务状态"),
    limit: int = Query(default=50, ge=1, le=200, description="返回数量"),
    session: AsyncSession = Depends(get_session),
) -> TaskListResponse:
    """按状态查询任务列表。"""

    try:
        repository = TaskRepository(session)
        tasks = await repository.list_tasks_by_status(status=status, limit=limit)
        logger.info("Task API listed tasks", extra={"status": status.value, "count": len(tasks)})
        return TaskListResponse(
            status=status,
            items=[TaskResponse.model_validate(task) for task in tasks],
        )
    except Exception as exc:
        logger.exception("Task API failed to list tasks", extra={"status": status.value})
        raise AppError("Failed to list tasks", status_code=500) from exc


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
) -> TaskResponse:
    """按 ID 查询任务。"""

    try:
        repository = TaskRepository(session)
        task = await repository.get_task(task_id)
        if task is None:
            raise AppError("Task not found", status_code=404)
        logger.info("Task API loaded task", extra={"task_id": str(task_id)})
        return TaskResponse.model_validate(task)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Task API failed to get task", extra={"task_id": str(task_id)})
        raise AppError("Failed to get task", status_code=500) from exc
