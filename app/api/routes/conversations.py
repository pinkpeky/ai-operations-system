"""Conversation Runtime API routes。"""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation.services import ConversationApprovalService, ConversationService
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.models.enums import ConversationRole
from app.schemas.conversation import (
    ConversationEventListResponse,
    ConversationEventResponse,
    ConversationApprovalListResponse,
    ConversationApprovalResponse,
    ConversationMessageCreateRequest,
    ConversationMessageListResponse,
    ConversationMessageResponse,
    ConversationRunRequest,
    ConversationRunResponse,
    ConversationThreadCreateRequest,
    ConversationThreadListResponse,
    ConversationThreadResponse,
)
from app.task_orchestration.service import TaskOrchestratorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversations", tags=["conversations"])


@router.post("", response_model=ConversationThreadResponse, status_code=201)
async def create_conversation(
    request: ConversationThreadCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationThreadResponse:
    """创建 Conversation Runtime thread。"""

    try:
        thread = await ConversationService(session).create_thread(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            title=request.title,
            metadata=request.metadata,
        )
        return ConversationThreadResponse.from_model(thread)
    except Exception as exc:
        logger.exception("Conversation create API failed")
        raise AppError(str(exc) or "Conversation create failed", status_code=500) from exc


@router.get("", response_model=ConversationThreadListResponse)
async def list_conversations(
    status: str | None = Query(default=None, description="active / archived / deleted"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationThreadListResponse:
    """列出当前 workspace 的对话线程。"""

    try:
        threads = await ConversationService(session).list_threads(
            workspace_id=context.workspace_id,
            status=status,
            limit=limit,
        )
        return ConversationThreadListResponse(items=[ConversationThreadResponse.from_model(item) for item in threads])
    except Exception as exc:
        logger.exception("Conversation list API failed")
        raise AppError("Conversation list failed", status_code=500) from exc


@router.get("/{thread_id}", response_model=ConversationThreadResponse)
async def get_conversation(
    thread_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationThreadResponse:
    """获取对话线程详情。"""

    try:
        thread = await ConversationService(session).get_thread(workspace_id=context.workspace_id, thread_id=thread_id)
        if thread is None:
            raise AppError("Conversation thread not found", status_code=404)
        return ConversationThreadResponse.from_model(thread)
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Conversation get API failed", extra={"thread_id": str(thread_id)})
        raise AppError("Conversation get failed", status_code=500) from exc


@router.post("/{thread_id}/messages", response_model=ConversationMessageResponse, status_code=201)
async def append_conversation_message(
    thread_id: UUID,
    request: ConversationMessageCreateRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationMessageResponse:
    """追加对话消息。"""

    try:
        message = await ConversationService(session).append_message(
            workspace_id=context.workspace_id,
            thread_id=thread_id,
            role=request.role,
            content=request.content,
            metadata=request.metadata,
        )
        return ConversationMessageResponse.from_model(message)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation append message API failed", extra={"thread_id": str(thread_id)})
        raise AppError("Conversation append message failed", status_code=500) from exc


@router.get("/{thread_id}/messages", response_model=ConversationMessageListResponse)
async def list_conversation_messages(
    thread_id: UUID,
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationMessageListResponse:
    """列出对话消息。"""

    try:
        messages = await ConversationService(session).list_messages(
            workspace_id=context.workspace_id,
            thread_id=thread_id,
            limit=limit,
        )
        return ConversationMessageListResponse(
            thread_id=thread_id,
            items=[ConversationMessageResponse.from_model(item) for item in messages],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Conversation message list API failed", extra={"thread_id": str(thread_id)})
        raise AppError("Conversation message list failed", status_code=500) from exc


@router.get("/{thread_id}/events", response_model=ConversationEventListResponse)
async def list_conversation_events(
    thread_id: UUID,
    limit: int = Query(default=200, ge=1, le=1000),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationEventListResponse:
    """列出对话事件。

    当前使用普通 polling；WebSocket / SSE 只保留为后续 placeholder。
    """

    try:
        events = await ConversationService(session).list_events(
            workspace_id=context.workspace_id,
            thread_id=thread_id,
            limit=limit,
        )
        return ConversationEventListResponse(
            thread_id=thread_id,
            items=[ConversationEventResponse.from_model(item) for item in events],
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=404) from exc
    except Exception as exc:
        logger.exception("Conversation event list API failed", extra={"thread_id": str(thread_id)})
        raise AppError("Conversation event list failed", status_code=500) from exc


@router.get("/{thread_id}/approvals", response_model=ConversationApprovalListResponse)
async def list_conversation_approvals(
    thread_id: UUID,
    status: str | None = Query(default=None, description="pending / approved / rejected / cancelled / expired / executed"),
    limit: int = Query(default=100, ge=1, le=500),
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationApprovalListResponse:
    """List execution approvals for a conversation thread."""

    try:
        thread = await ConversationService(session).get_thread(workspace_id=context.workspace_id, thread_id=thread_id)
        if thread is None:
            raise AppError("Conversation thread not found", status_code=404)
        approvals = await ConversationApprovalService(session).list_approvals(
            workspace_id=context.workspace_id,
            thread_id=thread_id,
            status=status,
            limit=limit,
        )
        return ConversationApprovalListResponse(
            thread_id=thread_id,
            items=[ConversationApprovalResponse.from_model(item) for item in approvals],
        )
    except AppError:
        raise
    except Exception as exc:
        logger.exception("Conversation approval list API failed", extra={"thread_id": str(thread_id)})
        raise AppError("Conversation approval list failed", status_code=500) from exc


@router.post("/{thread_id}/run", response_model=ConversationRunResponse)
async def run_conversation(
    thread_id: UUID,
    request: ConversationRunRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationRunResponse:
    """执行一轮 rule-based conversation runtime。"""

    try:
        if request.execution_mode in {"background", "scheduled"}:
            if request.execution_mode == "scheduled" and request.scheduled_at is None:
                raise AppError("scheduled_at is required for scheduled execution", status_code=400)
            conversation = ConversationService(session)
            text = str(
                request.input.get("message")
                or request.input.get("topic")
                or request.workflow_template_key
                or request.playbook_name
                or "Background conversation task"
            )
            user_message = await conversation.append_message(
                workspace_id=context.workspace_id,
                thread_id=thread_id,
                role=ConversationRole.USER.value,
                content=text,
                metadata={"execution_mode": request.execution_mode, "source": "task_orchestration"},
            )
            assistant_message = await conversation.append_message(
                workspace_id=context.workspace_id,
                thread_id=thread_id,
                role=ConversationRole.ASSISTANT.value,
                content="Background task queued. Poll /api/v1/task-runs/{task_run_id} for status.",
                metadata={"execution_mode": request.execution_mode, "queued": True},
            )
            run_payload = request.model_dump()
            run_payload.pop("execution_mode", None)
            run_payload.pop("scheduled_at", None)
            task = await TaskOrchestratorService(session).enqueue_task(
                workspace_id=context.workspace_id,
                task_type="playbook" if request.playbook_name or request.workflow_template_key else "conversation",
                source_type="conversation",
                source_id=str(thread_id),
                input_payload={"thread_id": str(thread_id), "run_input": run_payload, **run_payload},
                created_by=context.user_id,
                scheduled_at=request.scheduled_at,
                metadata={
                    "execution_mode": request.execution_mode,
                    "playbook_name": request.playbook_name,
                    "workflow_template_key": request.workflow_template_key,
                },
            )
            await conversation.append_event(
                workspace_id=context.workspace_id,
                thread_id=thread_id,
                event_type="task_queued",
                message="Conversation run queued as background task",
                payload={"task_run_id": str(task.id), "execution_mode": request.execution_mode, "task_status": task.status},
            )
            return ConversationRunResponse(
                thread_id=thread_id,
                user_message_id=user_message.id,
                assistant_message_id=assistant_message.id,
                assistant_message=ConversationMessageResponse.from_model(assistant_message),
                route="task_run",
                route_name="task_run",
                selected_tool=None,
                events=[],
                events_created=1,
                success=True,
                summary="Background task queued",
                result_metadata={
                    "task_run_id": str(task.id),
                    "task_status": task.status,
                    "execution_mode": request.execution_mode,
                    "workflow_run_id": (task.task_metadata or {}).get("workflow_run_id"),
                },
                output={
                    "task_run_id": str(task.id),
                    "task_status": task.status,
                    "workflow_run_id": (task.task_metadata or {}).get("workflow_run_id"),
                },
                task_run_id=task.id,
                task_status=task.status,
                workflow_run_id=UUID(str((task.task_metadata or {}).get("workflow_run_id")))
                if (task.task_metadata or {}).get("workflow_run_id")
                else None,
                execution_mode=request.execution_mode,
            )
        result = await ConversationService(session).run_conversation_turn(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            thread_id=thread_id,
            run_input=request.model_dump(),
        )
        return ConversationRunResponse(
            thread_id=result.thread_id,
            user_message_id=result.user_message_id,
            assistant_message_id=result.assistant_message_id,
            assistant_message=ConversationMessageResponse.from_model(result.assistant_message),
            route=result.route,
            route_name=result.route_name,
            selected_tool=result.selected_tool,
            events=[ConversationEventResponse.from_model(item) for item in result.events],
            events_created=result.events_created,
            success=result.success,
            summary=result.summary,
            result_metadata=result.result_metadata,
            output=result.output,
            approval_required=result.approval_required,
            approval_id=result.approval_id,
            approval_status=result.approval_status,
            risk_level=result.risk_level,
            proposed_action=result.proposed_action,
            playbook_run_id=result.playbook_run_id,
            playbook_name=result.playbook_name,
            playbook_status=result.playbook_status,
            workflow_run_id=result.workflow_run_id,
            workflow_step_id=result.workflow_step_id,
            checkpoint_id=result.checkpoint_id,
            memory_snapshot_id=result.memory_snapshot_id,
            workflow_template_id=result.workflow_template_id,
            workflow_template_version_id=result.workflow_template_version_id,
            workflow_template_run_id=result.workflow_template_run_id,
            workflow_template_key=result.workflow_template_key,
            execution_mode=request.execution_mode,
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation run API failed", extra={"thread_id": str(thread_id)})
        raise AppError("Conversation run failed", status_code=500) from exc
