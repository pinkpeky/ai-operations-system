"""任务 API 路由模块。

该模块提供中央任务系统的基础 HTTP 接口，用于创建任务和按状态查询任务。
"""

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.models.enums import TaskStatus
from app.repositories.task_observability_repository import TaskObservabilityRepository
from app.repositories.task_repository import TaskRepository
from app.schemas.task import (
    AgenticRAGTaskCreateRequest,
    ContentGenerationTaskCreateRequest,
    TaskControlResponse,
    TaskCreateRequest,
    TaskEventListResponse,
    TaskEventResponse,
    TaskListResponse,
    TaskLogListResponse,
    TaskLogResponse,
    TaskResponse,
)
from app.workers.handlers.agentic_rag_handler import AGENTIC_RAG_TASK_TYPE
from app.workers.handlers.content_generation_handler import CONTENT_GENERATION_TASK_TYPE

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    request: TaskCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskResponse:
    """创建中央任务。"""

    try:
        repository = TaskRepository(session)
        task = await repository.create_task(
            title=request.title,
            task_type=request.task_type,
            payload=request.payload,
            account_id=request.account_id,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            scheduled_at=request.scheduled_at,
            max_retries=request.max_retries,
        )
        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=context.workspace_id,
            event_type="created",
            message="Task created",
            payload={"task_type": task.task_type},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=context.workspace_id,
            level="info",
            message="Task created",
            metadata={"task_type": task.task_type},
        )
        await session.commit()
        logger.info("Task API created task", extra={"task_id": str(task.id)})
        return TaskResponse.model_validate(task)
    except Exception as exc:
        logger.exception("Task API failed to create task")
        raise AppError("Failed to create task", status_code=500) from exc


@router.post("/agentic-rag", response_model=TaskResponse, status_code=201)
async def create_agentic_rag_task(
    request: AgenticRAGTaskCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskResponse:
    """创建 Agentic RAG 查询任务。"""

    try:
        repository = TaskRepository(session)
        payload = {
            "query": request.query,
            "collection_name": request.collection_name,
            "top_k": request.top_k,
            "debug": request.debug,
        }
        task = await repository.create_task(
            title=request.title or f"Agentic RAG Query: {request.query[:80]}",
            task_type=AGENTIC_RAG_TASK_TYPE,
            payload=payload,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            scheduled_at=request.scheduled_at,
            max_retries=request.max_retries,
        )
        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=context.workspace_id,
            event_type="created",
            message="Agentic RAG task created",
            payload={"task_type": task.task_type, "collection_name": request.collection_name},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=context.workspace_id,
            level="info",
            message="Agentic RAG task created",
            metadata={"task_type": task.task_type, "collection_name": request.collection_name},
        )
        await session.commit()
        logger.info("Task API created Agentic RAG task", extra={"task_id": str(task.id)})
        return TaskResponse.model_validate(task)
    except Exception as exc:
        logger.exception("Task API failed to create Agentic RAG task")
        raise AppError("Failed to create Agentic RAG task", status_code=500) from exc


@router.post("/content-generation", response_model=TaskResponse, status_code=201)
async def create_content_generation_task(
    request: ContentGenerationTaskCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskResponse:
    """创建内容生成任务。"""

    try:
        repository = TaskRepository(session)
        payload = {
            "topic": request.topic,
            "platform": request.platform,
            "style": request.style,
        }
        task = await repository.create_task(
            title=request.title or f"Content Generation: {request.topic[:80]}",
            task_type=CONTENT_GENERATION_TASK_TYPE,
            payload=payload,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            scheduled_at=request.scheduled_at,
            max_retries=request.max_retries,
        )
        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=context.workspace_id,
            event_type="created",
            message="Content generation task created",
            payload={"task_type": task.task_type, "platform": request.platform},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=context.workspace_id,
            level="info",
            message="Content generation task created",
            metadata={"task_type": task.task_type, "platform": request.platform},
        )
        await session.commit()
        logger.info("Task API created content generation task", extra={"task_id": str(task.id)})
        return TaskResponse.model_validate(task)
    except Exception as exc:
        logger.exception("Task API failed to create content generation task")
        raise AppError("Failed to create content generation task", status_code=500) from exc


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    status: TaskStatus = Query(default=TaskStatus.PENDING, description="任务状态"),
    limit: int = Query(default=50, ge=1, le=200, description="返回数量"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskListResponse:
    """按状态查询任务列表。"""

    try:
        repository = TaskRepository(session)
        tasks = await repository.list_tasks_by_status(status=status, limit=limit, workspace_id=context.workspace_id)
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
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskResponse:
    """按 ID 查询任务。"""

    try:
        repository = TaskRepository(session)
        task = await repository.get_task(task_id, workspace_id=context.workspace_id)
        if task is None:
            raise AppError("Task not found", status_code=404)
        logger.info("Task API loaded task", extra={"task_id": str(task_id)})
        return TaskResponse.model_validate(task)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Task API failed to get task", extra={"task_id": str(task_id)})
        raise AppError("Failed to get task", status_code=500) from exc


@router.post("/{task_id}/cancel", response_model=TaskControlResponse)
async def cancel_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskControlResponse:
    """取消当前工作区内的任务。"""

    try:
        repository = TaskRepository(session)
        task = await repository.cancel_task(task_id=task_id, workspace_id=context.workspace_id)
        if task is None:
            raise AppError("Task not found", status_code=404)
        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=context.workspace_id,
            event_type="cancelled",
            message="Task cancelled by user",
            payload={"status": task.status},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=context.workspace_id,
            level="warning",
            message="Task cancelled by user",
            metadata={"duration_ms": task.duration_ms},
        )
        await session.commit()
        return TaskControlResponse(task=TaskResponse.model_validate(task), message="Task cancelled")
    except AppError:
        raise
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Task API failed to cancel task", extra={"task_id": str(task_id)})
        raise AppError("Failed to cancel task", status_code=500) from exc


