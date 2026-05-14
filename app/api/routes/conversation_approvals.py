"""Conversation approval API routes."""

from __future__ import annotations

import logging
from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation.services import ConversationApprovalService, ConversationService
from app.core.errors import AppError
from app.core.workspace_context import WorkspaceContext, get_workspace_context
from app.db.postgres import get_session
from app.schemas.conversation import (
    ConversationApprovalDecisionRequest,
    ConversationApprovalExecuteRequest,
    ConversationApprovalResponse,
    ConversationEventResponse,
    ConversationMessageResponse,
    ConversationRunResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/conversation-approvals", tags=["conversation-approvals"])


@router.get("/{approval_id}", response_model=ConversationApprovalResponse)
async def get_conversation_approval(
    approval_id: UUID,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationApprovalResponse:
    """Get one conversation approval."""

    approval = await ConversationApprovalService(session).get_approval(
        workspace_id=context.workspace_id,
        approval_id=approval_id,
    )
    if approval is None:
        raise AppError("Conversation approval not found", status_code=404)
    return ConversationApprovalResponse.from_model(approval)


@router.post("/{approval_id}/approve", response_model=ConversationApprovalResponse)
async def approve_conversation_approval(
    approval_id: UUID,
    request: ConversationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationApprovalResponse:
    """Approve a pending conversation action."""

    try:
        approval = await ConversationApprovalService(session).approve(
            workspace_id=context.workspace_id,
            approval_id=approval_id,
            approved_by=context.user_id,
            reviewer_notes=request.reviewer_notes,
        )
        return ConversationApprovalResponse.from_model(approval)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation approval approve API failed", extra={"approval_id": str(approval_id)})
        raise AppError("Conversation approval approve failed", status_code=500) from exc


@router.post("/{approval_id}/reject", response_model=ConversationApprovalResponse)
async def reject_conversation_approval(
    approval_id: UUID,
    request: ConversationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationApprovalResponse:
    """Reject a pending conversation action."""

    try:
        approval = await ConversationApprovalService(session).reject(
            workspace_id=context.workspace_id,
            approval_id=approval_id,
            reviewer_notes=request.reviewer_notes,
        )
        return ConversationApprovalResponse.from_model(approval)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation approval reject API failed", extra={"approval_id": str(approval_id)})
        raise AppError("Conversation approval reject failed", status_code=500) from exc


@router.post("/{approval_id}/cancel", response_model=ConversationApprovalResponse)
async def cancel_conversation_approval(
    approval_id: UUID,
    request: ConversationApprovalDecisionRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationApprovalResponse:
    """Cancel a pending or approved conversation action."""

    try:
        approval = await ConversationApprovalService(session).cancel(
            workspace_id=context.workspace_id,
            approval_id=approval_id,
            reviewer_notes=request.reviewer_notes,
        )
        return ConversationApprovalResponse.from_model(approval)
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation approval cancel API failed", extra={"approval_id": str(approval_id)})
        raise AppError("Conversation approval cancel failed", status_code=500) from exc


@router.post("/{approval_id}/execute", response_model=ConversationRunResponse)
async def execute_conversation_approval(
    approval_id: UUID,
    request: ConversationApprovalExecuteRequest,
    session: AsyncSession = Depends(get_session),
    context: WorkspaceContext = Depends(get_workspace_context),
) -> ConversationRunResponse:
    """Execute an approved conversation action exactly once."""

    try:
        approval = await ConversationApprovalService(session).require_approval(
            workspace_id=context.workspace_id,
            approval_id=approval_id,
        )
        run_input = {
            "input": {**request.input, "approval_id": str(approval_id)},
            "mode": "execute_after_approval",
        }
        result = await ConversationService(session).run_conversation_turn(
            workspace_id=context.workspace_id,
            user_id=context.user_id,
            thread_id=approval.thread_id,
            run_input=run_input,
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
        )
    except ValueError as exc:
        raise AppError(str(exc), status_code=400) from exc
    except Exception as exc:
        logger.exception("Conversation approval execute API failed", extra={"approval_id": str(approval_id)})
        raise AppError("Conversation approval execute failed", status_code=500) from exc
