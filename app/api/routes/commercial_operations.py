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
    CommercialOperationApprovalCreateRequest,
    CommercialOperationApprovalDecisionRequest,
    CommercialOperationApprovalListResponse,
    CommercialOperationApprovalResponse,
    CommercialOperationAssetRequestCreateRequest,
    CommercialOperationAssetRequestDecisionRequest,
    CommercialOperationAssetRequestListResponse,
    CommercialOperationAssetRequestResponse,
    CommercialOperationAssetRequestUpdateRequest,
    CommercialOperationContentDraftCreateRequest,
    CommercialOperationContentDraftDecisionRequest,
    CommercialOperationContentDraftListResponse,
    CommercialOperationContentDraftResponse,
    CommercialOperationContentDraftUpdateRequest,
    CommercialOperationCreateRequest,
    CommercialOperationDeliverableCreateRequest,
    CommercialOperationDeliverableDecisionRequest,
    CommercialOperationDeliverableListResponse,
    CommercialOperationDeliverableResponse,
    CommercialOperationDeliverableUpdateRequest,
    CommercialOperationDryRunCreateRequest,
    CommercialOperationDryRunDecisionRequest,
    CommercialOperationDryRunListResponse,
    CommercialOperationDryRunResponse,
    CommercialOperationExecutionRequestCreateRequest,
    CommercialOperationExecutionRequestDecisionRequest,
    CommercialOperationExecutionRequestListResponse,
    CommercialOperationExecutionRequestResponse,
    CommercialOperationExecutionRequestUpdateRequest,
    CommercialOperationExecutionRunCreateRequest,
    CommercialOperationExecutionRunDecisionRequest,
    CommercialOperationExecutionRunListResponse,
    CommercialOperationExecutionRunResponse,
    CommercialOperationExecutionRunUpdateRequest,
    CommercialOperationLinkCreateRequest,
    CommercialOperationLinkListResponse,
    CommercialOperationLinkResponse,
    CommercialOperationListResponse,
    CommercialOperationMonitoringObservationCreateRequest,
    CommercialOperationMonitoringObservationDecisionRequest,
    CommercialOperationMonitoringObservationListResponse,
    CommercialOperationMonitoringObservationResponse,
    CommercialOperationMonitoringObservationUpdateRequest,
    CommercialOperationOptimizationDecisionCreateRequest,
    CommercialOperationOptimizationDecisionDecisionRequest,
    CommercialOperationOptimizationDecisionListResponse,
    CommercialOperationOptimizationDecisionResponse,
    CommercialOperationOptimizationDecisionUpdateRequest,
    CommercialOperationPlanPreviewResponse,
    CommercialOperationResultCreateRequest,
    CommercialOperationResultDecisionRequest,
    CommercialOperationResultListResponse,
    CommercialOperationResultResponse,
    CommercialOperationResultUpdateRequest,
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


@router.post("/{operation_id}/approvals", response_model=CommercialOperationApprovalResponse, status_code=201)
async def create_commercial_operation_approval(
    operation_id: UUID,
    request: CommercialOperationApprovalCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Request human approval for one commercial operation plan step."""

    try:
        approval = await CommercialOperationService(session).create_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation approval create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation approval create failed", status_code=500) from exc


@router.get("/{operation_id}/approvals", response_model=CommercialOperationApprovalListResponse)
async def list_commercial_operation_approvals(
    operation_id: UUID,
    status: str | None = Query(default=None, description="pending / approved / rejected / cancelled"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalListResponse:
    """List approval gates for a commercial operation."""

    try:
        approvals = await CommercialOperationService(session).list_approvals(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationApprovalListResponse(
            operation_id=operation_id,
            items=[CommercialOperationApprovalResponse.from_model(approval) for approval in approvals],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation approval list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation approval list failed", status_code=500) from exc


@router.post("/{operation_id}/approvals/{approval_id}/approve", response_model=CommercialOperationApprovalResponse)
async def approve_commercial_operation_approval(
    operation_id: UUID,
    approval_id: UUID,
    request: CommercialOperationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Approve a pending commercial operation plan-step gate."""

    try:
        approval = await CommercialOperationService(session).approve_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            reviewer_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation approval approve API failed",
            extra={"operation_id": str(operation_id), "approval_id": str(approval_id)},
        )
        raise AppError("Commercial operation approval approve failed", status_code=500) from exc


