"""OpenClaw worker adapter API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.openclaw.schemas import OpenClawActionRequest, OpenClawActionResponse, OpenClawCapabilitiesResponse, OpenClawHealthResponse
from app.openclaw.service import OpenClawService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/openclaw", tags=["openclaw"])


@router.get("/health", response_model=OpenClawHealthResponse)
async def get_openclaw_health(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OpenClawHealthResponse:
    """检查当前 workspace 的 OpenClaw worker mock runtime。"""

    try:
        response = await OpenClawService(session).health_check(
            workspace_id=context.workspace_id,
            actor_type="api",
            actor_id=context.user_id,
        )
        await session.commit()
        return response
    except Exception as exc:
        logger.exception("OpenClaw health API failed")
        raise AppError("OpenClaw health check failed", status_code=500) from exc


@router.get("/capabilities", response_model=OpenClawCapabilitiesResponse)
async def get_openclaw_capabilities(
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OpenClawCapabilitiesResponse:
    """查询当前 workspace 的 OpenClaw mock capabilities。"""

    try:
        response = await OpenClawService(session).capabilities(
            workspace_id=context.workspace_id,
            actor_type="api",
            actor_id=context.user_id,
        )
        await session.commit()
        return response
    except Exception as exc:
        logger.exception("OpenClaw capabilities API failed")
        raise AppError("OpenClaw capabilities failed", status_code=500) from exc


@router.post("/actions", response_model=OpenClawActionResponse)
async def execute_openclaw_action(
    request: OpenClawActionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OpenClawActionResponse:
    """执行 OpenClaw mock action。"""

    try:
        response = await OpenClawService(session).execute_action(
            workspace_id=context.workspace_id,
            request=request,
            actor_type="api",
            actor_id=context.user_id,
        )
        await session.commit()
        return response
    except Exception as exc:
        logger.exception("OpenClaw action API failed", extra={"action_type": request.action_type})
        raise AppError("OpenClaw action failed", status_code=500) from exc
