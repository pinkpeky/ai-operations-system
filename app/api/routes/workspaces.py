"""工作区管理 API 路由模块。"""

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.db.postgres import get_session
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import WorkspaceCreateRequest, WorkspaceListResponse, WorkspaceResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceResponse, status_code=201)
async def create_workspace(
    request: WorkspaceCreateRequest,
    session: AsyncSession = Depends(get_session),
) -> WorkspaceResponse:
    """创建工作区。"""

    try:
        repository = WorkspaceRepository(session)
        workspace = await repository.create_workspace(name=request.name, slug=request.slug)
        return WorkspaceResponse.from_model(workspace)
    except Exception as exc:
        logger.exception("Workspace create API failed")
        raise AppError(f"Workspace create failed: {exc}", status_code=500) from exc


@router.get("", response_model=WorkspaceListResponse)
async def list_workspaces(
    limit: int = Query(default=100, ge=1, le=500, description="返回数量"),
    session: AsyncSession = Depends(get_session),
) -> WorkspaceListResponse:
    """查询工作区列表。"""

    try:
        repository = WorkspaceRepository(session)
        workspaces = await repository.list_workspaces(limit=limit)
        return WorkspaceListResponse(items=[WorkspaceResponse.from_model(workspace) for workspace in workspaces])
    except Exception as exc:
        logger.exception("Workspace list API failed")
        raise AppError("Workspace list failed", status_code=500) from exc
