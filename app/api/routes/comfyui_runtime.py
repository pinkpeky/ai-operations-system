"""ComfyUI runtime adapter contract API routes."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.comfyui_runtime import ComfyUIRuntimeService
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.comfyui_runtime import (
    ComfyUIRuntimeCapabilitiesResponse,
    ComfyUIRuntimeConfigChangeDecisionRequest,
    ComfyUIRuntimeConfigChangeRequestCreateRequest,
    ComfyUIRuntimeConfigChangeRequestListResponse,
    ComfyUIRuntimeConfigChangeRequestResponse,
    ComfyUIRuntimeDiagnosticSnapshotCreateRequest,
    ComfyUIRuntimeDiagnosticSnapshotListResponse,
    ComfyUIRuntimeDiagnosticSnapshotResponse,
    ComfyUIRuntimeDiagnosticsResponse,
    ComfyUIRuntimeHealthResponse,
    ComfyUIRuntimeMaintenanceRunbookResponse,
    ComfyUIRuntimeManualApplyEvidenceCreateRequest,
    ComfyUIRuntimeManualApplyEvidenceDecisionRequest,
    ComfyUIRuntimeManualApplyEvidenceListResponse,
    ComfyUIRuntimeManualApplyEvidenceResponse,
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


@router.get("/maintenance-runbook", response_model=ComfyUIRuntimeMaintenanceRunbookResponse)
async def get_comfyui_runtime_maintenance_runbook(
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
) -> ComfyUIRuntimeMaintenanceRunbookResponse:
    """Return a no-network ComfyUI runtime maintenance runbook."""

    try:
        return ComfyUIRuntimeService(settings=settings).maintenance_runbook(workspace_id=context.workspace_id)
    except Exception as exc:
        logger.exception("ComfyUI runtime maintenance runbook API failed")
        raise AppError("ComfyUI runtime maintenance runbook failed", status_code=500) from exc


@router.post("/config-change-requests", response_model=ComfyUIRuntimeConfigChangeRequestResponse)
async def create_comfyui_runtime_config_change_request(
    request: ComfyUIRuntimeConfigChangeRequestCreateRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeConfigChangeRequestResponse:
    """Persist a metadata-only ComfyUI runtime configuration change request."""

    try:
        return await ComfyUIRuntimeService(settings=settings).create_config_change_request(
            session,
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            change_reason=request.change_reason,
            requested_changes=request.requested_changes,
            operator_note=request.operator_note,
            metadata=request.metadata,
        )
    except Exception as exc:
        logger.exception("ComfyUI runtime config change request create API failed")
        raise AppError("ComfyUI runtime config change request create failed", status_code=500) from exc


@router.get("/config-change-requests", response_model=ComfyUIRuntimeConfigChangeRequestListResponse)
async def list_comfyui_runtime_config_change_requests(
    limit: int = Query(default=20, ge=1, le=100),
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeConfigChangeRequestListResponse:
    """List metadata-only ComfyUI runtime configuration change requests."""

    try:
        return await ComfyUIRuntimeService(settings=settings).list_config_change_requests(
            session,
            workspace_id=context.workspace_id,
            limit=limit,
        )
    except Exception as exc:
        logger.exception("ComfyUI runtime config change request list API failed")
        raise AppError("ComfyUI runtime config change request list failed", status_code=500) from exc


async def _set_config_change_request_status(
    *,
    request_id: UUID,
    status: str,
    request: ComfyUIRuntimeConfigChangeDecisionRequest,
    context: WorkspaceContext,
    settings: Settings,
    session: AsyncSession,
) -> ComfyUIRuntimeConfigChangeRequestResponse:
    try:
        return await ComfyUIRuntimeService(settings=settings).update_config_change_request_status(
            session,
            workspace_id=context.workspace_id,
            request_id=request_id,
            status=status,
            reviewer_notes=request.reviewer_notes,
            metadata=request.metadata,
        )
    except LookupError as exc:
        raise AppError("ComfyUI runtime config change request not found", status_code=404) from exc
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("ComfyUI runtime config change request status API failed", extra={"request_id": str(request_id)})
        raise AppError("ComfyUI runtime config change request status update failed", status_code=500) from exc


@router.post("/config-change-requests/{request_id}/ready", response_model=ComfyUIRuntimeConfigChangeRequestResponse)
async def ready_comfyui_runtime_config_change_request(
    request_id: UUID,
    request: ComfyUIRuntimeConfigChangeDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeConfigChangeRequestResponse:
    """Mark a ComfyUI runtime configuration change request ready for review."""

    return await _set_config_change_request_status(
        request_id=request_id,
        status="ready_for_review",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/config-change-requests/{request_id}/approve", response_model=ComfyUIRuntimeConfigChangeRequestResponse)
async def approve_comfyui_runtime_config_change_request(
    request_id: UUID,
    request: ComfyUIRuntimeConfigChangeDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeConfigChangeRequestResponse:
    """Approve a metadata-only ComfyUI runtime configuration change request for manual apply."""

    return await _set_config_change_request_status(
        request_id=request_id,
        status="approved_for_manual_apply",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/config-change-requests/{request_id}/reject", response_model=ComfyUIRuntimeConfigChangeRequestResponse)
async def reject_comfyui_runtime_config_change_request(
    request_id: UUID,
    request: ComfyUIRuntimeConfigChangeDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeConfigChangeRequestResponse:
    """Reject a ComfyUI runtime configuration change request."""

    return await _set_config_change_request_status(
        request_id=request_id,
        status="rejected",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/config-change-requests/{request_id}/cancel", response_model=ComfyUIRuntimeConfigChangeRequestResponse)
async def cancel_comfyui_runtime_config_change_request(
    request_id: UUID,
    request: ComfyUIRuntimeConfigChangeDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeConfigChangeRequestResponse:
    """Cancel a ComfyUI runtime configuration change request."""

    return await _set_config_change_request_status(
        request_id=request_id,
        status="cancelled",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/config-change-requests/{request_id}/archive", response_model=ComfyUIRuntimeConfigChangeRequestResponse)
async def archive_comfyui_runtime_config_change_request(
    request_id: UUID,
    request: ComfyUIRuntimeConfigChangeDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeConfigChangeRequestResponse:
    """Archive a ComfyUI runtime configuration change request."""

    return await _set_config_change_request_status(
        request_id=request_id,
        status="archived",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post(
    "/config-change-requests/{request_id}/manual-apply-evidence",
    response_model=ComfyUIRuntimeManualApplyEvidenceResponse,
)
async def create_comfyui_runtime_manual_apply_evidence(
    request_id: UUID,
    request: ComfyUIRuntimeManualApplyEvidenceCreateRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeManualApplyEvidenceResponse:
    """Record metadata-only evidence for a human-applied ComfyUI runtime configuration change."""

    try:
        return await ComfyUIRuntimeService(settings=settings).create_manual_apply_evidence(
            session,
            workspace_id=context.workspace_id,
            request_id=request_id,
            user_id=context.user_id,
            before_snapshot_id=request.before_snapshot_id,
            after_snapshot_id=request.after_snapshot_id,
            manual_config_applied=request.manual_config_applied,
            service_restart_reported=request.service_restart_reported,
            manual_apply_steps=request.manual_apply_steps,
            restart_evidence=request.restart_evidence,
            rollback_notes=request.rollback_notes,
            verification_notes=request.verification_notes,
            operator_note=request.operator_note,
            metadata=request.metadata,
        )
    except LookupError as exc:
        raise AppError("ComfyUI runtime config change request not found", status_code=404) from exc
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("ComfyUI runtime manual apply evidence create API failed")
        raise AppError("ComfyUI runtime manual apply evidence create failed", status_code=500) from exc


@router.get("/manual-apply-evidence", response_model=ComfyUIRuntimeManualApplyEvidenceListResponse)
async def list_comfyui_runtime_manual_apply_evidence(
    limit: int = Query(default=20, ge=1, le=100),
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeManualApplyEvidenceListResponse:
    """List metadata-only ComfyUI runtime manual apply evidence records."""

    try:
        return await ComfyUIRuntimeService(settings=settings).list_manual_apply_evidence(
            session,
            workspace_id=context.workspace_id,
            limit=limit,
        )
    except Exception as exc:
        logger.exception("ComfyUI runtime manual apply evidence list API failed")
        raise AppError("ComfyUI runtime manual apply evidence list failed", status_code=500) from exc


async def _set_manual_apply_evidence_status(
    *,
    evidence_id: UUID,
    status: str,
    request: ComfyUIRuntimeManualApplyEvidenceDecisionRequest,
    context: WorkspaceContext,
    settings: Settings,
    session: AsyncSession,
) -> ComfyUIRuntimeManualApplyEvidenceResponse:
    try:
        return await ComfyUIRuntimeService(settings=settings).update_manual_apply_evidence_status(
            session,
            workspace_id=context.workspace_id,
            evidence_id=evidence_id,
            status=status,
            reviewer_notes=request.reviewer_notes,
            metadata=request.metadata,
        )
    except LookupError as exc:
        raise AppError("ComfyUI runtime manual apply evidence not found", status_code=404) from exc
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("ComfyUI runtime manual apply evidence status API failed", extra={"evidence_id": str(evidence_id)})
        raise AppError("ComfyUI runtime manual apply evidence status update failed", status_code=500) from exc


@router.post("/manual-apply-evidence/{evidence_id}/ready", response_model=ComfyUIRuntimeManualApplyEvidenceResponse)
async def ready_comfyui_runtime_manual_apply_evidence(
    evidence_id: UUID,
    request: ComfyUIRuntimeManualApplyEvidenceDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeManualApplyEvidenceResponse:
    """Mark ComfyUI runtime manual apply evidence ready for review."""

    return await _set_manual_apply_evidence_status(
        evidence_id=evidence_id,
        status="ready_for_review",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/manual-apply-evidence/{evidence_id}/verify", response_model=ComfyUIRuntimeManualApplyEvidenceResponse)
async def verify_comfyui_runtime_manual_apply_evidence(
    evidence_id: UUID,
    request: ComfyUIRuntimeManualApplyEvidenceDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeManualApplyEvidenceResponse:
    """Verify ComfyUI runtime manual apply evidence."""

    return await _set_manual_apply_evidence_status(
        evidence_id=evidence_id,
        status="verified",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/manual-apply-evidence/{evidence_id}/reject", response_model=ComfyUIRuntimeManualApplyEvidenceResponse)
async def reject_comfyui_runtime_manual_apply_evidence(
    evidence_id: UUID,
    request: ComfyUIRuntimeManualApplyEvidenceDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeManualApplyEvidenceResponse:
    """Reject ComfyUI runtime manual apply evidence."""

    return await _set_manual_apply_evidence_status(
        evidence_id=evidence_id,
        status="rejected",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/manual-apply-evidence/{evidence_id}/fail", response_model=ComfyUIRuntimeManualApplyEvidenceResponse)
async def fail_comfyui_runtime_manual_apply_evidence(
    evidence_id: UUID,
    request: ComfyUIRuntimeManualApplyEvidenceDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeManualApplyEvidenceResponse:
    """Mark ComfyUI runtime manual apply evidence failed."""

    return await _set_manual_apply_evidence_status(
        evidence_id=evidence_id,
        status="failed",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


@router.post("/manual-apply-evidence/{evidence_id}/archive", response_model=ComfyUIRuntimeManualApplyEvidenceResponse)
async def archive_comfyui_runtime_manual_apply_evidence(
    evidence_id: UUID,
    request: ComfyUIRuntimeManualApplyEvidenceDecisionRequest,
    context: WorkspaceContext = Depends(get_workspace_context),
    settings: Settings = Depends(get_settings),
    session: AsyncSession = Depends(get_session),
) -> ComfyUIRuntimeManualApplyEvidenceResponse:
    """Archive ComfyUI runtime manual apply evidence."""

    return await _set_manual_apply_evidence_status(
        evidence_id=evidence_id,
        status="archived",
        request=request,
        context=context,
        settings=settings,
        session=session,
    )


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
