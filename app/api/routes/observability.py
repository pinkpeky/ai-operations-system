"""可观测性 API 路由。"""

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.repositories.task_observability_repository import TaskObservabilityRepository
from app.schemas.observability import ObservabilitySummaryResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/summary", response_model=ObservabilitySummaryResponse)
async def get_observability_summary(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ObservabilitySummaryResponse:
    """返回当前工作区任务可靠性与可观测性概览。"""

    try:
        repository = TaskObservabilityRepository(session)
        summary = await repository.get_summary(workspace_id=context.workspace_id)
        return ObservabilitySummaryResponse(**summary)
    except Exception as exc:
        logger.exception("Observability summary API failed", extra={"workspace_id": context.workspace_id})
        raise AppError("Failed to load observability summary", status_code=500) from exc