@router.post("/{task_id}/retry", response_model=TaskControlResponse)
async def retry_task(
    task_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskControlResponse:
    """手动重试 failed/cancelled/timeout 任务。"""

    try:
        repository = TaskRepository(session)
        task = await repository.retry_task(task_id=task_id, workspace_id=context.workspace_id)
        if task is None:
            raise AppError("Task not found", status_code=404)
        observability = TaskObservabilityRepository(session)
        await observability.create_event(
            task_id=task.id,
            workspace_id=context.workspace_id,
            event_type="retry_requested",
            message="Task retry requested by user",
            payload={"status": task.status},
        )
        await observability.create_log(
            task_id=task.id,
            workspace_id=context.workspace_id,
            level="info",
            message="Task retry requested by user",
            metadata={"retry_count": task.retry_count},
        )
        await session.commit()
        return TaskControlResponse(task=TaskResponse.model_validate(task), message="Task retry scheduled")
    except AppError:
        raise
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Task API failed to retry task", extra={"task_id": str(task_id)})
        raise AppError("Failed to retry task", status_code=500) from exc


@router.get("/{task_id}/events", response_model=TaskEventListResponse)
async def list_task_events(
    task_id: UUID,
    limit: int = Query(default=100, ge=1, le=500, description="返回事件数量"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskEventListResponse:
    """查询任务事件。"""

    try:
        repository = TaskRepository(session)
        task = await repository.get_task(task_id=task_id, workspace_id=context.workspace_id)
        if task is None:
            raise AppError("Task not found", status_code=404)
        observability = TaskObservabilityRepository(session)
        events = await observability.list_events(task_id=task_id, workspace_id=context.workspace_id, limit=limit)
        return TaskEventListResponse(
            task_id=task_id,
            items=[TaskEventResponse.model_validate(event) for event in events],
        )
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Task API failed to list events", extra={"task_id": str(task_id)})
        raise AppError("Failed to list task events", status_code=500) from exc


@router.get("/{task_id}/logs", response_model=TaskLogListResponse)
async def list_task_logs(
    task_id: UUID,
    limit: int = Query(default=200, ge=1, le=1000, description="返回日志数量"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> TaskLogListResponse:
    """查询任务日志。"""

    try:
        repository = TaskRepository(session)
        task = await repository.get_task(task_id=task_id, workspace_id=context.workspace_id)
        if task is None:
            raise AppError("Task not found", status_code=404)
        observability = TaskObservabilityRepository(session)
        logs = await observability.list_logs(task_id=task_id, workspace_id=context.workspace_id, limit=limit)
        return TaskLogListResponse(
            task_id=task_id,
            items=[
                TaskLogResponse(
                    id=log.id,
                    task_id=log.task_id,
                    workspace_id=log.workspace_id,
                    level=log.level,
                    message=log.message,
                    metadata=log.log_metadata,
                    created_at=log.created_at,
                )
                for log in logs
            ],
        )
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Task API failed to list logs", extra={"task_id": str(task_id)})
        raise AppError("Failed to list task logs", status_code=500) from exc
