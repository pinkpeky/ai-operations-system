"""ComfyUI runtime adapter contract API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.comfyui_runtime import ComfyUIRuntimeService
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.comfyui_runtime import (
    ComfyUIRuntimeCapabilitiesResponse,
    ComfyUIRuntimeDiagnosticSnapshotCreateRequest,
    ComfyUIRuntimeDiagnosticSnapshotListResponse,
    ComfyUIRuntimeDiagnosticSnapshotResponse,
    ComfyUIRuntimeDiagnosticsResponse,
    ComfyUIRuntimeHealthResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/comfyui-runtime", tags=["comfyui-runtime"])


@router.get("/health", response_model=ComfyUIRuntimeHealthResponse)
async def get_comfyui_runtime_health(
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
) -> ComfyUIRuntimeHealthResponse:
    """Return disabled-by-default ComfyUI runtime contract health."""

    try:
        return ComfyUIRuntimeService(settings=settings).health_check(workspace_id=context.workspace_id)
    except Exception as exc:
        logger.exception("ComfyUI runtime health API failed")
        raise AppError("ComfyUI runtime health check failed", status_code=500) from exc


@router.get("/capabilities", response_model=ComfyUIRuntimeCapabilitiesResponse)
async def get_comfyui_runtime_capabilities(
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
) -> ComfyUIRuntimeCapabilitiesResponse:
    """Return the guarded ComfyUI runtime adapter contract capabilities."""

    try:
        return ComfyUIRuntimeService(settings=settings).capabilities(workspace_id=context.workspace_id)
    except Exception as exc:
        logger.exception("ComfyUI runtime capabilities API failed")
        raise AppError("ComfyUI runtime capabilities failed", status_code=500) from exc


@router.get("/diagnostics", response_model=ComfyUIRuntimeDiagnosticsResponse)
async def get_comfyui_runtime_diagnostics(
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
) -> ComfyUIRuntimeDiagnosticsResponse:
    """Return no-network ComfyUI runtime readiness diagnostics."""

    try:
        return ComfyUIRuntimeService(settings=settings).diagnostics(workspace_id=context.workspace_id)
    except Exception as exc:
        logger.exception("ComfyUI runtime diagnostics API failed")
        raise AppError("ComfyUI runtime diagnostics failed", status_code=500) from exc


@router.post("/diagnostic-snapshots", response_model=ComfyUIRuntimeDiagnosticSnapshotResponse)
async def create_comfyui_runtime_diagnostic_snapshot(
    request: ComfyUIRuntimeDiagnosticSnapshotCreateRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeDiagnosticSnapshotResponse:
    """Persist a no-network ComfyUI runtime diagnostic snapshot."""

    try:
        return await ComfyUIRuntimeService(settings=settings).create_diagnostic_snapshot(
            session,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            operator_note=request.operator_note,
            metadata=request.metadata,
        )
    except Exception as exc:
        logger.exception("ComfyUI runtime diagnostic snapshot create API failed")
        raise AppError("ComfyUI runtime diagnostic snapshot create failed", status_code=500) from exc


@router.get("/diagnostic-snapshots", response_model=ComfyUIRuntimeDiagnosticSnapshotListResponse)
async def list_comfyui_runtime_diagnostic_snapshots(
    limit: int = Query(default=20, ge=1, le=100),
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeDiagnosticSnapshotListResponse:
    """List persisted no-network ComfyUI runtime diagnostic snapshots."""

    try:
        return await ComfyUIRuntimeService(settings=settings).list_diagnostic_snapshots(
            session,
            workspace_id=context.workspace_id,
            limit=limit,
        )
    except Exception as exc:
        logger.exception("ComfyUI runtime diagnostic snapshot list API failed")
        raise AppError("ComfyUI runtime diagnostic snapshot list failed", status_code=500) from exc
