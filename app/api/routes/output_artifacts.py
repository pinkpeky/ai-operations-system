"""Output Library API routes."""

from __future__ import annotations

import logging
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.output_artifact import (
    ArtifactCleanupPreviewRequest,
    ArtifactCleanupPreviewResponse,
    ArtifactLineageResponse,
    ArtifactRelationshipListResponse,
    ArtifactRelationshipResponse,
    OutputArtifactCreateRequest,
    OutputArtifactActionResponse,
    OutputArtifactExportResponse,
    OutputArtifactExportRequest,
    OutputArtifactListResponse,
    OutputArtifactPackageRequest,
    OutputArtifactResponse,
    OutputArtifactUpdateRequest,
)
from app.services.artifact_export_service import ArtifactExportService
from app.services.artifact_packaging_service import ArtifactPackagingService
from app.services.artifact_retention_service import ArtifactRetentionService
from app.services.output_artifact_service import OutputArtifactService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/output-artifacts", tags=["output-artifacts"])


@router.get("", response_model=OutputArtifactListResponse)
async def list_output_artifacts(
    artifact_type: str | None = Query(default=None),
    source_type: str | None = Query(default=None),
    thread_id: UUID | None = Query(default=None),
    playbook_run_id: UUID | None = Query(default=None),
    task_run_id: UUID | None = Query(default=None),
    artifact_role: str | None = Query(default=None),
    artifact_stage: str | None = Query(default=None),
    source_task_run_id: UUID | None = Query(default=None),
    source_playbook_run_id: UUID | None = Query(default=None),
    source_conversation_id: UUID | None = Query(default=None),
    source_runtime_session_id: UUID | None = Query(default=None),
    workflow_run_id: UUID | None = Query(default=None),
    workflow_step_id: UUID | None = Query(default=None),
    checkpoint_id: UUID | None = Query(default=None),
    memory_snapshot_id: UUID | None = Query(default=None),
    workflow_template_id: UUID | None = Query(default=None),
    workflow_template_version_id: UUID | None = Query(default=None),
    workflow_template_run_id: UUID | None = Query(default=None),
    source_template_review_id: UUID | None = Query(default=None),
    governance_state: str | None = Query(default=None),
    producing_node_key: str | None = Query(default=None),
    replay_source: str | None = Query(default=None),
    trace_id: UUID | None = Query(default=None),
    replay_session_id: UUID | None = Query(default=None),
    diagnostic_reference: str | None = Query(default=None),
    exportable: bool | None = Query(default=None),
    archived: bool | None = Query(default=None),
    retention_policy: str | None = Query(default=None),
    created_from: datetime | None = Query(default=None),
    created_to: datetime | None = Query(default=None),
    include_deleted: bool = Query(default=False),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactListResponse:
    """List output artifacts in the current workspace."""

    artifacts = await OutputArtifactService(session).list_artifacts(
        workspace_id=context.workspace_id,
        artifact_type=artifact_type,
        source_type=source_type,
        thread_id=thread_id,
        playbook_run_id=playbook_run_id,
        task_run_id=task_run_id,
        artifact_role=artifact_role,
        artifact_stage=artifact_stage,
        source_task_run_id=source_task_run_id,
        source_playbook_run_id=source_playbook_run_id,
        source_conversation_id=source_conversation_id,
        source_runtime_session_id=source_runtime_session_id,
        workflow_run_id=workflow_run_id,
        workflow_step_id=workflow_step_id,
        checkpoint_id=checkpoint_id,
        memory_snapshot_id=memory_snapshot_id,
        workflow_template_id=workflow_template_id,
        workflow_template_version_id=workflow_template_version_id,
        workflow_template_run_id=workflow_template_run_id,
        source_template_review_id=source_template_review_id,
        governance_state=governance_state,
        producing_node_key=producing_node_key,
        replay_source=replay_source,
        trace_id=trace_id,
        replay_session_id=replay_session_id,
        diagnostic_reference=diagnostic_reference,
        exportable=exportable,
        archived=archived,
        retention_policy=retention_policy,
        created_from=created_from,
        created_to=created_to,
        include_deleted=include_deleted,
        limit=limit,
    )
    return OutputArtifactListResponse(items=[OutputArtifactResponse.from_model(item) for item in artifacts])


@router.post("", response_model=OutputArtifactResponse, status_code=201)
async def create_output_artifact(
    request: OutputArtifactCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactResponse:
    """Create a manual output artifact."""

    try:
        artifact = await OutputArtifactService(session).create_artifact(
            workspace_id=context.workspace_id,
            thread_id=request.thread_id,
            playbook_run_id=request.playbook_run_id,
            task_run_id=request.task_run_id,
            parent_artifact_id=request.parent_artifact_id,
            root_artifact_id=request.root_artifact_id,
            source_task_run_id=request.source_task_run_id,
            source_playbook_run_id=request.source_playbook_run_id,
            source_conversation_id=request.source_conversation_id,
            source_runtime_session_id=request.source_runtime_session_id,
            workflow_run_id=request.workflow_run_id,
            workflow_step_id=request.workflow_step_id,
            checkpoint_id=request.checkpoint_id,
            memory_snapshot_id=request.memory_snapshot_id,
            workflow_template_id=request.workflow_template_id,
            workflow_template_version_id=request.workflow_template_version_id,
            workflow_template_run_id=request.workflow_template_run_id,
            source_template_review_id=request.source_template_review_id,
            governance_state=request.governance_state,
            producing_node_key=request.producing_node_key,
            replay_source=request.replay_source,
            trace_id=request.trace_id,
            replay_session_id=request.replay_session_id,
            diagnostic_reference=request.diagnostic_reference,
            graph_lineage=request.graph_lineage,
            source_type=request.source_type,
            artifact_type=request.artifact_type,
            artifact_role=request.artifact_role,
            artifact_stage=request.artifact_stage,
            title=request.title,
            summary=request.summary,
            content=request.content,
            file_path=request.file_path,
            mime_type=request.mime_type,
            metadata=request.metadata,
            generated_by=request.generated_by,
            exportable=request.exportable,
            retention_policy=request.retention_policy,
            expires_at=request.expires_at,
            created_by=context.user_id,
        )
        return OutputArtifactResponse.from_model(artifact)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Create output artifact API failed")
        raise AppError("Create output artifact failed", status_code=500) from exc


@router.post("/cleanup/preview", response_model=ArtifactCleanupPreviewResponse)
async def preview_output_artifact_cleanup(
    request: ArtifactCleanupPreviewRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ArtifactCleanupPreviewResponse:
    """Preview retention cleanup. This does not delete physical files."""

    try:
        preview = await ArtifactRetentionService(session).cleanup_preview(
            workspace_id=context.workspace_id,
            retention_policy=request.retention_policy,
            limit=request.limit,
        )
        return ArtifactCleanupPreviewResponse(**preview)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/{artifact_id}", response_model=OutputArtifactResponse)
async def get_output_artifact(
    artifact_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactResponse:
    """Get one output artifact."""

    artifact = await OutputArtifactService(session).get_artifact(
        workspace_id=context.workspace_id,
        artifact_id=artifact_id,
    )
    if artifact is None:
        raise AppError("Output artifact not found", status_code=404)
    return OutputArtifactResponse.from_model(artifact)


@router.patch("/{artifact_id}", response_model=OutputArtifactResponse)
async def update_output_artifact(
    artifact_id: UUID,
    request: OutputArtifactUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactResponse:
    """Patch an output artifact."""

    try:
        artifact = await OutputArtifactService(session).update_artifact(
            workspace_id=context.workspace_id,
            artifact_id=artifact_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return OutputArtifactResponse.from_model(artifact)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.delete("/{artifact_id}", response_model=OutputArtifactResponse)
async def delete_output_artifact(
    artifact_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactResponse:
    """Soft-delete an output artifact."""

    try:
        artifact = await OutputArtifactService(session).delete_artifact(
            workspace_id=context.workspace_id,
            artifact_id=artifact_id,
        )
        return OutputArtifactResponse.from_model(artifact)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/from-message/{message_id}", response_model=OutputArtifactResponse, status_code=201)
async def create_output_artifact_from_message(
    message_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactResponse:
    """Create an output artifact from a conversation message."""

    try:
        artifact = await OutputArtifactService(session).create_from_conversation_message(
            workspace_id=context.workspace_id,
            message_id=message_id,
            created_by=context.user_id,
        )
        return OutputArtifactResponse.from_model(artifact)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.post("/from-playbook-run/{run_id}", response_model=OutputArtifactListResponse, status_code=201)
async def create_output_artifacts_from_playbook_run(
    run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactListResponse:
    """Create output artifacts from a playbook run."""

    try:
        artifacts = await OutputArtifactService(session).create_from_playbook_run(
            workspace_id=context.workspace_id,
            run_id=run_id,
            created_by=context.user_id,
        )
        return OutputArtifactListResponse(items=[OutputArtifactResponse.from_model(item) for item in artifacts])
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/{artifact_id}/export", response_model=OutputArtifactExportResponse)
async def export_output_artifact(
    artifact_id: UUID,
    format: str = Query(default="markdown", pattern="^(markdown|json|txt)$"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactExportResponse:
    """Export an output artifact to markdown/json/txt."""

    try:
        artifact, export_path, content = await OutputArtifactService(session).export_artifact(
            workspace_id=context.workspace_id,
            artifact_id=artifact_id,
            export_format=format,
        )
        return OutputArtifactExportResponse(
            artifact=OutputArtifactResponse.from_model(artifact),
            format=format,
            export_path=str(export_path),
            content=content,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/{artifact_id}/export", response_model=OutputArtifactActionResponse)
async def export_output_artifact_pipeline(
    artifact_id: UUID,
    request: OutputArtifactExportRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactActionResponse:
    """Export one artifact through the Phase 44 artifact export pipeline."""

    try:
        service = ArtifactExportService(session)
        if request.format == "markdown":
            result = await service.export_markdown(workspace_id=context.workspace_id, artifact_id=artifact_id, metadata=request.metadata)
        elif request.format == "html":
            result = await service.export_html(workspace_id=context.workspace_id, artifact_id=artifact_id, metadata=request.metadata)
        elif request.format == "json":
            result = await service.export_json(workspace_id=context.workspace_id, artifact_id=artifact_id, metadata=request.metadata)
        elif request.format == "txt":
            result = await service.export_txt(workspace_id=context.workspace_id, artifact_id=artifact_id, metadata=request.metadata)
        elif request.format == "report_package":
            result = await service.export_report_package(workspace_id=context.workspace_id, artifact_ids=[artifact_id], metadata=request.metadata)
        else:
            result = await service.export_bundle_zip(workspace_id=context.workspace_id, artifact_ids=[artifact_id], metadata=request.metadata)
        return OutputArtifactActionResponse(
            artifact=OutputArtifactResponse.from_model(result["artifact"]),
            generated_artifact=OutputArtifactResponse.from_model(result["generated_artifact"]) if result.get("generated_artifact") else None,
            format=request.format,
            output_path=str(result["output_path"]),
            content=result.get("content"),
            metadata=result.get("metadata") or {},
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.post("/{artifact_id}/package", response_model=OutputArtifactActionResponse)
async def package_output_artifact(
    artifact_id: UUID,
    request: OutputArtifactPackageRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> OutputArtifactActionResponse:
    """Create a ZIP package artifact from an artifact and optionally related lineage."""

    try:
        result = await ArtifactPackagingService(session).package_artifact(
            workspace_id=context.workspace_id,
            artifact_id=artifact_id,
            include_related=request.include_related,
            package_type=request.package_type,
            metadata=request.metadata,
        )
        return OutputArtifactActionResponse(
            artifact=OutputArtifactResponse.from_model(result["artifact"]),
            generated_artifact=OutputArtifactResponse.from_model(result["generated_artifact"]) if result.get("generated_artifact") else None,
            format=request.package_type,
            output_path=str(result["output_path"]),
            metadata=result.get("metadata") or {},
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc


@router.get("/{artifact_id}/relationships", response_model=ArtifactRelationshipListResponse)
async def list_output_artifact_relationships(
    artifact_id: UUID,
    direction: str = Query(default="both", pattern="^(both|parents|children)$"),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ArtifactRelationshipListResponse:
    """List lineage relationships for an artifact."""

    try:
        relationships = await OutputArtifactService(session).list_relationships(
            workspace_id=context.workspace_id,
            artifact_id=artifact_id,
            direction=direction,
        )
        return ArtifactRelationshipListResponse(items=[ArtifactRelationshipResponse.from_model(item) for item in relationships])
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc


@router.get("/{artifact_id}/lineage", response_model=ArtifactLineageResponse)
async def get_output_artifact_lineage(
    artifact_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ArtifactLineageResponse:
    """Return ancestors, descendants, and relationship edges for one artifact."""

    try:
        lineage = await OutputArtifactService(session).lineage_for_artifact(
            workspace_id=context.workspace_id,
            artifact_id=artifact_id,
        )
        return ArtifactLineageResponse(
            artifact=OutputArtifactResponse.from_model(lineage["artifact"]),
            root_artifact_id=lineage["root_artifact_id"],
            ancestors=[OutputArtifactResponse.from_model(item) for item in lineage["ancestors"]],
            descendants=[OutputArtifactResponse.from_model(item) for item in lineage["descendants"]],
            relationships=[ArtifactRelationshipResponse.from_model(item) for item in lineage["relationships"]],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
