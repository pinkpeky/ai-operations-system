"""Commercial operations API routes."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.commercial_operations.service import CommercialOperationService
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.commercial_operation import (
    CommercialOperationCreateRequest,
    CommercialOperationLinkCreateRequest,
    CommercialOperationLinkListResponse,
    CommercialOperationLinkResponse,
    CommercialOperationListResponse,
    CommercialOperationPlanPreviewResponse,
    CommercialOperationResponse,
    CommercialOperationUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/commercial-operations", tags=["commercial-operations"])


@router.post("", response_model=CommercialOperationResponse, status_code=201)
async def create_commercial_operation(
    request: CommercialOperationCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResponse:
    """Create a commercial operation project from a business objective."""

    try:
        operation = await CommercialOperationService(session).create_operation(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationResponse.from_model(operation)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Commercial operation create API failed")
        raise AppError("Commercial operation create failed", status_code=500) from exc


@router.get("", response_model=CommercialOperationListResponse)
async def list_commercial_operations(
    status: str | None = Query(default=None, description="draft / planning / ready / active / paused / completed / archived"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationListResponse:
    """List commercial operations in the current workspace."""

    try:
        operations = await CommercialOperationService(session).list_operations(
            workspace_id=context.workspace_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationListResponse(
            items=[CommercialOperationResponse.from_model(operation) for operation in operations]
        )
    except Exception as exc:
        logger.exception("Commercial operation list API failed")
        raise AppError("Commercial operation list failed", status_code=500) from exc


@router.get("/{operation_id}", response_model=CommercialOperationResponse)
async def get_commercial_operation(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResponse:
    """Read one commercial operation in the current workspace."""

    try:
        operation = await CommercialOperationService(session).require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        return CommercialOperationResponse.from_model(operation)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation get API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation get failed", status_code=500) from exc


@router.patch("/{operation_id}", response_model=CommercialOperationResponse)
async def update_commercial_operation(
    operation_id: UUID,
    request: CommercialOperationUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResponse:
    """Patch one commercial operation and rebuild its non-executing plan outline."""

    try:
        operation = await CommercialOperationService(session).update_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationResponse.from_model(operation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation update API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation update failed", status_code=500) from exc


@router.post("/{operation_id}/plan-draft", response_model=CommercialOperationPlanPreviewResponse)
async def regenerate_commercial_operation_plan(
    operation_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationPlanPreviewResponse:
    """Regenerate the conservative plan outline without executing external actions."""

    try:
        operation = await CommercialOperationService(session).regenerate_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        return CommercialOperationPlanPreviewResponse(
            operation_id=operation.id,
            plan_outline=operation.plan_outline,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation plan API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation plan failed", status_code=500) from exc


@router.post("/{operation_id}/links", response_model=CommercialOperationLinkResponse, status_code=201)
async def create_commercial_operation_link(
    operation_id: UUID,
    request: CommercialOperationLinkCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationLinkResponse:
    """Attach evidence, handoff, or runtime context to a commercial operation."""

    try:
        link = await CommercialOperationService(session).create_link(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            **request.model_dump(),
        )
        return CommercialOperationLinkResponse.from_model(link)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation link create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation link create failed", status_code=500) from exc


@router.get("/{operation_id}/links", response_model=CommercialOperationLinkListResponse)
async def list_commercial_operation_links(
    operation_id: UUID,
    link_type: str | None = Query(default=None, description="conversation / artifact / task_run / workflow_run / rag_document / knowledge_source / approval / external"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationLinkListResponse:
    """List evidence and handoff links for a commercial operation."""

    try:
        links = await CommercialOperationService(session).list_links(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            link_type=link_type,
            limit=limit,
        )
        return CommercialOperationLinkListResponse(
            operation_id=operation_id,
            items=[CommercialOperationLinkResponse.from_model(link) for link in links],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation link list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation link list failed", status_code=500) from exc


@router.delete("/{operation_id}/links/{link_id}", response_model=CommercialOperationLinkResponse)
async def delete_commercial_operation_link(
    operation_id: UUID,
    link_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationLinkResponse:
    """Remove one commercial operation evidence or handoff link."""

    try:
        link = await CommercialOperationService(session).delete_link(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            link_id=link_id,
        )
        return CommercialOperationLinkResponse.from_model(link)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation link delete API failed",
            extra={"operation_id": str(operation_id), "link_id": str(link_id)},
        )
        raise AppError("Commercial operation link delete failed", status_code=500) from exc
