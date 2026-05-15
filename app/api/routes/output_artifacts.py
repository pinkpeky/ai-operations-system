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
    OutputArtifactCreateRequest,
    OutputArtifactExportResponse,
    OutputArtifactListResponse,
    OutputArtifactResponse,
    OutputArtifactUpdateRequest,
)
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
            source_type=request.source_type,
            artifact_type=request.artifact_type,
            title=request.title,
            summary=request.summary,
            content=request.content,
            file_path=request.file_path,
            mime_type=request.mime_type,
            metadata=request.metadata,
            created_by=context.user_id,
        )
        return OutputArtifactResponse.from_model(artifact)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Create output artifact API failed")
        raise AppError("Create output artifact failed", status_code=500) from exc


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
