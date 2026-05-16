"""Workflow template governance and internal marketplace API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.workflow_template import WorkflowTemplateResponse
from app.schemas.workflow_template_governance import (
    WorkflowTemplateAuditLogListResponse,
    WorkflowTemplateAuditLogResponse,
    WorkflowTemplateCompatibilityMatrixListResponse,
    WorkflowTemplateCompatibilityMatrixResponse,
    WorkflowTemplateLifecycleRequest,
    WorkflowTemplateMarketplaceItem,
    WorkflowTemplateMarketplaceResponse,
    WorkflowTemplateReviewActionRequest,
    WorkflowTemplateReviewCreateRequest,
    WorkflowTemplateReviewListResponse,
    WorkflowTemplateReviewResponse,
)
from app.workflow.template_governance import WorkflowTemplateGovernanceService


reviews_router = APIRouter(prefix="/workflow-template-reviews", tags=["workflow-template-governance"])
templates_router = APIRouter(prefix="/workflow-templates", tags=["workflow-template-governance"])
audit_router = APIRouter(prefix="/workflow-template-audit-logs", tags=["workflow-template-governance"])
marketplace_router = APIRouter(prefix="/workflow-template-marketplace", tags=["workflow-template-governance"])
matrix_router = APIRouter(prefix="/workflow-template-compatibility-matrix", tags=["workflow-template-governance"])


@reviews_router.get("", response_model=WorkflowTemplateReviewListResponse)
async def list_workflow_template_reviews(
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateReviewListResponse:
    reviews = await WorkflowTemplateGovernanceService(session).list_review_queue(
        workspace_id=context.workspace_id,
        status=status,
        limit=limit,
    )
    return WorkflowTemplateReviewListResponse(items=[WorkflowTemplateReviewResponse.from_model(item) for item in reviews])


@reviews_router.post("", response_model=WorkflowTemplateReviewResponse, status_code=201)
async def submit_workflow_template_review(
    request: WorkflowTemplateReviewCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateReviewResponse:
    try:
        review = await WorkflowTemplateGovernanceService(session).submit_for_review(
            workspace_id=context.workspace_id,
            template_id=request.template_id,
            template_version_id=request.template_version_id,
            reviewer_id=request.reviewer_id,
            review_notes=request.review_notes,
            risk_assessment=request.risk_assessment,
            actor_id=context.user_id,
        )
        return WorkflowTemplateReviewResponse.from_model(review)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@reviews_router.post("/{review_id}/approve", response_model=WorkflowTemplateReviewResponse)
async def approve_workflow_template_review(
    review_id: UUID,
    request: WorkflowTemplateReviewActionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateReviewResponse:
    try:
        review = await WorkflowTemplateGovernanceService(session).approve_review(
            workspace_id=context.workspace_id,
            review_id=review_id,
            actor_id=context.user_id,
            review_notes=request.review_notes,
            metadata=request.metadata,
        )
        return WorkflowTemplateReviewResponse.from_model(review)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@reviews_router.post("/{review_id}/reject", response_model=WorkflowTemplateReviewResponse)
async def reject_workflow_template_review(
    review_id: UUID,
    request: WorkflowTemplateReviewActionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateReviewResponse:
    try:
        review = await WorkflowTemplateGovernanceService(session).reject_review(
            workspace_id=context.workspace_id,
            review_id=review_id,
            actor_id=context.user_id,
            review_notes=request.review_notes,
            metadata=request.metadata,
        )
        return WorkflowTemplateReviewResponse.from_model(review)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@reviews_router.post("/{review_id}/request-changes", response_model=WorkflowTemplateReviewResponse)
async def request_workflow_template_review_changes(
    review_id: UUID,
    request: WorkflowTemplateReviewActionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateReviewResponse:
    try:
        review = await WorkflowTemplateGovernanceService(session).request_changes(
            workspace_id=context.workspace_id,
            review_id=review_id,
            actor_id=context.user_id,
            review_notes=request.review_notes,
            metadata=request.metadata,
        )
        return WorkflowTemplateReviewResponse.from_model(review)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@templates_router.post("/{template_id}/rollback/{version_id}", response_model=WorkflowTemplateResponse)
async def rollback_workflow_template(
    template_id: UUID,
    version_id: UUID,
    request: WorkflowTemplateLifecycleRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateResponse:
    try:
        template = await WorkflowTemplateGovernanceService(session).rollback_template_version(
            workspace_id=context.workspace_id,
            template_id=template_id,
            version_id=version_id,
            actor_id=context.user_id,
            reason=request.reason,
        )
        return WorkflowTemplateResponse.from_model(template)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@templates_router.post("/{template_id}/deprecate", response_model=WorkflowTemplateResponse)
async def deprecate_workflow_template(
    template_id: UUID,
    request: WorkflowTemplateLifecycleRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateResponse:
    try:
        template = await WorkflowTemplateGovernanceService(session).deprecate_template(
            workspace_id=context.workspace_id,
            template_id=template_id,
            actor_id=context.user_id,
            reason=request.reason,
        )
        return WorkflowTemplateResponse.from_model(template)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@templates_router.post("/{template_id}/archive", response_model=WorkflowTemplateResponse)
async def archive_workflow_template(
    template_id: UUID,
    request: WorkflowTemplateLifecycleRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateResponse:
    try:
        template = await WorkflowTemplateGovernanceService(session).archive_template(
            workspace_id=context.workspace_id,
            template_id=template_id,
            actor_id=context.user_id,
            reason=request.reason,
        )
        return WorkflowTemplateResponse.from_model(template)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@audit_router.get("", response_model=WorkflowTemplateAuditLogListResponse)
async def list_workflow_template_audit_logs(
    template_id: UUID | None = Query(default=None),
    action: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateAuditLogListResponse:
    logs = await WorkflowTemplateGovernanceService(session).list_governance_events(
        workspace_id=context.workspace_id,
        template_id=template_id,
        action=action,
        limit=limit,
    )
    return WorkflowTemplateAuditLogListResponse(items=[WorkflowTemplateAuditLogResponse.from_model(item) for item in logs])


@marketplace_router.get("", response_model=WorkflowTemplateMarketplaceResponse)
async def list_workflow_template_marketplace(
    featured: bool | None = Query(default=None),
    verified: bool | None = Query(default=None),
    recommended: bool | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateMarketplaceResponse:
    items = await WorkflowTemplateGovernanceService(session).list_marketplace(
        workspace_id=context.workspace_id,
        featured=featured,
        verified=verified,
        recommended=recommended,
        limit=limit,
    )
    return WorkflowTemplateMarketplaceResponse(
        items=[
            WorkflowTemplateMarketplaceItem(
                template=WorkflowTemplateResponse.from_model(item["template"]),
                badges=item["badges"],
                metrics=item["metrics"],
                governance_status=item["governance_status"],
                latest_review_status=item["latest_review_status"],
            )
            for item in items
        ]
    )


@matrix_router.get("", response_model=WorkflowTemplateCompatibilityMatrixListResponse)
async def list_workflow_template_compatibility_matrix(
    template_version_id: UUID | None = Query(default=None),
    runtime_capability: str | None = Query(default=None),
    limit: int = Query(default=500, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateCompatibilityMatrixListResponse:
    rows = await WorkflowTemplateGovernanceService(session).list_compatibility_matrix(
        workspace_id=context.workspace_id,
        template_version_id=template_version_id,
        runtime_capability=runtime_capability,
        limit=limit,
    )
    return WorkflowTemplateCompatibilityMatrixListResponse(
        items=[WorkflowTemplateCompatibilityMatrixResponse.from_model(item) for item in rows]
    )
