"""Commercial operations API routes."""

from __future__ import annotations

import logging
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.routes.rag import build_retrieved_chunk_from_reranked, create_hybrid_search_pipeline
from app.commercial_operations.service import CommercialOperationService
from app.core.config import get_settings
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.reranker.reranker_client import RerankerClient
from app.schemas.commercial_operation import (
    CommercialOperationApprovalCreateRequest,
    CommercialOperationApprovalDecisionRequest,
    CommercialOperationApprovalListResponse,
    CommercialOperationApprovalResponse,
    CommercialOperationAssetRequestCreateRequest,
    CommercialOperationAssetRequestDecisionRequest,
    CommercialOperationAssetRequestGenerateRequest,
    CommercialOperationAssetRequestListResponse,
    CommercialOperationAssetRequestResponse,
    CommercialOperationAssetRequestUpdateRequest,
    CommercialOperationComfyUIAdapterConfigCreateRequest,
    CommercialOperationComfyUIAdapterConfigDecisionRequest,
    CommercialOperationComfyUIAdapterConfigListResponse,
    CommercialOperationComfyUIAdapterConfigResponse,
    CommercialOperationComfyUIAdapterConfigUpdateRequest,
    CommercialOperationComfyUIAdapterDispatchCreateRequest,
    CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    CommercialOperationComfyUIAdapterDispatchListResponse,
    CommercialOperationComfyUIAdapterDispatchResponse,
    CommercialOperationComfyUIAdapterDispatchUpdateRequest,
    CommercialOperationComfyUIConnectionProbeCreateRequest,
    CommercialOperationComfyUIConnectionProbeDecisionRequest,
    CommercialOperationComfyUIConnectionProbeListResponse,
    CommercialOperationComfyUIConnectionProbeResponse,
    CommercialOperationComfyUIConnectionProbeUpdateRequest,
    CommercialOperationComfyUIExecutionPlanCreateRequest,
    CommercialOperationComfyUIExecutionPlanDecisionRequest,
    CommercialOperationComfyUIExecutionPlanListResponse,
    CommercialOperationComfyUIExecutionPlanResponse,
    CommercialOperationComfyUIExecutionPlanUpdateRequest,
    CommercialOperationComfyUIHandoffCreateRequest,
    CommercialOperationComfyUIHandoffDecisionRequest,
    CommercialOperationComfyUIHandoffListResponse,
    CommercialOperationComfyUIHandoffResponse,
    CommercialOperationComfyUIHandoffUpdateRequest,
    CommercialOperationComfyUIJobRequestCreateRequest,
    CommercialOperationComfyUIJobRequestDecisionRequest,
    CommercialOperationComfyUIJobRequestListResponse,
    CommercialOperationComfyUIJobRequestResponse,
    CommercialOperationComfyUIJobRequestUpdateRequest,
    CommercialOperationComfyUIPreflightCreateRequest,
    CommercialOperationComfyUIPreflightDecisionRequest,
    CommercialOperationComfyUIPreflightListResponse,
    CommercialOperationComfyUIPreflightResponse,
    CommercialOperationComfyUIPreflightUpdateRequest,
    CommercialOperationComfyUIRuntimeGateCreateRequest,
    CommercialOperationComfyUIRuntimeGateDecisionRequest,
    CommercialOperationComfyUIRuntimeGateListResponse,
    CommercialOperationComfyUIRuntimeGateResponse,
    CommercialOperationComfyUIRuntimeGateUpdateRequest,
    CommercialOperationComfyUIRuntimeDryRunCreateRequest,
    CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    CommercialOperationComfyUIRuntimeDryRunListResponse,
    CommercialOperationComfyUIRuntimeDryRunResponse,
    CommercialOperationComfyUIRuntimeDryRunUpdateRequest,
    CommercialOperationContentDraftCreateRequest,
    CommercialOperationContentDraftDecisionRequest,
    CommercialOperationContentDraftGenerateRequest,
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
    CommercialOperationEvidenceSnapshotCreateRequest,
    CommercialOperationEvidenceSnapshotDecisionRequest,
    CommercialOperationEvidenceSnapshotGenerateRequest,
    CommercialOperationEvidenceSnapshotListResponse,
    CommercialOperationEvidenceSnapshotResponse,
    CommercialOperationEvidenceSnapshotUpdateRequest,
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


def _clean_optional_text(value: str | None) -> str | None:
    return value.strip() if value and value.strip() else None


def _rag_generation_query(
    *,
    operation_title: str,
    operation_objective: str,
    deliverable_title: str,
    deliverable_summary: str | None,
    requested_query: str | None,
) -> str:
    clean_query = _clean_optional_text(requested_query)
    if clean_query:
        return clean_query
    pieces = [
        operation_title,
        operation_objective,
        deliverable_title,
        deliverable_summary or "",
    ]
    return " ".join(piece.strip() for piece in pieces if piece and piece.strip())[:1000]


def _rag_operation_query(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    channels: list[str] | None,
    success_metrics: list[str] | None,
    requested_query: str | None,
) -> str:
    clean_query = _clean_optional_text(requested_query)
    if clean_query:
        return clean_query
    pieces = [
        operation_title,
        operation_objective,
        target_audience or "",
        " ".join(channels or []),
        " ".join(success_metrics or []),
    ]
    return " ".join(piece.strip() for piece in pieces if piece and piece.strip())[:1000]


def _rag_evidence_item(chunk: Any) -> dict[str, Any]:
    metadata = dict(getattr(chunk, "metadata", {}) or {})
    score = (
        getattr(chunk, "rerank_score", None)
        or getattr(chunk, "hybrid_score", None)
        or getattr(chunk, "keyword_score", None)
        or getattr(chunk, "dense_score", None)
        or getattr(chunk, "similarity_score", None)
    )
    text = getattr(chunk, "text", "") or ""
    return {
        "chunk_id": getattr(chunk, "id", None),
        "document_id": metadata.get("document_id"),
        "source_id": metadata.get("source_id"),
        "chunk_index": getattr(chunk, "chunk_index", None),
        "score": score,
        "text_excerpt": text[:800],
        "metadata": metadata,
        "evidence_boundary": "retrieved from existing RAG index; not auto-approved or externally executed",
    }


def _rag_source_materials(*, collection_name: str, evidence_items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    materials: list[str] = []
    candidates: list[str] = [f"rag:{collection_name}"]
    for item in evidence_items:
        document_id = item.get("document_id")
        source_id = item.get("source_id")
        if isinstance(document_id, str) and document_id:
            candidates.append(f"document:{document_id}")
        if isinstance(source_id, str) and source_id:
            candidates.append(f"source:{source_id}")
    for candidate in candidates:
        if candidate not in seen:
            seen.add(candidate)
            materials.append(candidate)
    return materials


def _rag_content_draft_body(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    channel: str,
    content_format: str,
    query: str,
    evidence_items: list[dict[str, Any]],
    call_to_action: str | None,
) -> str:
    audience = target_audience or "target audience"
    evidence_lines = [
        (
            f"- {str(item.get('text_excerpt') or '').strip()[:240]} "
            f"(document: {item.get('document_id') or 'unknown'}, source: {item.get('source_id') or 'unknown'})"
        )
        for item in evidence_items
        if str(item.get("text_excerpt") or "").strip()
    ]
    if not evidence_lines:
        evidence_lines = [
            "- No retrieved RAG chunks; revise the query or attach source material before review."
        ]
    proof_points = [
        str(item.get("text_excerpt") or "").strip()[:160]
        for item in evidence_items[:3]
        if str(item.get("text_excerpt") or "").strip()
    ]
    proof_sentence = " ".join(proof_points) if proof_points else "Evidence still needs operator review before use."
    return "\n".join(
        [
            f"Channel: {channel}",
            f"Format: {content_format}",
            f"Operation: {operation_title}",
            f"Audience: {audience}",
            f"Objective: {operation_objective}",
            f"RAG query: {query}",
            "",
            "RAG evidence used:",
            *evidence_lines,
            "",
            "Draft:",
            f"Opening: Address {audience} with the operation goal: {operation_objective}",
            f"Proof points: {proof_sentence}",
            f"Call to action: {call_to_action or 'Confirm the next step with the operator.'}",
            "",
            (
                "Review boundary: draft only; no publishing, account control, ComfyUI, OpenClaw, "
                "or browser worker action was executed."
            ),
        ]
    )


def _rag_asset_brief_query(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    success_metrics: list[str] | None,
    channel: str,
    asset_type: str,
    content_draft: Any | None,
    requested_query: str | None,
) -> str:
    clean_query = _clean_optional_text(requested_query)
    if clean_query:
        return clean_query
    draft_body = getattr(content_draft, "content_body", "") if content_draft else ""
    pieces = [
        operation_title,
        operation_objective,
        target_audience or "",
        " ".join(success_metrics or []),
        channel,
        asset_type,
        getattr(content_draft, "title", "") if content_draft else "",
        getattr(content_draft, "summary", "") if content_draft else "",
        str(draft_body or "")[:500],
    ]
    return " ".join(piece.strip() for piece in pieces if piece and piece.strip())[:1000]


def _rag_asset_generation_prompt(
    *,
    operation_title: str,
    operation_objective: str,
    target_audience: str | None,
    channel: str,
    asset_type: str,
    purpose: str,
    style_constraints: str,
    dimensions: str | None,
    query: str,
    evidence_items: list[dict[str, Any]],
    content_draft: Any | None,
) -> str:
    audience = target_audience or "target audience"
    evidence_lines = [
        (
            f"- {str(item.get('text_excerpt') or '').strip()[:240]} "
            f"(document: {item.get('document_id') or 'unknown'}, source: {item.get('source_id') or 'unknown'})"
        )
        for item in evidence_items
        if str(item.get("text_excerpt") or "").strip()
    ]
    if not evidence_lines:
        evidence_lines = ["- No retrieved RAG chunks; revise the query or attach source material before review."]
    draft_context = ""
    if content_draft is not None:
        draft_context = " ".join(
            piece.strip()
            for piece in [
                getattr(content_draft, "title", "") or "",
                getattr(content_draft, "summary", "") or "",
                getattr(content_draft, "call_to_action", "") or "",
            ]
            if piece and piece.strip()
        )
    return "\n".join(
        [
            f"Asset type: {asset_type}",
            f"Channel: {channel}",
            f"Operation: {operation_title}",
            f"Audience: {audience}",
            f"Objective: {operation_objective}",
            f"Purpose: {purpose}",
            f"Dimensions: {dimensions or 'operator-selected dimensions'}",
            f"Style constraints: {style_constraints}",
            f"RAG query: {query}",
            "",
            "Source evidence:",
            *evidence_lines,
            "",
            "Visual brief:",
            f"Create a reviewable {asset_type} asset brief for {channel} that supports: {operation_objective}",
            "Use the reviewed knowledge points as conceptual guidance only.",
            f"Draft context: {draft_context or 'no linked content draft'}",
            "",
            (
                "Execution boundary: brief only; no ComfyUI job, OpenClaw action, browser worker action, "
                "publishing, account control, or approval bypass was executed."
            ),
        ]
    )


def _rag_asset_readiness_checks(
    *,
    requested_checks: list[str],
    evidence_items: list[dict[str, Any]],
) -> list[str]:
    seen: set[str] = set()
    checks: list[str] = []
    candidates = [
        *requested_checks,
        "RAG search completed against existing knowledge index",
        "operator must review source materials before approval",
        "no ComfyUI job was created",
        "no publishing or account action was executed",
    ]
    if not evidence_items:
        candidates.append("no retrieved chunks; revise query or attach source material before approval")
    for candidate in candidates:
        clean_candidate = candidate.strip() if candidate else ""
        if clean_candidate and clean_candidate not in seen:
            seen.add(clean_candidate)
            checks.append(clean_candidate)
    return checks


def _unique_document_ids(evidence_items: list[dict[str, Any]]) -> list[str]:
    seen: set[str] = set()
    document_ids: list[str] = []
    for item in evidence_items:
        document_id = item.get("document_id")
        if isinstance(document_id, str) and document_id and document_id not in seen:
            seen.add(document_id)
            document_ids.append(document_id)
    return document_ids


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


@router.post(
    "/{operation_id}/content-drafts/generate-rag",
    response_model=CommercialOperationContentDraftResponse,
    status_code=201,
)
async def generate_commercial_operation_content_draft_from_rag(
    operation_id: UUID,
    request: CommercialOperationContentDraftGenerateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationContentDraftResponse:
    """Generate a draft content record from existing RAG search results."""

    try:
        service = CommercialOperationService(session)
        operation = await service.require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        settings = get_settings()
        search_mode = request.search_mode or settings.default_search_mode
        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        dense_top_k = request.dense_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or settings.final_top_k
        query = _rag_operation_query(
            operation_title=operation.title,
            operation_objective=operation.objective,
            target_audience=operation.target_audience,
            channels=operation.channels,
            success_metrics=operation.success_metrics,
            requested_query=request.query,
        )
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=_clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
        )
        bundle = await pipeline.search(
            query=query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=_clean_optional_text(request.source_id),
            workspace_id=context.workspace_id,
        )
        reranked = await RerankerClient(settings=settings).rerank(
            query=query,
            chunks=bundle.merged_results,
            top_n=final_top_k,
        )
        retrieved_chunks = [build_retrieved_chunk_from_reranked(result) for result in reranked]
        evidence_items = [_rag_evidence_item(chunk) for chunk in retrieved_chunks]
        collection_name = pipeline.vector_store.collection_name
        source_materials = _rag_source_materials(collection_name=collection_name, evidence_items=evidence_items)
        summary = _clean_optional_text(request.summary) or (
            f"Generated from {len(evidence_items)} existing RAG chunk(s) for query: {query}"
            if evidence_items
            else f"RAG search returned no chunks for query: {query}"
        )
        draft = await service.create_content_draft(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            step_key=request.step_key,
            channel=request.channel,
            content_format=request.content_format,
            title=_clean_optional_text(request.title) or f"RAG content draft: {operation.title}",
            audience_segment=request.audience_segment or operation.target_audience,
            content_body=_rag_content_draft_body(
                operation_title=operation.title,
                operation_objective=operation.objective,
                target_audience=request.audience_segment or operation.target_audience,
                channel=request.channel,
                content_format=request.content_format,
                query=query,
                evidence_items=evidence_items,
                call_to_action=request.call_to_action,
            ),
            summary=summary,
            call_to_action=request.call_to_action,
            source_materials=source_materials,
            asset_requests=request.asset_requests,
            created_by=context.user_id,
            metadata={
                **request.metadata,
                "source": "commercial_operations_rag_content_generation",
                "phase": "61O",
                "generation_mode": "rag_content_draft",
                "query": query,
                "collection_name": collection_name,
                "source_id": _clean_optional_text(request.source_id),
                "search_mode": search_mode,
                "dense_top_k": dense_top_k,
                "keyword_top_k": keyword_top_k,
                "final_top_k": final_top_k,
                "rag_result_count": len(evidence_items),
                "dense_candidate_count": len(bundle.dense_results),
                "keyword_candidate_count": len(bundle.keyword_results),
                "merged_candidate_count": len(bundle.merged_results),
                "forbidden_actions": [
                    "no knowledge ingestion",
                    "no automatic approval",
                    "no publishing",
                    "no account control",
                    "no ComfyUI, OpenClaw, or browser worker execution",
                ],
            },
        )
        return CommercialOperationContentDraftResponse.from_model(draft)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation RAG content draft generate API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation RAG content draft generate failed", status_code=500) from exc


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


@router.post(
    "/{operation_id}/asset-requests/generate-rag",
    response_model=CommercialOperationAssetRequestResponse,
    status_code=201,
)
async def generate_commercial_operation_asset_request_from_rag(
    operation_id: UUID,
    request: CommercialOperationAssetRequestGenerateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationAssetRequestResponse:
    """Generate a non-executing asset request brief from existing RAG search results."""

    try:
        service = CommercialOperationService(session)
        operation = await service.require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        content_draft = None
        if request.content_draft_id is not None:
            content_draft = await service.require_content_draft(
                workspace_id=context.workspace_id,
                operation_id=operation_id,
                draft_id=request.content_draft_id,
            )
        settings = get_settings()
        search_mode = request.search_mode or settings.default_search_mode
        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        dense_top_k = request.dense_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or settings.final_top_k
        query = _rag_asset_brief_query(
            operation_title=operation.title,
            operation_objective=operation.objective,
            target_audience=operation.target_audience,
            success_metrics=operation.success_metrics,
            channel=request.channel,
            asset_type=request.asset_type,
            content_draft=content_draft,
            requested_query=request.query,
        )
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=_clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
        )
        bundle = await pipeline.search(
            query=query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=_clean_optional_text(request.source_id),
            workspace_id=context.workspace_id,
        )
        reranked = await RerankerClient(settings=settings).rerank(
            query=query,
            chunks=bundle.merged_results,
            top_n=final_top_k,
        )
        retrieved_chunks = [build_retrieved_chunk_from_reranked(result) for result in reranked]
        evidence_items = [_rag_evidence_item(chunk) for chunk in retrieved_chunks]
        collection_name = pipeline.vector_store.collection_name
        source_materials = _rag_source_materials(collection_name=collection_name, evidence_items=evidence_items)
        for material in getattr(content_draft, "source_materials", []) or []:
            if isinstance(material, str) and material.strip() and material.strip() not in source_materials:
                source_materials.append(material.strip())
        purpose = _clean_optional_text(request.purpose) or (
            f"Prepare a reviewable {request.asset_type} asset brief for {request.channel} using existing RAG evidence."
        )
        style_constraints = _clean_optional_text(request.style_constraints) or (
            "Use only reviewed source context; avoid real logos, private data, unreadable text, and unsupported claims."
        )
        asset_request = await service.create_asset_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            step_key=request.step_key,
            content_draft_id=request.content_draft_id,
            channel=request.channel,
            asset_type=request.asset_type,
            title=_clean_optional_text(request.title) or f"RAG asset brief: {operation.title}",
            purpose=purpose,
            dimensions=request.dimensions,
            style_constraints=style_constraints,
            generation_prompt=_rag_asset_generation_prompt(
                operation_title=operation.title,
                operation_objective=operation.objective,
                target_audience=operation.target_audience,
                channel=request.channel,
                asset_type=request.asset_type,
                purpose=purpose,
                style_constraints=style_constraints,
                dimensions=request.dimensions,
                query=query,
                evidence_items=evidence_items,
                content_draft=content_draft,
            ),
            negative_prompt=_clean_optional_text(request.negative_prompt)
            or "No real logos, no private data, no unsupported claims, no unreadable text.",
            source_materials=source_materials,
            readiness_checks=_rag_asset_readiness_checks(
                requested_checks=request.readiness_checks,
                evidence_items=evidence_items,
            ),
            requested_by=context.user_id,
            metadata={
                **request.metadata,
                "source": "commercial_operations_rag_asset_generation",
                "phase": "61P",
                "generation_mode": "rag_asset_brief",
                "query": query,
                "collection_name": collection_name,
                "source_id": _clean_optional_text(request.source_id),
                "search_mode": search_mode,
                "dense_top_k": dense_top_k,
                "keyword_top_k": keyword_top_k,
                "final_top_k": final_top_k,
                "rag_result_count": len(evidence_items),
                "dense_candidate_count": len(bundle.dense_results),
                "keyword_candidate_count": len(bundle.keyword_results),
                "merged_candidate_count": len(bundle.merged_results),
                "content_draft_id": str(request.content_draft_id) if request.content_draft_id else None,
                "forbidden_actions": [
                    "no knowledge ingestion",
                    "no automatic approval",
                    "no publishing",
                    "no account control",
                    "no ComfyUI, OpenClaw, or browser worker execution",
                ],
            },
        )
        return CommercialOperationAssetRequestResponse.from_model(asset_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation RAG asset request generate API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation RAG asset request generate failed", status_code=500) from exc


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


@router.post("/{operation_id}/comfyui-handoffs", response_model=CommercialOperationComfyUIHandoffResponse, status_code=201)
async def create_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    request: CommercialOperationComfyUIHandoffCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Create a metadata-only ComfyUI handoff from an approved asset request."""

    try:
        handoff = await CommercialOperationService(session).create_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI handoff create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI handoff create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-handoffs", response_model=CommercialOperationComfyUIHandoffListResponse)
async def list_commercial_operation_comfyui_handoffs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / prepared / failed / archived"),
    asset_request_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffListResponse:
    """List metadata-only ComfyUI handoffs for a commercial operation."""

    try:
        handoffs = await CommercialOperationService(session).list_comfyui_handoffs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            asset_request_id=asset_request_id,
            limit=limit,
        )
        return CommercialOperationComfyUIHandoffListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIHandoffResponse.from_model(handoff) for handoff in handoffs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI handoff list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI handoff list failed", status_code=500) from exc


@router.patch("/{operation_id}/comfyui-handoffs/{handoff_id}", response_model=CommercialOperationComfyUIHandoffResponse)
async def update_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Patch one metadata-only ComfyUI handoff without submitting jobs."""

    try:
        handoff = await CommercialOperationService(session).update_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff update API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff update failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/ready", response_model=CommercialOperationComfyUIHandoffResponse)
async def ready_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Mark a metadata-only ComfyUI handoff ready for review."""

    try:
        handoff = await CommercialOperationService(session).mark_comfyui_handoff_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff ready API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff ready failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/approve", response_model=CommercialOperationComfyUIHandoffResponse)
async def approve_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Approve a metadata-only ComfyUI handoff without generating assets."""

    try:
        handoff = await CommercialOperationService(session).approve_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff approve API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff approve failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/reject", response_model=CommercialOperationComfyUIHandoffResponse)
async def reject_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Reject a metadata-only ComfyUI handoff without generating assets."""

    try:
        handoff = await CommercialOperationService(session).reject_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff reject API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff reject failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/prepare", response_model=CommercialOperationComfyUIHandoffResponse)
async def prepare_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Mark an approved ComfyUI handoff prepared for a future guarded adapter."""

    try:
        handoff = await CommercialOperationService(session).prepare_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            prepared_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff prepare API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff prepare failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/fail", response_model=CommercialOperationComfyUIHandoffResponse)
async def fail_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Mark an approved ComfyUI handoff failed during preparation."""

    try:
        handoff = await CommercialOperationService(session).fail_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff fail API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff fail failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-handoffs/{handoff_id}/archive", response_model=CommercialOperationComfyUIHandoffResponse)
async def archive_commercial_operation_comfyui_handoff(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIHandoffDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIHandoffResponse:
    """Archive a ComfyUI handoff without deleting the audit trail."""

    try:
        handoff = await CommercialOperationService(session).archive_comfyui_handoff(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIHandoffResponse.from_model(handoff)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI handoff archive API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI handoff archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-handoffs/{handoff_id}/preflights",
    response_model=CommercialOperationComfyUIPreflightResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    handoff_id: UUID,
    request: CommercialOperationComfyUIPreflightCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Create a metadata-only ComfyUI adapter readiness preflight for a handoff."""

    try:
        preflight = await CommercialOperationService(session).create_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            handoff_id=handoff_id,
            checked_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight create API failed",
            extra={"operation_id": str(operation_id), "handoff_id": str(handoff_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-preflights", response_model=CommercialOperationComfyUIPreflightListResponse)
async def list_commercial_operation_comfyui_preflights(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / checked / blocked / failed / archived"),
    handoff_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightListResponse:
    """List metadata-only ComfyUI preflights for a commercial operation."""

    try:
        preflights = await CommercialOperationService(session).list_comfyui_preflights(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            handoff_id=handoff_id,
            limit=limit,
        )
        return CommercialOperationComfyUIPreflightListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIPreflightResponse.from_model(preflight) for preflight in preflights],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI preflight list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI preflight list failed", status_code=500) from exc


@router.patch("/{operation_id}/comfyui-preflights/{preflight_id}", response_model=CommercialOperationComfyUIPreflightResponse)
async def update_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Patch a ComfyUI preflight and rerun metadata-only readiness evaluation."""

    try:
        preflight = await CommercialOperationService(session).update_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight update API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight update failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-preflights/{preflight_id}/check", response_model=CommercialOperationComfyUIPreflightResponse)
async def check_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Re-run local ComfyUI preflight evaluation without calling ComfyUI."""

    _ = request
    try:
        preflight = await CommercialOperationService(session).check_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            checked_by=context.user_id,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight check API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight check failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-preflights/{preflight_id}/fail", response_model=CommercialOperationComfyUIPreflightResponse)
async def fail_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Mark a ComfyUI preflight failed without external execution."""

    try:
        preflight = await CommercialOperationService(session).fail_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight fail API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight fail failed", status_code=500) from exc


@router.post("/{operation_id}/comfyui-preflights/{preflight_id}/archive", response_model=CommercialOperationComfyUIPreflightResponse)
async def archive_commercial_operation_comfyui_preflight(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIPreflightDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIPreflightResponse:
    """Archive a ComfyUI preflight without deleting its audit trail."""

    _ = request
    try:
        preflight = await CommercialOperationService(session).archive_comfyui_preflight(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            archived_by=context.user_id,
        )
        return CommercialOperationComfyUIPreflightResponse.from_model(preflight)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI preflight archive API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI preflight archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Create a metadata-only ComfyUI adapter config for server maintainers."""

    try:
        config = await CommercialOperationService(session).create_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI adapter config create API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI adapter config create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-adapter-configs", response_model=CommercialOperationComfyUIAdapterConfigListResponse)
async def list_commercial_operation_comfyui_adapter_configs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready / blocked / failed / archived"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigListResponse:
    """List metadata-only ComfyUI adapter configs for a commercial operation."""

    try:
        configs = await CommercialOperationService(session).list_comfyui_adapter_configs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            limit=limit,
        )
        return CommercialOperationComfyUIAdapterConfigListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIAdapterConfigResponse.from_model(config) for config in configs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI adapter config list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI adapter config list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-adapter-configs/{config_id}",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def update_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Patch a ComfyUI adapter config and rerun metadata-only validation."""

    try:
        config = await CommercialOperationService(session).update_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config update API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs/{config_id}/validate",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def validate_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Re-run local ComfyUI adapter config validation without calling ComfyUI."""

    _ = request
    try:
        config = await CommercialOperationService(session).validate_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            validated_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config validate API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config validate failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs/{config_id}/fail",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def fail_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Mark a ComfyUI adapter config failed without external execution."""

    try:
        config = await CommercialOperationService(session).fail_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config fail API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-configs/{config_id}/archive",
    response_model=CommercialOperationComfyUIAdapterConfigResponse,
)
async def archive_commercial_operation_comfyui_adapter_config(
    operation_id: UUID,
    config_id: UUID,
    request: CommercialOperationComfyUIAdapterConfigDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterConfigResponse:
    """Archive a ComfyUI adapter config without deleting its audit trail."""

    _ = request
    try:
        config = await CommercialOperationService(session).archive_comfyui_adapter_config(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            config_id=config_id,
            archived_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterConfigResponse.from_model(config)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter config archive API failed",
            extra={"operation_id": str(operation_id), "config_id": str(config_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter config archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-preflights/{preflight_id}/job-requests",
    response_model=CommercialOperationComfyUIJobRequestResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    preflight_id: UUID,
    request: CommercialOperationComfyUIJobRequestCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Create a metadata-only ComfyUI job request from a checked preflight."""

    try:
        job_request = await CommercialOperationService(session).create_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            preflight_id=preflight_id,
            requested_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request create API failed",
            extra={"operation_id": str(operation_id), "preflight_id": str(preflight_id)},
        )
        raise AppError("Commercial operation ComfyUI job request create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-job-requests", response_model=CommercialOperationComfyUIJobRequestListResponse)
async def list_commercial_operation_comfyui_job_requests(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / queued / failed / cancelled / archived"),
    preflight_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestListResponse:
    """List metadata-only ComfyUI job requests for a commercial operation."""

    try:
        job_requests = await CommercialOperationService(session).list_comfyui_job_requests(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            preflight_id=preflight_id,
            limit=limit,
        )
        return CommercialOperationComfyUIJobRequestListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIJobRequestResponse.from_model(item) for item in job_requests],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI job request list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI job request list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-job-requests/{job_request_id}",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def update_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Patch a metadata-only ComfyUI job request before queue handoff."""

    try:
        job_request = await CommercialOperationService(session).update_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request update API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/ready",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def ready_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Mark a metadata-only ComfyUI job request ready for review."""

    try:
        job_request = await CommercialOperationService(session).mark_comfyui_job_request_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request ready API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/approve",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def approve_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Approve a metadata-only ComfyUI job request without submitting it."""

    try:
        job_request = await CommercialOperationService(session).approve_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request approve API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/reject",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def reject_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Reject a metadata-only ComfyUI job request without submitting it."""

    try:
        job_request = await CommercialOperationService(session).reject_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request reject API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/queue",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def queue_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Mark a ComfyUI job request queued as metadata only; no ComfyUI call occurs."""

    try:
        job_request = await CommercialOperationService(session).queue_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            queued_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request queue API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request queue failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/fail",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def fail_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Mark a ComfyUI job request failed without external execution."""

    try:
        job_request = await CommercialOperationService(session).fail_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request fail API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/cancel",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def cancel_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Cancel a metadata-only ComfyUI job request."""

    try:
        job_request = await CommercialOperationService(session).cancel_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request cancel API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/archive",
    response_model=CommercialOperationComfyUIJobRequestResponse,
)
async def archive_commercial_operation_comfyui_job_request(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIJobRequestDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIJobRequestResponse:
    """Archive a ComfyUI job request without deleting its audit trail."""

    try:
        job_request = await CommercialOperationService(session).archive_comfyui_job_request(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIJobRequestResponse.from_model(job_request)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI job request archive API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI job request archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-job-requests/{job_request_id}/execution-plans",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    job_request_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Create a metadata-only ComfyUI execution plan from an approved job request."""

    try:
        plan = await CommercialOperationService(session).create_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            job_request_id=job_request_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan create API failed",
            extra={"operation_id": str(operation_id), "job_request_id": str(job_request_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-execution-plans", response_model=CommercialOperationComfyUIExecutionPlanListResponse)
async def list_commercial_operation_comfyui_execution_plans(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / simulated / failed / cancelled / archived"),
    job_request_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanListResponse:
    """List metadata-only ComfyUI execution plans for a commercial operation."""

    try:
        plans = await CommercialOperationService(session).list_comfyui_execution_plans(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            job_request_id=job_request_id,
            limit=limit,
        )
        return CommercialOperationComfyUIExecutionPlanListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIExecutionPlanResponse.from_model(item) for item in plans],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI execution plan list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI execution plan list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def update_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Patch a metadata-only ComfyUI execution plan before simulation."""

    try:
        plan = await CommercialOperationService(session).update_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan update API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/ready",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def ready_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Mark a metadata-only ComfyUI execution plan ready for review."""

    try:
        plan = await CommercialOperationService(session).mark_comfyui_execution_plan_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan ready API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/approve",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def approve_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Approve a metadata-only ComfyUI execution plan without submitting it."""

    try:
        plan = await CommercialOperationService(session).approve_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan approve API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/reject",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def reject_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Reject a metadata-only ComfyUI execution plan without submitting it."""

    try:
        plan = await CommercialOperationService(session).reject_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan reject API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/simulate",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def simulate_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Mark a ComfyUI execution plan simulated as metadata only; no ComfyUI call occurs."""

    try:
        plan = await CommercialOperationService(session).simulate_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            simulated_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan simulate API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan simulate failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/fail",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def fail_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Mark a ComfyUI execution plan failed without external execution."""

    try:
        plan = await CommercialOperationService(session).fail_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan fail API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/cancel",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def cancel_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Cancel a metadata-only ComfyUI execution plan."""

    try:
        plan = await CommercialOperationService(session).cancel_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan cancel API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/archive",
    response_model=CommercialOperationComfyUIExecutionPlanResponse,
)
async def archive_commercial_operation_comfyui_execution_plan(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIExecutionPlanDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIExecutionPlanResponse:
    """Archive a ComfyUI execution plan without deleting its audit trail."""

    try:
        plan = await CommercialOperationService(session).archive_comfyui_execution_plan(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIExecutionPlanResponse.from_model(plan)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI execution plan archive API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI execution plan archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-execution-plans/{execution_plan_id}/connection-probes",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    execution_plan_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Create a metadata-only ComfyUI connection probe from an execution plan."""

    try:
        probe = await CommercialOperationService(session).create_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            execution_plan_id=execution_plan_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe create API failed",
            extra={"operation_id": str(operation_id), "execution_plan_id": str(execution_plan_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-connection-probes", response_model=CommercialOperationComfyUIConnectionProbeListResponse)
async def list_commercial_operation_comfyui_connection_probes(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / probed / failed / cancelled / archived"),
    execution_plan_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeListResponse:
    """List metadata-only ComfyUI connection probes for a commercial operation."""

    try:
        probes = await CommercialOperationService(session).list_comfyui_connection_probes(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            execution_plan_id=execution_plan_id,
            limit=limit,
        )
        return CommercialOperationComfyUIConnectionProbeListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIConnectionProbeResponse.from_model(item) for item in probes],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI connection probe list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI connection probe list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def update_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Patch a metadata-only ComfyUI connection probe before probe recording."""

    try:
        probe = await CommercialOperationService(session).update_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe update API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/ready",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def ready_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Mark a metadata-only ComfyUI connection probe ready for review."""

    try:
        probe = await CommercialOperationService(session).mark_comfyui_connection_probe_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe ready API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/approve",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def approve_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Approve a metadata-only ComfyUI connection probe without calling ComfyUI."""

    try:
        probe = await CommercialOperationService(session).approve_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe approve API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/reject",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def reject_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Reject a metadata-only ComfyUI connection probe without calling ComfyUI."""

    try:
        probe = await CommercialOperationService(session).reject_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe reject API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/probe",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def probe_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Record a metadata-only ComfyUI connection probe; no HTTP call occurs."""

    try:
        probe = await CommercialOperationService(session).probe_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            probed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe record API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe record failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/fail",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def fail_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Mark a ComfyUI connection probe failed without external execution."""

    try:
        probe = await CommercialOperationService(session).fail_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe fail API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/cancel",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def cancel_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Cancel a metadata-only ComfyUI connection probe."""

    try:
        probe = await CommercialOperationService(session).cancel_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe cancel API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/archive",
    response_model=CommercialOperationComfyUIConnectionProbeResponse,
)
async def archive_commercial_operation_comfyui_connection_probe(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIConnectionProbeDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIConnectionProbeResponse:
    """Archive a ComfyUI connection probe without deleting its audit trail."""

    try:
        probe = await CommercialOperationService(session).archive_comfyui_connection_probe(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIConnectionProbeResponse.from_model(probe)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI connection probe archive API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI connection probe archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-connection-probes/{connection_probe_id}/adapter-dispatches",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    connection_probe_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Create a metadata-only ComfyUI adapter dispatch from a probed connection probe."""

    try:
        dispatch = await CommercialOperationService(session).create_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            connection_probe_id=connection_probe_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch create API failed",
            extra={"operation_id": str(operation_id), "connection_probe_id": str(connection_probe_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-adapter-dispatches", response_model=CommercialOperationComfyUIAdapterDispatchListResponse)
async def list_commercial_operation_comfyui_adapter_dispatches(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / dispatched / failed / cancelled / archived"),
    connection_probe_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchListResponse:
    """List metadata-only ComfyUI adapter dispatches for a commercial operation."""

    try:
        dispatches = await CommercialOperationService(session).list_comfyui_adapter_dispatches(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            connection_probe_id=connection_probe_id,
            limit=limit,
        )
        return CommercialOperationComfyUIAdapterDispatchListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIAdapterDispatchResponse.from_model(item) for item in dispatches],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI adapter dispatch list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI adapter dispatch list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def update_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Patch a metadata-only ComfyUI adapter dispatch before dispatch recording."""

    try:
        dispatch = await CommercialOperationService(session).update_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch update API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/ready",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def ready_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Mark a metadata-only ComfyUI adapter dispatch ready for review."""

    try:
        dispatch = await CommercialOperationService(session).mark_comfyui_adapter_dispatch_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch ready API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/approve",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def approve_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Approve a metadata-only ComfyUI adapter dispatch without calling ComfyUI."""

    try:
        dispatch = await CommercialOperationService(session).approve_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch approve API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/reject",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def reject_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Reject a metadata-only ComfyUI adapter dispatch without calling ComfyUI."""

    try:
        dispatch = await CommercialOperationService(session).reject_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch reject API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/dispatch",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def dispatch_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Record a metadata-only ComfyUI adapter dispatch; no adapter call occurs."""

    try:
        dispatch = await CommercialOperationService(session).dispatch_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            dispatched_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch record API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch record failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/fail",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def fail_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Mark a ComfyUI adapter dispatch failed without external execution."""

    try:
        dispatch = await CommercialOperationService(session).fail_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch fail API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/cancel",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def cancel_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Cancel a metadata-only ComfyUI adapter dispatch."""

    try:
        dispatch = await CommercialOperationService(session).cancel_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch cancel API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/archive",
    response_model=CommercialOperationComfyUIAdapterDispatchResponse,
)
async def archive_commercial_operation_comfyui_adapter_dispatch(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIAdapterDispatchDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIAdapterDispatchResponse:
    """Archive a ComfyUI adapter dispatch without deleting its audit trail."""

    try:
        dispatch = await CommercialOperationService(session).archive_comfyui_adapter_dispatch(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIAdapterDispatchResponse.from_model(dispatch)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI adapter dispatch archive API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI adapter dispatch archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-adapter-dispatches/{adapter_dispatch_id}/runtime-gates",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    adapter_dispatch_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Create a metadata-only ComfyUI runtime gate from a recorded adapter dispatch."""

    try:
        gate = await CommercialOperationService(session).create_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            adapter_dispatch_id=adapter_dispatch_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate create API failed",
            extra={"operation_id": str(operation_id), "adapter_dispatch_id": str(adapter_dispatch_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-runtime-gates", response_model=CommercialOperationComfyUIRuntimeGateListResponse)
async def list_commercial_operation_comfyui_runtime_gates(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / armed / disabled / failed / archived"),
    adapter_dispatch_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateListResponse:
    """List metadata-only ComfyUI runtime gates for a commercial operation."""

    try:
        gates = await CommercialOperationService(session).list_comfyui_runtime_gates(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            adapter_dispatch_id=adapter_dispatch_id,
            limit=limit,
        )
        return CommercialOperationComfyUIRuntimeGateListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIRuntimeGateResponse.from_model(item) for item in gates],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI runtime gate list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI runtime gate list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def update_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Patch a metadata-only ComfyUI runtime gate before arming."""

    try:
        gate = await CommercialOperationService(session).update_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate update API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/ready",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def ready_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Mark a metadata-only ComfyUI runtime gate ready for review."""

    try:
        gate = await CommercialOperationService(session).mark_comfyui_runtime_gate_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate ready API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/approve",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def approve_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Approve a metadata-only ComfyUI runtime gate without enabling runtime calls."""

    try:
        gate = await CommercialOperationService(session).approve_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate approve API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/reject",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def reject_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Reject a metadata-only ComfyUI runtime gate."""

    try:
        gate = await CommercialOperationService(session).reject_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate reject API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/arm",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def arm_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Arm a metadata-only ComfyUI runtime gate; no adapter runtime call occurs."""

    try:
        gate = await CommercialOperationService(session).arm_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            armed_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate arm API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate arm failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/fail",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def fail_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Mark a ComfyUI runtime gate failed without calling ComfyUI."""

    try:
        gate = await CommercialOperationService(session).fail_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate fail API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/disable",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def disable_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Disable a metadata-only ComfyUI runtime gate."""

    try:
        gate = await CommercialOperationService(session).disable_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate disable API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate disable failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/archive",
    response_model=CommercialOperationComfyUIRuntimeGateResponse,
)
async def archive_commercial_operation_comfyui_runtime_gate(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeGateDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeGateResponse:
    """Archive a ComfyUI runtime gate without deleting its audit trail."""

    try:
        gate = await CommercialOperationService(session).archive_comfyui_runtime_gate(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeGateResponse.from_model(gate)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime gate archive API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime gate archive failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-gates/{runtime_gate_id}/runtime-dry-runs",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
    status_code=201,
)
async def create_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_gate_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Create a metadata-only ComfyUI runtime dry-run from an armed runtime gate."""

    try:
        dry_run = await CommercialOperationService(session).create_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_gate_id=runtime_gate_id,
            planned_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run create API failed",
            extra={"operation_id": str(operation_id), "runtime_gate_id": str(runtime_gate_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run create failed", status_code=500) from exc


@router.get("/{operation_id}/comfyui-runtime-dry-runs", response_model=CommercialOperationComfyUIRuntimeDryRunListResponse)
async def list_commercial_operation_comfyui_runtime_dry_runs(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / validated / failed / cancelled / archived"),
    runtime_gate_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunListResponse:
    """List metadata-only ComfyUI runtime dry-runs for a commercial operation."""

    try:
        dry_runs = await CommercialOperationService(session).list_comfyui_runtime_dry_runs(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            runtime_gate_id=runtime_gate_id,
            limit=limit,
        )
        return CommercialOperationComfyUIRuntimeDryRunListResponse(
            operation_id=operation_id,
            items=[CommercialOperationComfyUIRuntimeDryRunResponse.from_model(item) for item in dry_runs],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Commercial operation ComfyUI runtime dry-run list API failed", extra={"operation_id": str(operation_id)})
        raise AppError("Commercial operation ComfyUI runtime dry-run list failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def update_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Patch a metadata-only ComfyUI runtime dry-run before validation."""

    try:
        dry_run = await CommercialOperationService(session).update_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            patch=request.model_dump(exclude_unset=True),
            updated_by=context.user_id,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run update API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/ready",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def ready_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Mark a metadata-only ComfyUI runtime dry-run ready for review."""

    try:
        dry_run = await CommercialOperationService(session).mark_comfyui_runtime_dry_run_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run ready API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/approve",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def approve_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Approve a metadata-only ComfyUI runtime dry-run without enabling runtime calls."""

    try:
        dry_run = await CommercialOperationService(session).approve_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run approve API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/reject",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def reject_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Reject a metadata-only ComfyUI runtime dry-run."""

    try:
        dry_run = await CommercialOperationService(session).reject_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            rejected_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run reject API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/validate",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def validate_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Validate a metadata-only ComfyUI runtime dry-run; no adapter runtime call occurs."""

    try:
        dry_run = await CommercialOperationService(session).validate_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            validated_by=context.user_id,
            result_summary=request.result_summary,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run validate API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run validate failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/fail",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def fail_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Mark a ComfyUI runtime dry-run failed without calling ComfyUI."""

    try:
        dry_run = await CommercialOperationService(session).fail_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            updated_by=context.user_id,
            failure_reason=request.failure_reason,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run fail API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run fail failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/cancel",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def cancel_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Cancel a metadata-only ComfyUI runtime dry-run."""

    try:
        dry_run = await CommercialOperationService(session).cancel_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run cancel API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run cancel failed", status_code=500) from exc


@router.post(
    "/{operation_id}/comfyui-runtime-dry-runs/{runtime_dry_run_id}/archive",
    response_model=CommercialOperationComfyUIRuntimeDryRunResponse,
)
async def archive_commercial_operation_comfyui_runtime_dry_run(
    operation_id: UUID,
    runtime_dry_run_id: UUID,
    request: CommercialOperationComfyUIRuntimeDryRunDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationComfyUIRuntimeDryRunResponse:
    """Archive a ComfyUI runtime dry-run without deleting its audit trail."""

    try:
        dry_run = await CommercialOperationService(session).archive_comfyui_runtime_dry_run(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            runtime_dry_run_id=runtime_dry_run_id,
            archived_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationComfyUIRuntimeDryRunResponse.from_model(dry_run)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation ComfyUI runtime dry-run archive API failed",
            extra={"operation_id": str(operation_id), "runtime_dry_run_id": str(runtime_dry_run_id)},
        )
        raise AppError("Commercial operation ComfyUI runtime dry-run archive failed", status_code=500) from exc


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


@router.post(
    "/{operation_id}/evidence-snapshots",
    response_model=CommercialOperationEvidenceSnapshotResponse,
    status_code=201,
)
async def create_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    request: CommercialOperationEvidenceSnapshotCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Create a reviewable evidence snapshot from a packaged deliverable."""

    try:
        snapshot = await CommercialOperationService(session).create_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            created_by=context.user_id,
            **request.model_dump(),
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot create API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation evidence snapshot create failed", status_code=500) from exc


@router.get("/{operation_id}/evidence-snapshots", response_model=CommercialOperationEvidenceSnapshotListResponse)
async def list_commercial_operation_evidence_snapshots(
    operation_id: UUID,
    status: str | None = Query(default=None, description="draft / ready_for_review / approved / rejected / archived"),
    deliverable_id: UUID | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotListResponse:
    """List reviewable evidence snapshots for a commercial operation."""

    try:
        snapshots = await CommercialOperationService(session).list_evidence_snapshots(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            status=status,
            deliverable_id=deliverable_id,
            limit=limit,
        )
        return CommercialOperationEvidenceSnapshotListResponse(
            operation_id=operation_id,
            items=[CommercialOperationEvidenceSnapshotResponse.from_model(item) for item in snapshots],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot list API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation evidence snapshot list failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/generate-rag",
    response_model=CommercialOperationEvidenceSnapshotResponse,
    status_code=201,
)
async def generate_commercial_operation_evidence_snapshot_from_rag(
    operation_id: UUID,
    request: CommercialOperationEvidenceSnapshotGenerateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Generate a draft evidence snapshot from existing RAG search results."""

    try:
        service = CommercialOperationService(session)
        operation = await service.require_operation(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
        )
        deliverable = await service.require_deliverable(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=request.deliverable_id,
        )
        if deliverable.deliverable_status != "packaged":
            raise ValueError("Evidence snapshots require a packaged commercial deliverable")

        settings = get_settings()
        search_mode = request.search_mode or settings.default_search_mode
        if search_mode not in {"dense", "keyword", "hybrid"}:
            raise ValueError("search_mode must be dense, keyword, or hybrid")
        dense_top_k = request.dense_top_k or settings.dense_top_k
        keyword_top_k = request.keyword_top_k or settings.keyword_top_k
        final_top_k = request.final_top_k or settings.final_top_k
        query = _rag_generation_query(
            operation_title=operation.title,
            operation_objective=operation.objective,
            deliverable_title=deliverable.title,
            deliverable_summary=deliverable.summary,
            requested_query=request.query,
        )
        pipeline = create_hybrid_search_pipeline(
            settings=settings,
            session=session,
            collection_name=_clean_optional_text(request.knowledge_collection) or operation.knowledge_collection,
        )
        bundle = await pipeline.search(
            query=query,
            search_mode=search_mode,  # type: ignore[arg-type]
            dense_top_k=dense_top_k,
            keyword_top_k=keyword_top_k,
            source_id=_clean_optional_text(request.source_id),
            workspace_id=context.workspace_id,
        )
        reranked = await RerankerClient(settings=settings).rerank(
            query=query,
            chunks=bundle.merged_results,
            top_n=final_top_k,
        )
        retrieved_chunks = [build_retrieved_chunk_from_reranked(result) for result in reranked]
        evidence_items = [_rag_evidence_item(chunk) for chunk in retrieved_chunks]
        source_document_ids = _unique_document_ids(evidence_items)
        coverage_checks = request.coverage_checks or [
            "RAG search completed against the existing knowledge index",
            "operator must review retrieved chunks before approval",
            "no knowledge upload, publishing, account control, or external runtime was executed",
        ]
        if not evidence_items:
            coverage_checks = [
                *coverage_checks,
                "no retrieved chunks; revise the query or attach manual evidence before approval",
            ]
        evidence_summary = _clean_optional_text(request.evidence_summary) or (
            f"Generated from {len(evidence_items)} existing RAG chunk(s) for query: {query}"
            if evidence_items
            else f"RAG search returned no chunks for query: {query}"
        )
        relevance_notes = _clean_optional_text(request.relevance_notes) or (
            "Review the retrieved chunks and approve only if they support the packaged deliverable."
        )
        snapshot = await service.create_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            deliverable_id=request.deliverable_id,
            evidence_type="rag_snapshot",
            title=_clean_optional_text(request.title) or f"RAG evidence draft: {deliverable.title}",
            knowledge_collection=pipeline.vector_store.collection_name,
            query=query,
            evidence_summary=evidence_summary,
            relevance_notes=relevance_notes,
            source_document_ids=source_document_ids,
            source_links=[
                {
                    "title": "RAG search",
                    "target": "/api/v1/rag/search",
                    "collection_name": pipeline.vector_store.collection_name,
                    "query": query,
                    "search_mode": search_mode,
                }
            ],
            evidence_items=evidence_items,
            coverage_checks=coverage_checks,
            snapshot_payload={
                "generation_mode": "rag_search_snapshot",
                "collection_name": pipeline.vector_store.collection_name,
                "query": query,
                "source_id": _clean_optional_text(request.source_id),
                "search_mode": search_mode,
                "dense_top_k": dense_top_k,
                "keyword_top_k": keyword_top_k,
                "final_top_k": final_top_k,
                "result_count": len(evidence_items),
                "dense_candidate_count": len(bundle.dense_results),
                "keyword_candidate_count": len(bundle.keyword_results),
                "merged_candidate_count": len(bundle.merged_results),
                "forbidden_actions": [
                    "no knowledge ingestion",
                    "no automatic approval",
                    "no publishing",
                    "no account control",
                    "no ComfyUI, OpenClaw, or browser worker execution",
                ],
            },
            created_by=context.user_id,
            metadata={
                **request.metadata,
                "source": "commercial_operations_rag_generation",
                "phase": "61N",
            },
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation RAG evidence snapshot generation API failed",
            extra={"operation_id": str(operation_id)},
        )
        raise AppError("Commercial operation RAG evidence snapshot generation failed", status_code=500) from exc


@router.patch(
    "/{operation_id}/evidence-snapshots/{snapshot_id}",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def update_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Patch a draft or rejected commercial evidence snapshot."""

    try:
        snapshot = await CommercialOperationService(session).update_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot update API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot update failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/ready",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def ready_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Mark a commercial evidence snapshot ready for review."""

    try:
        snapshot = await CommercialOperationService(session).mark_evidence_snapshot_ready(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot ready API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot ready failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/approve",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def approve_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Approve a reviewed commercial evidence snapshot."""

    try:
        snapshot = await CommercialOperationService(session).approve_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot approve API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot approve failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/reject",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def reject_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Reject a reviewed commercial evidence snapshot for revision."""

    try:
        snapshot = await CommercialOperationService(session).reject_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot reject API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot reject failed", status_code=500) from exc


@router.post(
    "/{operation_id}/evidence-snapshots/{snapshot_id}/archive",
    response_model=CommercialOperationEvidenceSnapshotResponse,
)
async def archive_commercial_operation_evidence_snapshot(
    operation_id: UUID,
    snapshot_id: UUID,
    request: CommercialOperationEvidenceSnapshotDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> CommercialOperationEvidenceSnapshotResponse:
    """Archive a commercial evidence snapshot while preserving the audit trail."""

    try:
        snapshot = await CommercialOperationService(session).archive_evidence_snapshot(
            workspace_id=context.workspace_id,
            operation_id=operation_id,
            snapshot_id=snapshot_id,
            updated_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return CommercialOperationEvidenceSnapshotResponse.from_model(snapshot)
    except ValueError as exc:
        message = str(exc)
        status_code = 404 if "not found" in message.lower() else 400
        raise AppError(message, status_code=status_code) from exc
    except Exception as exc:
        logger.exception(
            "Commercial operation evidence snapshot archive API failed",
            extra={"operation_id": str(operation_id), "snapshot_id": str(snapshot_id)},
        )
        raise AppError("Commercial operation evidence snapshot archive failed", status_code=500) from exc


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
