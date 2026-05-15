"""Conversation Playbook API routes."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation.services import ConversationPlaybookService, ConversationService
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.conversation_playbook import (
    ConversationPlaybookCreateRequest,
    ConversationPlaybookListResponse,
    ConversationPlaybookResponse,
    ConversationPlaybookRunListResponse,
    ConversationPlaybookRunRequest,
    ConversationPlaybookRunResponse,
    ConversationPlaybookUpdateRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation-playbooks", tags=["conversation-playbooks"])
runs_router = APIRouter(prefix="/conversation-playbook-runs", tags=["conversation-playbook-runs"])


@router.get("", response_model=ConversationPlaybookListResponse)
async def list_conversation_playbooks(
    status: str | None = Query(default=None, description="active / disabled / archived"),
    category: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookListResponse:
    """List playbooks in the current workspace."""

    try:
        playbooks = await ConversationPlaybookService(session).list_playbooks(
            workspace_id=context.workspace_id,
            status=status,
            category=category,
            limit=limit,
        )
        return ConversationPlaybookListResponse(items=[ConversationPlaybookResponse.from_model(item) for item in playbooks])
    except Exception as exc:
        logger.exception("Conversation playbook list API failed")
        raise AppError("Conversation playbook list failed", status_code=500) from exc


@router.get("/{playbook_id}", response_model=ConversationPlaybookResponse)
async def get_conversation_playbook(
    playbook_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookResponse:
    """Get one playbook."""

    playbook = await ConversationPlaybookService(session).get_playbook(workspace_id=context.workspace_id, playbook_id=playbook_id)
    if playbook is None:
        raise AppError("Conversation playbook not found", status_code=404)
    return ConversationPlaybookResponse.from_model(playbook)


@router.post("", response_model=ConversationPlaybookResponse, status_code=201)
async def create_conversation_playbook(
    request: ConversationPlaybookCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookResponse:
    """Create a custom playbook."""

    try:
        playbook = await ConversationPlaybookService(session).create_playbook(
            workspace_id=context.workspace_id,
            name=request.name,
            description=request.description,
            category=request.category,
            risk_level=request.risk_level,
            steps=request.steps,
            default_inputs=request.default_inputs,
            metadata=request.metadata,
            status=request.status,
        )
        return ConversationPlaybookResponse.from_model(playbook)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation playbook create API failed")
        raise AppError("Conversation playbook create failed", status_code=500) from exc


@router.patch("/{playbook_id}", response_model=ConversationPlaybookResponse)
async def update_conversation_playbook(
    playbook_id: UUID,
    request: ConversationPlaybookUpdateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookResponse:
    """Patch a playbook."""

    try:
        playbook = await ConversationPlaybookService(session).update_playbook(
            workspace_id=context.workspace_id,
            playbook_id=playbook_id,
            patch=request.model_dump(exclude_unset=True),
        )
        return ConversationPlaybookResponse.from_model(playbook)
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Conversation playbook update API failed", extra={"playbook_id": str(playbook_id)})
        raise AppError("Conversation playbook update failed", status_code=500) from exc


@router.post("/{playbook_id}/run", response_model=ConversationPlaybookRunResponse)
async def run_conversation_playbook(
    playbook_id: UUID,
    request: ConversationPlaybookRunRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookRunResponse:
    """Run a playbook directly."""

    try:
        playbook_service = ConversationPlaybookService(session)
        conversation_service = ConversationService(session)
        await playbook_service.ensure_builtin_playbooks(workspace_id=context.workspace_id)
        playbook = await playbook_service.require_playbook(workspace_id=context.workspace_id, playbook_id=playbook_id)
        if request.thread_id is None:
            thread = await conversation_service.create_thread(
                workspace_id=context.workspace_id,
                user_id=context.user_id,
                title=f"Playbook: {playbook.name}",
                metadata={"source": "conversation_playbook_api", "playbook_name": playbook.name},
            )
        else:
            thread = await conversation_service.get_thread(workspace_id=context.workspace_id, thread_id=request.thread_id)
            if thread is None:
                raise AppError("Conversation thread not found", status_code=404)
        result = await playbook_service.run_playbook(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            thread=thread,
            playbook=playbook,
            input_payload=request.input,
            mode=request.mode,
            message_id=None,
            source_message=str(request.input.get("message") or request.input.get("topic") or playbook.name),
        )
        return ConversationPlaybookRunResponse.from_model(result.run)
    except AppError:
        raise
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation playbook run API failed", extra={"playbook_id": str(playbook_id)})
        raise AppError("Conversation playbook run failed", status_code=500) from exc


@runs_router.get("", response_model=ConversationPlaybookRunListResponse)
async def list_conversation_playbook_runs(
    thread_id: UUID | None = Query(default=None),
    status: str | None = Query(default=None),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookRunListResponse:
    """List playbook runs."""

    runs = await ConversationPlaybookService(session).list_playbook_runs(
        workspace_id=context.workspace_id,
        thread_id=thread_id,
        status=status,
        limit=limit,
    )
    return ConversationPlaybookRunListResponse(items=[ConversationPlaybookRunResponse.from_model(item) for item in runs])


@runs_router.get("/{run_id}", response_model=ConversationPlaybookRunResponse)
async def get_conversation_playbook_run(
    run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookRunResponse:
    """Get one playbook run."""

    run = await ConversationPlaybookService(session).get_playbook_run(workspace_id=context.workspace_id, run_id=run_id)
    if run is None:
        raise AppError("Conversation playbook run not found", status_code=404)
    return ConversationPlaybookRunResponse.from_model(run)


@runs_router.post("/{run_id}/cancel", response_model=ConversationPlaybookRunResponse)
async def cancel_conversation_playbook_run(
    run_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationPlaybookRunResponse:
    """Cancel a pending/running/waiting playbook run."""

    try:
        run = await ConversationPlaybookService(session).cancel_playbook_run(workspace_id=context.workspace_id, run_id=run_id)
        return ConversationPlaybookRunResponse.from_model(run)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation playbook cancel API failed", extra={"run_id": str(run_id)})
        raise AppError("Conversation playbook cancel failed", status_code=500) from exc
