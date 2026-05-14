"""Conversation approval service.

The service owns the legal state machine for execution review. It records every
approval state change into conversation_events so polling frontends can show a
clear timeline without WebSocket/SSE.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.conversation.repositories import ConversationRuntimeRepository
from app.conversation.tool_router import ConversationRouteDecision
from app.models.conversation import ConversationApproval
from app.models.enums import ConversationApprovalStatus


class ConversationApprovalService:
    """Workspace-scoped approval lifecycle manager."""

    TERMINAL_STATUSES = {
        ConversationApprovalStatus.REJECTED.value,
        ConversationApprovalStatus.CANCELLED.value,
        ConversationApprovalStatus.EXPIRED.value,
        ConversationApprovalStatus.EXECUTED.value,
    }

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ConversationRuntimeRepository(session)

    async def create_approval(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        message_id: UUID | None,
        decision: ConversationRouteDecision,
        risk_level: str,
        source_message: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationApproval:
        """Create a pending approval and write timeline events."""

        proposed_payload = {
            "decision": decision.to_payload(),
            "tool_input": decision.tool_input,
            "source_message": source_message,
            "approval_context": metadata or {},
        }
        approval = await self.repository.create_approval(
            workspace_id=workspace_id,
            thread_id=thread_id,
            message_id=message_id,
            route_name=decision.route_name,
            selected_tool=decision.selected_tool,
            risk_level=risk_level,
            proposed_action=self._describe_action(decision),
            proposed_payload=proposed_payload,
            metadata=metadata or {},
        )
        payload = self._event_payload(approval)
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="approval_required",
            message=f"Approval required for {decision.route_name}",
            payload=payload,
        )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="approval_created",
            message="Conversation approval created",
            payload=payload,
        )
        return approval

    async def list_approvals(
        self,
        *,
        workspace_id: str,
        thread_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationApproval]:
        """List approvals with workspace isolation."""

        return await self.repository.list_approvals(
            workspace_id=workspace_id,
            thread_id=thread_id,
            status=status,
            limit=limit,
        )

    async def get_approval(self, *, workspace_id: str, approval_id: UUID) -> ConversationApproval | None:
        """Get one approval with workspace isolation."""

        return await self.repository.get_approval(workspace_id=workspace_id, approval_id=approval_id)

    async def require_approval(self, *, workspace_id: str, approval_id: UUID) -> ConversationApproval:
        """Return approval or raise a clear error."""

        approval = await self.get_approval(workspace_id=workspace_id, approval_id=approval_id)
        if approval is None:
            raise ValueError("Conversation approval not found in workspace")
        return approval

    async def approve(
        self,
        *,
        workspace_id: str,
        approval_id: UUID,
        approved_by: str | None,
        reviewer_notes: str | None = None,
        commit: bool = True,
    ) -> ConversationApproval:
        """Approve a pending action."""

        approval = await self.require_approval(workspace_id=workspace_id, approval_id=approval_id)
        self._ensure_status(approval, {ConversationApprovalStatus.PENDING.value}, "Only pending approvals can be approved")
        approval.approval_status = ConversationApprovalStatus.APPROVED.value
        approval.approved_by = approved_by
        approval.approved_at = datetime.now(UTC)
        approval.reviewer_notes = reviewer_notes
        await self._append_state_event(approval, "approval_approved", "Conversation approval approved")
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(approval)
        return approval

    async def reject(
        self,
        *,
        workspace_id: str,
        approval_id: UUID,
        reviewer_notes: str | None = None,
        commit: bool = True,
    ) -> ConversationApproval:
        """Reject a pending action."""

        approval = await self.require_approval(workspace_id=workspace_id, approval_id=approval_id)
        self._ensure_status(approval, {ConversationApprovalStatus.PENDING.value}, "Only pending approvals can be rejected")
        approval.approval_status = ConversationApprovalStatus.REJECTED.value
        approval.rejected_at = datetime.now(UTC)
        approval.reviewer_notes = reviewer_notes
        await self._append_state_event(approval, "approval_rejected", "Conversation approval rejected")
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(approval)
        return approval

    async def cancel(
        self,
        *,
        workspace_id: str,
        approval_id: UUID,
        reviewer_notes: str | None = None,
        commit: bool = True,
    ) -> ConversationApproval:
        """Cancel a pending or approved action before execution."""

        approval = await self.require_approval(workspace_id=workspace_id, approval_id=approval_id)
        self._ensure_status(
            approval,
            {ConversationApprovalStatus.PENDING.value, ConversationApprovalStatus.APPROVED.value},
            "Only pending or approved approvals can be cancelled",
        )
        approval.approval_status = ConversationApprovalStatus.CANCELLED.value
        approval.cancelled_at = datetime.now(UTC)
        approval.reviewer_notes = reviewer_notes
        await self._append_state_event(approval, "approval_cancelled", "Conversation approval cancelled")
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(approval)
        return approval

    async def expire_pending(
        self,
        *,
        workspace_id: str,
        thread_id: UUID | None = None,
        now: datetime | None = None,
        commit: bool = True,
    ) -> list[ConversationApproval]:
        """Expire pending approvals whose expiry time has passed."""

        now = now or datetime.now(UTC)
        approvals = await self.list_approvals(
            workspace_id=workspace_id,
            thread_id=thread_id,
            status=ConversationApprovalStatus.PENDING.value,
            limit=1000,
        )
        expired: list[ConversationApproval] = []
        for approval in approvals:
            if approval.expires_at is not None and approval.expires_at <= now:
                approval.approval_status = ConversationApprovalStatus.EXPIRED.value
                await self._append_state_event(approval, "approval_expired", "Conversation approval expired")
                expired.append(approval)
        await self.session.flush()
        if commit:
            await self.session.commit()
        return expired

    async def mark_executed(
        self,
        *,
        workspace_id: str,
        approval_id: UUID,
        commit: bool = False,
    ) -> ConversationApproval:
        """Mark an approved action as executed."""

        approval = await self.require_approval(workspace_id=workspace_id, approval_id=approval_id)
        self._ensure_status(approval, {ConversationApprovalStatus.APPROVED.value}, "Only approved approvals can be executed")
        approval.approval_status = ConversationApprovalStatus.EXECUTED.value
        await self._append_state_event(approval, "approval_executed", "Conversation approval executed")
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(approval)
        return approval

    def ensure_executable(self, approval: ConversationApproval) -> None:
        """Validate that an approval can run exactly once."""

        if approval.approval_status == ConversationApprovalStatus.EXECUTED.value:
            raise ValueError("Conversation approval has already been executed")
        if approval.approval_status != ConversationApprovalStatus.APPROVED.value:
            raise ValueError(f"Conversation approval must be approved before execution; current={approval.approval_status}")

    def _ensure_status(self, approval: ConversationApproval, allowed: set[str], message: str) -> None:
        if approval.approval_status not in allowed:
            raise ValueError(message)

    async def _append_state_event(self, approval: ConversationApproval, event_type: str, message: str) -> None:
        await self.repository.append_event(
            workspace_id=approval.workspace_id,
            thread_id=approval.thread_id,
            event_type=event_type,
            message=message,
            payload=self._event_payload(approval),
        )

    def _event_payload(self, approval: ConversationApproval) -> dict[str, Any]:
        return {
            "approval_id": str(approval.id),
            "thread_id": str(approval.thread_id),
            "message_id": str(approval.message_id) if approval.message_id else None,
            "route_name": approval.route_name,
            "selected_tool": approval.selected_tool,
            "risk_level": approval.risk_level,
            "approval_status": approval.approval_status,
            "proposed_action": approval.proposed_action,
            "metadata": approval.approval_metadata,
        }

    def _describe_action(self, decision: ConversationRouteDecision) -> str:
        if decision.selected_tool:
            action_type = decision.tool_input.get("action_type") or decision.tool_input.get("openclaw_action_type") or decision.route_name
            return f"{decision.selected_tool}:{action_type}"
        return decision.route_name
