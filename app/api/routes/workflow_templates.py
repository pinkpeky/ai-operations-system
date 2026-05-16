"""Workflow Template Registry API routes."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.workflow_template import (
    WorkflowTemplateCompatibilityResponse,
    WorkflowTemplateCreateRequest,
    WorkflowTemplateExportResponse,
    WorkflowTemplateImportRequest,
    WorkflowTemplateImportResponse,
    WorkflowTemplateListResponse,
    WorkflowTemplateResponse,
    WorkflowTemplateRunListResponse,
    WorkflowTemplateRunRequest,
    WorkflowTemplateRunResponse,
    WorkflowTemplateUpdateRequest,
    WorkflowTemplateVersionCreateRequest,
    WorkflowTemplateVersionResponse,
)
from app.workflow.template_registry import WorkflowTemplateRegistryService
from app.workflow.template_governance import WorkflowTemplateGovernanceService


router = APIRouter(prefix="/workflow-templates", tags=["workflow-templates"])
runs_router = APIRouter(prefix="/workflow-template-runs", tags=["workflow-template-runs"])


@router.get("", response_model=WorkflowTemplateListResponse)
async def list_workflow_templates(
    status: str | None = Query(default=None),
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateListResponse:
    templates = await WorkflowTemplateRegistryService(session).list_templates(
        workspace_id=context.workspace_id,
        status=status,
        category=category,
        limit=limit,
    )
    return WorkflowTemplateListResponse(items=[WorkflowTemplateResponse.from_model(item) for item in templates])


@router.post("", response_model=WorkflowTemplateResponse, status_code=201)
async def create_workflow_template(
    request: WorkflowTemplateCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateResponse:
    try:
        template = await WorkflowTemplateRegistryService(session).create_template(
            workspace_id=context.workspace_id,
            template_key=request.template_key,
            name=request.name,
            description=request.description,
            category=request.category,
            status=request.status,
            risk_level=request.risk_level,
            tags=request.tags,
            metadata=request.metadata,
            version=request.version,
            graph_definition=request.graph_definition,
            entry_node=request.entry_node,
            input_schema=request.input_schema,
            output_schema=request.output_schema,
            changelog=request.changelog,
            created_by=context.user_id,
        )
        return WorkflowTemplateResponse.from_model(template)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/{template_id}", response_model=WorkflowTemplateResponse)
async def get_workflow_template(
    template_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateResponse:
    template = await WorkflowTemplateRegistryService(session).get_template(
        workspace_id=context.workspace_id,
        template_id=template_id,
    )
    if template is None:
        raise AppError("Workflow template not found", status_code=404)
    return WorkflowTemplateResponse.from_model(template)


@router.patch("/{template_id}", response_model=WorkflowTemplateResponse)
async def update_workflow_template(
    template_id: UUID,
    request: WorkflowTemplateUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateResponse:
    try:
        service = WorkflowTemplateRegistryService(session)
        template = await service.require_template(workspace_id=context.workspace_id, template_id=template_id)
        patch = request.model_dump(exclude_unset=True)
        for field in ("name", "description", "category", "status", "risk_level", "tags"):
            if field in patch:
                setattr(template, field, patch[field])
        if "metadata" in patch:
            template.template_metadata = patch["metadata"] or {}
        await session.commit()
        template = await service.require_template(workspace_id=context.workspace_id, template_id=template_id)
        return WorkflowTemplateResponse.from_model(template)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{template_id}/versions", response_model=WorkflowTemplateVersionResponse, status_code=201)
async def create_workflow_template_version(
    template_id: UUID,
    request: WorkflowTemplateVersionCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateVersionResponse:
    try:
        version = await WorkflowTemplateRegistryService(session).create_version(
            workspace_id=context.workspace_id,
            template_id=template_id,
            version=request.version,
            graph_definition=request.graph_definition,
            entry_node=request.entry_node,
            input_schema=request.input_schema,
            output_schema=request.output_schema,
            changelog=request.changelog,
            created_by=context.user_id,
        )
        return WorkflowTemplateVersionResponse.from_model(version)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/{template_id}/versions/{version_id}", response_model=WorkflowTemplateVersionResponse)
async def get_workflow_template_version(
    template_id: UUID,
    version_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateVersionResponse:
    try:
        version = await WorkflowTemplateRegistryService(session).require_template_version(
            workspace_id=context.workspace_id,
            template_id=template_id,
            version_id=version_id,
        )
        return WorkflowTemplateVersionResponse.from_model(version)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/{template_id}/activate-version/{version_id}", response_model=WorkflowTemplateResponse)
async def activate_workflow_template_version(
    template_id: UUID,
    version_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateResponse:
    try:
        template = await WorkflowTemplateGovernanceService(session).activate_template_version(
            workspace_id=context.workspace_id,
            template_id=template_id,
            version_id=version_id,
            actor_id=context.user_id,
            reason="Activated through workflow template API",
        )
        return WorkflowTemplateResponse.from_model(template)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/{template_id}/validate", response_model=WorkflowTemplateCompatibilityResponse)
async def validate_workflow_template(
    template_id: UUID,
    version_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateCompatibilityResponse:
    try:
        version = await WorkflowTemplateRegistryService(session).validate_template(
            workspace_id=context.workspace_id,
            template_id=template_id,
            version_id=version_id,
        )
        return WorkflowTemplateCompatibilityResponse(**(version.compatibility or {}))
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/{template_id}/run", response_model=WorkflowTemplateRunResponse, status_code=201)
async def run_workflow_template(
    template_id: UUID,
    request: WorkflowTemplateRunRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateRunResponse:
    try:
        result = await WorkflowTemplateRegistryService(session).run_template(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            template_id=template_id,
            version_id=request.version_id,
            input_payload=request.input,
            source_type=request.source_type,
            source_id=request.source_id,
            mode=request.mode,
            execution_mode=request.execution_mode,
            metadata=request.metadata,
        )
        return WorkflowTemplateRunResponse.from_model(result.run)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/import", response_model=WorkflowTemplateImportResponse)
async def import_workflow_template(
    request: WorkflowTemplateImportRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateImportResponse:
    try:
        result = await WorkflowTemplateRegistryService(session).import_template(
            workspace_id=context.workspace_id,
            payload=request.template,
            dry_run=request.dry_run,
            conflict_strategy=request.conflict_strategy,
            created_by=context.user_id,
        )
        return WorkflowTemplateImportResponse(
            dry_run=result["dry_run"],
            valid=result["valid"],
            action=result["action"],
            errors=result.get("errors") or [],
            warnings=result.get("warnings") or [],
            template=WorkflowTemplateResponse.from_model(result["template"]) if result.get("template") else None,
            version=WorkflowTemplateVersionResponse.from_model(result["version"]) if result.get("version") else None,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/{template_id}/export", response_model=WorkflowTemplateExportResponse)
async def export_workflow_template(
    template_id: UUID,
    version_id: UUID | None = Query(default=None),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateExportResponse:
    try:
        payload = await WorkflowTemplateRegistryService(session).export_template(
            workspace_id=context.workspace_id,
            template_id=template_id,
            version_id=version_id,
        )
        return WorkflowTemplateExportResponse(**payload)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@runs_router.get("", response_model=WorkflowTemplateRunListResponse)
async def list_workflow_template_runs(
    template_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateRunListResponse:
    runs = await WorkflowTemplateRegistryService(session).list_template_runs(
        workspace_id=context.workspace_id,
        template_id=template_id,
        status=status,
        limit=limit,
    )
    return WorkflowTemplateRunListResponse(items=[WorkflowTemplateRunResponse.from_model(item) for item in runs])


@runs_router.get("/{run_id}", response_model=WorkflowTemplateRunResponse)
async def get_workflow_template_run(
    run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> WorkflowTemplateRunResponse:
    run = await WorkflowTemplateRegistryService(session).get_template_run(
        workspace_id=context.workspace_id,
        run_id=run_id,
    )
    if run is None:
        raise AppError("Workflow template run not found", status_code=404)
    return WorkflowTemplateRunResponse.from_model(run)
