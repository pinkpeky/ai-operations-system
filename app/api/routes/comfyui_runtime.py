"""ComfyUI runtime adapter contract API routes."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from app.comfyui_runtime import ComfyUIRuntimeService
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.schemas.comfyui_runtime import (
    ComfyUIRuntimeCapabilitiesResponse,
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