@router.post("/{operation_id}/approvals/{approval_id}/reject", response_model=CommercialOperationApprovalResponse)
async def reject_commercial_operation_approval(
    operation_id: UUID,
    approval_id: UUID,
    request: CommercialOperationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Reject a pending commercial operation plan-step gate."""

    try:
        approval = await CommercialOperationService(session).reject_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            reviewer_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation approval reject API failed",
            extra={"operation_id": str(operation_id), "approval_id": str(approval_id)},
        )
        raise AppError("Commercial operation approval reject failed", status_code=500) from exc


@router.post("/{operation_id}/approvals/{approval_id}/cancel", response_model=CommercialOperationApprovalResponse)
async def cancel_commercial_operation_approval(
    operation_id: UUID,
    approval_id: UUID,
    request: CommercialOperationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationApprovalResponse:
    """Cancel a pending or approved commercial operation plan-step gate before execution."""

    try:
        approval = await CommercialOperationService(session).cancel_approval(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            approval_id=approval_id,
            reviewer_user_id=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationApprovalResponse.from_model(approval)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation approval cancel API failed",
            extra={"operation_id": str(operation_id), "approval_id": str(approval_id)},
        )
        raise AppError("Commercial operation approval cancel failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs", response_model=CommercialOperationDryRunResponse, status_code=201)
async def create_commercial_operation_dry_run(
    operation_id: UUID,
    request: CommercialOperationDryRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Create a metadata-only dry-run record from an approved operation approval."""

    try:
        dry_run = await CommercialOperationService(session).create_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation dry-run create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation dry-run create failed", status_code=500) from exc


@router.get("/{operation_id}/dry-runs", response_model=CommercialOperationDryRunListResponse)
async def list_commercial_operation_dry_runs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="created / completed / failed / cancelled"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunListResponse:
    """List metadata-only dry-run records for a commercial operation."""

    try:
        dry_runs = await CommercialOperationService(session).list_dry_runs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationDryRunListResponse(
            operation_id=operation_id,
            items=[CommercialOperationDryRunResponse.from_model(dry_run) for dry_run in dry_runs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation dry-run list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation dry-run list failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs/{dry_run_id}/complete", response_model=CommercialOperationDryRunResponse)
async def complete_commercial_operation_dry_run(
    operation_id: UUID,
    dry_run_id: UUID,
    request: CommercialOperationDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Mark a commercial operation dry-run record as completed without external execution."""

    try:
        dry_run = await CommercialOperationService(session).complete_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation dry-run complete API failed",
            extra={"operation_id": str(operation_id), "dry_run_id": str(dry_run_id)},
        )
        raise AppError("Commercial operation dry-run complete failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs/{dry_run_id}/fail", response_model=CommercialOperationDryRunResponse)
async def fail_commercial_operation_dry_run(
    operation_id: UUID,
    dry_run_id: UUID,
    request: CommercialOperationDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Mark a commercial operation dry-run record as failed without retrying external actions."""

    try:
        dry_run = await CommercialOperationService(session).fail_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation dry-run fail API failed",
            extra={"operation_id": str(operation_id), "dry_run_id": str(dry_run_id)},
        )
        raise AppError("Commercial operation dry-run fail failed", status_code=500) from exc


@router.post("/{operation_id}/dry-runs/{dry_run_id}/cancel", response_model=CommercialOperationDryRunResponse)
async def cancel_commercial_operation_dry_run(
    operation_id: UUID,
    dry_run_id: UUID,
    request: CommercialOperationDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDryRunResponse:
    """Cancel a created commercial operation dry-run record."""

    try:
        dry_run = await CommercialOperationService(session).cancel_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            dry_run_id=dry_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation dry-run cancel API failed",
            extra={"operation_id": str(operation_id), "dry_run_id": str(dry_run_id)},
        )
        raise AppError("Commercial operation dry-run cancel failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts", response_model=CommercialOperationContentDraftResponse, status_code=201)
async def create_commercial_operation_content_draft(
    operation_id: UUID,
    request: CommercialOperationContentDraftCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Create a non-publishing content draft for a commercial operation channel."""

    try:
        draft = await CommercialOperationService(session).create_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation content draft create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation content draft create failed", status_code=500) from exc


@router.get("/{operation_id}/content-drafts", response_model=CommercialOperationContentDraftListResponse)
async def list_commercial_operation_content_drafts(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftListResponse:
    """List non-publishing content drafts for a commercial operation."""

    try:
        drafts = await CommercialOperationService(session).list_content_drafts(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationContentDraftListResponse(
            operation_id=operation_id,
            items=[CommercialOperationContentDraftResponse.from_model(draft) for draft in drafts],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation content draft list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation content draft list failed", status_code=500) from exc


@router.patch("/{operation_id}/content-drafts/{draft_id}", response_model=CommercialOperationContentDraftResponse)
async def update_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Patch one commercial operation content draft without publishing it."""

    try:
        draft = await CommercialOperationService(session).update_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft update API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft update failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/ready", response_model=CommercialOperationContentDraftResponse)
async def ready_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Mark a content draft ready for human review."""

    try:
        draft = await CommercialOperationService(session).mark_content_draft_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft ready API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft ready failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/approve", response_model=CommercialOperationContentDraftResponse)
async def approve_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Approve a ready content draft without publishing it."""

    try:
        draft = await CommercialOperationService(session).approve_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft approve API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft approve failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/reject", response_model=CommercialOperationContentDraftResponse)
async def reject_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Reject a ready content draft without publishing it."""

    try:
        draft = await CommercialOperationService(session).reject_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft reject API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft reject failed", status_code=500) from exc


@router.post("/{operation_id}/content-drafts/{draft_id}/archive", response_model=CommercialOperationContentDraftResponse)
async def archive_commercial_operation_content_draft(
    operation_id: UUID,
    draft_id: UUID,
    request: CommercialOperationContentDraftDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Archive a content draft without deleting the audit trail."""

    try:
        draft = await CommercialOperationService(session).archive_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            draft_id=draft_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation content draft archive API failed",
            extra={"operation_id": str(operation_id), "draft_id": str(draft_id)},
        )
        raise AppError("Commercial operation content draft archive failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests", response_model=CommercialOperationAssetRequestResponse, status_code=201)
async def create_commercial_operation_asset_request(
    operation_id: UUID,
    request: CommercialOperationAssetRequestCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Create a non-executing first-class asset request."""

    try:
        asset_request = await CommercialOperationService(session).create_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation asset request create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation asset request create failed", status_code=500) from exc


@router.get("/{operation_id}/asset-requests", response_model=CommercialOperationAssetRequestListResponse)
async def list_commercial_operation_asset_requests(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / prepared / failed / archived"),
    content_draft_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestListResponse:
    """List non-executing asset requests for a commercial operation."""

    try:
        asset_requests = await CommercialOperationService(session).list_asset_requests(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            content_draft_id=content_draft_id,
            limit=limit,
        )
        return CommercialOperationAssetRequestListResponse(
            operation_id=operation_id,
            items=[CommercialOperationAssetRequestResponse.from_model(asset_request) for asset_request in asset_requests],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation asset request list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation asset request list failed", status_code=500) from exc


@router.patch("/{operation_id}/asset-requests/{asset_request_id}", response_model=CommercialOperationAssetRequestResponse)
async def update_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Patch one asset request without starting generation."""

    try:
        asset_request = await CommercialOperationService(session).update_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request update API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request update failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/ready", response_model=CommercialOperationAssetRequestResponse)
async def ready_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Mark an asset request ready for review."""

    try:
        asset_request = await CommercialOperationService(session).mark_asset_request_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request ready API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request ready failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/approve", response_model=CommercialOperationAssetRequestResponse)
async def approve_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Approve an asset request without generating assets."""

    try:
        asset_request = await CommercialOperationService(session).approve_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request approve API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request approve failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/reject", response_model=CommercialOperationAssetRequestResponse)
async def reject_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Reject an asset request without generating assets."""

    try:
        asset_request = await CommercialOperationService(session).reject_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request reject API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request reject failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/prepare", response_model=CommercialOperationAssetRequestResponse)
async def prepare_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Mark an approved asset request prepared for future ComfyUI handoff."""

    try:
        asset_request = await CommercialOperationService(session).prepare_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            prepared_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request prepare API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request prepare failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/fail", response_model=CommercialOperationAssetRequestResponse)
async def fail_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Mark an approved asset request failed during preparation."""

    try:
        asset_request = await CommercialOperationService(session).fail_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request fail API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request fail failed", status_code=500) from exc


@router.post("/{operation_id}/asset-requests/{asset_request_id}/archive", response_model=CommercialOperationAssetRequestResponse)
async def archive_commercial_operation_asset_request(
    operation_id: UUID,
    asset_request_id: UUID,
    request: CommercialOperationAssetRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Archive an asset request without deleting the audit trail."""

    try:
        asset_request = await CommercialOperationService(session).archive_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            asset_request_id=asset_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation asset request archive API failed",
            extra={"operation_id": str(operation_id), "asset_request_id": str(asset_request_id)},
        )
        raise AppError("Commercial operation asset request archive failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables", response_model=CommercialOperationDeliverableResponse, status_code=201)
async def create_commercial_operation_deliverable(
    operation_id: UUID,
    request: CommercialOperationDeliverableCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Create a reviewable deliverable and Output Library artifact without publishing."""

    try:
        deliverable = await CommercialOperationService(session).create_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation deliverable create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation deliverable create failed", status_code=500) from exc


@router.get("/{operation_id}/deliverables", response_model=CommercialOperationDeliverableListResponse)
async def list_commercial_operation_deliverables(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / packaged / failed / archived"),
    content_draft_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableListResponse:
    """List commercial deliverables for an operation."""

    try:
        deliverables = await CommercialOperationService(session).list_deliverables(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            content_draft_id=content_draft_id,
            limit=limit,
        )
        return CommercialOperationDeliverableListResponse(
            operation_id=operation_id,
            items=[CommercialOperationDeliverableResponse.from_model(deliverable) for deliverable in deliverables],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation deliverable list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation deliverable list failed", status_code=500) from exc


@router.patch("/{operation_id}/deliverables/{deliverable_id}", response_model=CommercialOperationDeliverableResponse)
async def update_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Patch a commercial deliverable and refresh its Output Library artifact."""

    try:
        deliverable = await CommercialOperationService(session).update_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable update API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable update failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/ready", response_model=CommercialOperationDeliverableResponse)
async def ready_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Mark a commercial deliverable ready for review."""

    try:
        deliverable = await CommercialOperationService(session).mark_deliverable_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable ready API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable ready failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/approve", response_model=CommercialOperationDeliverableResponse)
async def approve_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Approve a ready commercial deliverable without publishing it."""

    try:
        deliverable = await CommercialOperationService(session).approve_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable approve API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable approve failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/reject", response_model=CommercialOperationDeliverableResponse)
async def reject_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Reject a ready commercial deliverable without publishing it."""

    try:
        deliverable = await CommercialOperationService(session).reject_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable reject API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable reject failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/package", response_model=CommercialOperationDeliverableResponse)
async def package_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Package an approved deliverable for operator handoff without external execution."""

    try:
        deliverable = await CommercialOperationService(session).package_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            packaged_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable package API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable package failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/fail", response_model=CommercialOperationDeliverableResponse)
async def fail_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Mark an approved deliverable failed during packaging."""

    try:
        deliverable = await CommercialOperationService(session).fail_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable fail API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable fail failed", status_code=500) from exc


@router.post("/{operation_id}/deliverables/{deliverable_id}/archive", response_model=CommercialOperationDeliverableResponse)
async def archive_commercial_operation_deliverable(
    operation_id: UUID,
    deliverable_id: UUID,
    request: CommercialOperationDeliverableDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationDeliverableResponse:
    """Archive a commercial deliverable without deleting its artifact trail."""

    try:
        deliverable = await CommercialOperationService(session).archive_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=deliverable_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationDeliverableResponse.from_model(deliverable)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation deliverable archive API failed",
            extra={"operation_id": str(operation_id), "deliverable_id": str(deliverable_id)},
        )
        raise AppError("Commercial operation deliverable archive failed", status_code=500) from exc


@router.post("/{operation_id}/execution-requests", response_model=CommercialOperationExecutionRequestResponse, status_code=201)
async def create_commercial_operation_execution_request(
    operation_id: UUID,
    request: CommercialOperationExecutionRequestCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Create a metadata-only monitored execution request from a packaged deliverable."""

    try:
        execution_request = await CommercialOperationService(session).create_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution request create failed", status_code=500) from exc


@router.get("/{operation_id}/execution-requests", response_model=CommercialOperationExecutionRequestListResponse)
async def list_commercial_operation_execution_requests(
    operation_id: UUID,
    status: str | None = Query(
        default=None,
        description="draft / ready_for_review / approved / rejected / prepared / failed / cancelled / archived",
    ),
    deliverable_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestListResponse:
    """List metadata-only execution requests for a commercial operation."""

    try:
        requests = await CommercialOperationService(session).list_execution_requests(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            deliverable_id=deliverable_id,
            limit=limit,
        )
        return CommercialOperationExecutionRequestListResponse(
            operation_id=operation_id,
            items=[CommercialOperationExecutionRequestResponse.from_model(item) for item in requests],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution request list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/execution-requests/{execution_request_id}",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def update_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Patch an execution request before it is prepared or archived."""

    try:
        execution_request = await CommercialOperationService(session).update_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request update API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/ready",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def ready_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Mark an execution request ready for review."""

    try:
        execution_request = await CommercialOperationService(session).mark_execution_request_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request ready API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/approve",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def approve_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Approve an execution request without executing it."""

    try:
        execution_request = await CommercialOperationService(session).approve_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request approve API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/reject",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def reject_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Reject an execution request without executing it."""

    try:
        execution_request = await CommercialOperationService(session).reject_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request reject API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/prepare",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def prepare_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Prepare an approved request for future guarded runtime handoff."""

    try:
        execution_request = await CommercialOperationService(session).prepare_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            prepared_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request prepare API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request prepare failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/fail",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def fail_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Mark an approved execution request failed before any external runtime action."""

    try:
        execution_request = await CommercialOperationService(session).fail_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request fail API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/cancel",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def cancel_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Cancel an execution request before it is prepared."""

    try:
        execution_request = await CommercialOperationService(session).cancel_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request cancel API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-requests/{execution_request_id}/archive",
    response_model=CommercialOperationExecutionRequestResponse,
)
async def archive_commercial_operation_execution_request(
    operation_id: UUID,
    execution_request_id: UUID,
    request: CommercialOperationExecutionRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRequestResponse:
    """Archive an execution request while preserving the audit trail."""

    try:
        execution_request = await CommercialOperationService(session).archive_execution_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_request_id=execution_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationExecutionRequestResponse.from_model(execution_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution request archive API failed",
            extra={"operation_id": str(operation_id), "execution_request_id": str(execution_request_id)},
        )
        raise AppError("Commercial operation execution request archive failed", status_code=500) from exc


@router.post("/{operation_id}/execution-runs", response_model=CommercialOperationExecutionRunResponse, status_code=201)
async def create_commercial_operation_execution_run(
    operation_id: UUID,
    request: CommercialOperationExecutionRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Create a metadata-only execution run record from a prepared execution request."""

    try:
        execution_run = await CommercialOperationService(session).create_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            queued_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution run create failed", status_code=500) from exc


@router.get("/{operation_id}/execution-runs", response_model=CommercialOperationExecutionRunListResponse)
async def list_commercial_operation_execution_runs(
    operation_id: UUID,
    status: str | None = Query(
        default=None,
        description="queued / running / succeeded / failed / retrying / cancelled / archived",
    ),
    execution_request_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunListResponse:
    """List metadata-only execution run records for a commercial operation."""

    try:
        execution_runs = await CommercialOperationService(session).list_execution_runs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            execution_request_id=execution_request_id,
            limit=limit,
        )
        return CommercialOperationExecutionRunListResponse(
            operation_id=operation_id,
            items=[CommercialOperationExecutionRunResponse.from_model(item) for item in execution_runs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation execution run list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/execution-runs/{execution_run_id}",
    response_model=CommercialOperationExecutionRunResponse,
)
async def update_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Patch a queued or retrying metadata-only execution run record."""

    try:
        execution_run = await CommercialOperationService(session).update_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run update API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/start",
    response_model=CommercialOperationExecutionRunResponse,
)
async def start_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Mark a metadata-only execution run as running without calling an external runtime."""

    try:
        execution_run = await CommercialOperationService(session).start_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            started_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run start API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run start failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/succeed",
    response_model=CommercialOperationExecutionRunResponse,
)
async def succeed_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Mark a metadata-only execution run succeeded and record operator results."""

    try:
        execution_run = await CommercialOperationService(session).succeed_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            completed_by=context.user_id,
            result_summary=request.result_summary,
            result_payload=request.result_payload,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run succeed API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run succeed failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/fail",
    response_model=CommercialOperationExecutionRunResponse,
)
async def fail_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Mark a metadata-only execution run failed and record recovery context."""

    try:
        execution_run = await CommercialOperationService(session).fail_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
            result_payload=request.result_payload,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run fail API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/retry",
    response_model=CommercialOperationExecutionRunResponse,
)
async def retry_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Move a failed metadata-only execution run into retrying state."""

    try:
        execution_run = await CommercialOperationService(session).retry_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run retry API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run retry failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/cancel",
    response_model=CommercialOperationExecutionRunResponse,
)
async def cancel_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Cancel a queued, running, or retrying metadata-only execution run."""

    try:
        execution_run = await CommercialOperationService(session).cancel_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run cancel API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/execution-runs/{execution_run_id}/archive",
    response_model=CommercialOperationExecutionRunResponse,
)
async def archive_commercial_operation_execution_run(
    operation_id: UUID,
    execution_run_id: UUID,
    request: CommercialOperationExecutionRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationExecutionRunResponse:
    """Archive a metadata-only execution run while preserving the audit trail."""

    try:
        execution_run = await CommercialOperationService(session).archive_execution_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_run_id=execution_run_id,
            updated_by=context.user_id,
            operator_notes=request.operator_notes,
        )
        return CommercialOperationExecutionRunResponse.from_model(execution_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation execution run archive API failed",
            extra={"operation_id": str(operation_id), "execution_run_id": str(execution_run_id)},
        )
        raise AppError("Commercial operation execution run archive failed", status_code=500) from exc


@router.post("/{operation_id}/results", response_model=CommercialOperationResultResponse, status_code=201)
async def create_commercial_operation_result(
    operation_id: UUID,
    request: CommercialOperationResultCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Create an operator-reviewed commercial result record from a terminal execution run."""

    try:
        result = await CommercialOperationService(session).create_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation result create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation result create failed", status_code=500) from exc


@router.get("/{operation_id}/results", response_model=CommercialOperationResultListResponse)
async def list_commercial_operation_results(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    execution_run_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultListResponse:
    """List operator-reviewed commercial result records for a commercial operation."""

    try:
        results = await CommercialOperationService(session).list_results(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            execution_run_id=execution_run_id,
            limit=limit,
        )
        return CommercialOperationResultListResponse(
            operation_id=operation_id,
            items=[CommercialOperationResultResponse.from_model(item) for item in results],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation result list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation result list failed", status_code=500) from exc


@router.patch("/{operation_id}/results/{result_id}", response_model=CommercialOperationResultResponse)
async def update_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Patch a draft or rejected commercial result record."""

    try:
        result = await CommercialOperationService(session).update_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result update API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result update failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/ready", response_model=CommercialOperationResultResponse)
async def ready_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Mark a commercial result ready for review."""

    try:
        result = await CommercialOperationService(session).mark_result_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result ready API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result ready failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/approve", response_model=CommercialOperationResultResponse)
async def approve_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Approve a reviewed commercial result record."""

    try:
        result = await CommercialOperationService(session).approve_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result approve API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result approve failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/reject", response_model=CommercialOperationResultResponse)
async def reject_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Reject a reviewed commercial result record for revision."""

    try:
        result = await CommercialOperationService(session).reject_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result reject API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result reject failed", status_code=500) from exc


@router.post("/{operation_id}/results/{result_id}/archive", response_model=CommercialOperationResultResponse)
async def archive_commercial_operation_result(
    operation_id: UUID,
    result_id: UUID,
    request: CommercialOperationResultDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationResultResponse:
    """Archive a commercial result record while preserving the audit trail."""

    try:
        result = await CommercialOperationService(session).archive_result(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            result_id=result_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationResultResponse.from_model(result)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation result archive API failed",
            extra={"operation_id": str(operation_id), "result_id": str(result_id)},
        )
        raise AppError("Commercial operation result archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations",
    response_model=CommercialOperationMonitoringObservationResponse,
    status_code=201,
)
async def create_commercial_operation_monitoring_observation(
    operation_id: UUID,
    request: CommercialOperationMonitoringObservationCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Create an operator-reviewed monitoring observation from an approved commercial result."""

    try:
        observation = await CommercialOperationService(session).create_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation monitoring observation create failed", status_code=500) from exc


@router.get("/{operation_id}/monitoring-observations", response_model=CommercialOperationMonitoringObservationListResponse)
async def list_commercial_operation_monitoring_observations(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    result_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationListResponse:
    """List operator-reviewed monitoring observations for a commercial operation."""

    try:
        observations = await CommercialOperationService(session).list_monitoring_observations(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            result_id=result_id,
            limit=limit,
        )
        return CommercialOperationMonitoringObservationListResponse(
            operation_id=operation_id,
            items=[CommercialOperationMonitoringObservationResponse.from_model(item) for item in observations],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation monitoring observation list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/monitoring-observations/{observation_id}",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def update_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Patch a draft or rejected commercial monitoring observation."""

    try:
        observation = await CommercialOperationService(session).update_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation update API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/ready",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def ready_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Mark a commercial monitoring observation ready for review."""

    try:
        observation = await CommercialOperationService(session).mark_monitoring_observation_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation ready API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/approve",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def approve_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Approve a reviewed commercial monitoring observation."""

    try:
        observation = await CommercialOperationService(session).approve_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation approve API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/reject",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def reject_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Reject a reviewed commercial monitoring observation for revision."""

    try:
        observation = await CommercialOperationService(session).reject_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation reject API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/monitoring-observations/{observation_id}/archive",
    response_model=CommercialOperationMonitoringObservationResponse,
)
async def archive_commercial_operation_monitoring_observation(
    operation_id: UUID,
    observation_id: UUID,
    request: CommercialOperationMonitoringObservationDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationMonitoringObservationResponse:
    """Archive a commercial monitoring observation while preserving the audit trail."""

    try:
        observation = await CommercialOperationService(session).archive_monitoring_observation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            observation_id=observation_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationMonitoringObservationResponse.from_model(observation)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation monitoring observation archive API failed",
            extra={"operation_id": str(operation_id), "observation_id": str(observation_id)},
        )
        raise AppError("Commercial operation monitoring observation archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions",
    response_model=CommercialOperationOptimizationDecisionResponse,
    status_code=201,
)
async def create_commercial_operation_optimization_decision(
    operation_id: UUID,
    request: CommercialOperationOptimizationDecisionCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Create an operator-reviewed optimization decision from an approved monitoring observation."""

    try:
        decision = await CommercialOperationService(session).create_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation optimization decision create failed", status_code=500) from exc


@router.get("/{operation_id}/optimization-decisions", response_model=CommercialOperationOptimizationDecisionListResponse)
async def list_commercial_operation_optimization_decisions(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    observation_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionListResponse:
    """List operator-reviewed optimization decisions for a commercial operation."""

    try:
        decisions = await CommercialOperationService(session).list_optimization_decisions(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            observation_id=observation_id,
            limit=limit,
        )
        return CommercialOperationOptimizationDecisionListResponse(
            operation_id=operation_id,
            items=[CommercialOperationOptimizationDecisionResponse.from_model(item) for item in decisions],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation optimization decision list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def update_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Patch a draft or rejected commercial optimization decision."""

    try:
        decision = await CommercialOperationService(session).update_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision update API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/ready",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def ready_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Mark a commercial optimization decision ready for review."""

    try:
        decision = await CommercialOperationService(session).mark_optimization_decision_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision ready API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/approve",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def approve_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Approve a reviewed commercial optimization decision."""

    try:
        decision = await CommercialOperationService(session).approve_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision approve API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/reject",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def reject_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Reject a reviewed commercial optimization decision for revision."""

    try:
        decision = await CommercialOperationService(session).reject_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision reject API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/optimization-decisions/{optimization_decision_id}/archive",
    response_model=CommercialOperationOptimizationDecisionResponse,
)
async def archive_commercial_operation_optimization_decision(
    operation_id: UUID,
    optimization_decision_id: UUID,
    request: CommercialOperationOptimizationDecisionDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationOptimizationDecisionResponse:
    """Archive a commercial optimization decision while preserving the audit trail."""

    try:
        decision = await CommercialOperationService(session).archive_optimization_decision(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            decision_id=optimization_decision_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationOptimizationDecisionResponse.from_model(decision)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation optimization decision archive API failed",
            extra={"operation_id": str(operation_id), "optimization_decision_id": str(optimization_decision_id)},
        )
        raise AppError("Commercial operation optimization decision archive failed", status_code=500) from exc


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
