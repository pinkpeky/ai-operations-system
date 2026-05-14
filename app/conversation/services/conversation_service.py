"""Conversation Runtime orchestration service.

Phase 38 turns the runtime into a bounded tool execution bridge. It still uses
deterministic routing, polling events, and safe mock/placeholders where the
underlying provider is not available.
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.content_agent import ContentAgent
from app.conversation.repositories import ConversationRuntimeRepository
from app.conversation.risk_policy import ConversationRiskPolicy
from app.conversation.services.approval_service import ConversationApprovalService
from app.conversation.tool_router import ConversationRouteDecision, ConversationToolRouter
from app.memory.services import MemoryService
from app.models.conversation import ConversationApproval, ConversationEvent, ConversationThread
from app.models.enums import ConversationApprovalRiskLevel, ConversationApprovalStatus, ConversationRole, ConversationRunMode, ConversationThreadStatus
from app.models.memory import ConversationMessage
from app.planning.services import PlanningService
from app.tools.base import ToolExecutionContext, ToolExecutionRecord
from app.tools.registry import build_default_tool_registry

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class ConversationRunResult:
    """One conversation turn result."""

    thread_id: UUID
    user_message_id: UUID
    assistant_message_id: UUID
    assistant_message: ConversationMessage
    route: str
    route_name: str
    selected_tool: str | None
    events: list[ConversationEvent]
    events_created: int
    success: bool
    summary: str
    result_metadata: dict[str, Any]
    output: dict[str, Any]
    approval_required: bool = False
    approval_id: UUID | None = None
    approval_status: str | None = None
    risk_level: str | None = None
    proposed_action: str | None = None
    playbook_run_id: UUID | None = None
    playbook_name: str | None = None
    playbook_status: str | None = None


class ConversationService:
    """Conversation runtime service with workspace isolation."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ConversationRuntimeRepository(session)
        self.router = ConversationToolRouter()
        self.risk_policy = ConversationRiskPolicy()
        self.approvals = ConversationApprovalService(session)

    async def create_thread(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        title: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationThread:
        """Create a conversation thread."""

        try:
            thread = await self.repository.create_thread(
                workspace_id=workspace_id,
                user_id=user_id,
                title=title,
                metadata=metadata,
            )
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread.id,
                event_type="thread_created",
                message="Conversation thread created",
                payload={"title": title},
            )
            await self.session.commit()
            await self.session.refresh(thread)
            logger.info("Conversation thread created", extra={"workspace_id": workspace_id, "thread_id": str(thread.id)})
            return thread
        except Exception:
            await self.session.rollback()
            logger.exception("Conversation thread creation failed", extra={"workspace_id": workspace_id})
            raise

    async def list_threads(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationThread]:
        """List conversation threads in one workspace."""

        return await self.repository.list_threads(workspace_id=workspace_id, status=status, limit=limit)

    async def get_thread(self, *, workspace_id: str, thread_id: UUID) -> ConversationThread | None:
        """Get a conversation thread."""

        return await self.repository.get_thread(workspace_id=workspace_id, thread_id=thread_id)

    async def append_message(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        role: str,
        content: str,
        metadata: dict[str, Any] | None = None,
    ) -> ConversationMessage:
        """Append one message and record the matching conversation event."""

        await self._require_thread(workspace_id=workspace_id, thread_id=thread_id)
        message = await self.repository.append_message(
            workspace_id=workspace_id,
            thread_id=thread_id,
            role=role,
            content=content,
            metadata=metadata,
        )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="message_received" if role == ConversationRole.USER.value else "message_appended",
            message=f"{role} message appended",
            payload={"message_id": str(message.id), "role": role},
        )
        await self.session.commit()
        await self.session.refresh(message)
        logger.info(
            "Conversation message appended",
            extra={"workspace_id": workspace_id, "thread_id": str(thread_id), "role": role},
        )
        return message

    async def append_event(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        event_type: str,
        message: str | None = None,
        payload: dict[str, Any] | None = None,
    ) -> ConversationEvent:
        """Append one event."""

        await self._require_thread(workspace_id=workspace_id, thread_id=thread_id)
        event = await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type=event_type,
            message=message,
            payload=payload,
        )
        await self.session.commit()
        await self.session.refresh(event)
        return event

    async def list_messages(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        limit: int = 100,
    ) -> list[ConversationMessage]:
        """List thread messages."""

        await self._require_thread(workspace_id=workspace_id, thread_id=thread_id)
        return await self.repository.list_messages(workspace_id=workspace_id, thread_id=thread_id, limit=limit)

    async def list_events(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        limit: int = 200,
    ) -> list[ConversationEvent]:
        """List thread events."""

        await self._require_thread(workspace_id=workspace_id, thread_id=thread_id)
        return await self.repository.list_events(workspace_id=workspace_id, thread_id=thread_id, limit=limit)

    async def archive_thread(self, *, workspace_id: str, thread_id: UUID) -> ConversationThread:
        """Archive a conversation thread."""

        thread = await self._require_thread(workspace_id=workspace_id, thread_id=thread_id)
        await self.repository.archive_thread(thread=thread)
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="thread_archived",
            message="Conversation thread archived",
        )
        await self.session.commit()
        await self.session.refresh(thread)
        return thread

    async def run_conversation_turn(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        thread_id: UUID,
        run_input: dict[str, Any] | None = None,
    ) -> ConversationRunResult:
        """Run one conversation turn with Phase 39 approval gates."""

        started_at = time.perf_counter()
        run_input = run_input or {}
        mode = str(run_input.get("mode") or ConversationRunMode.AUTO_SAFE.value)
        if mode not in {item.value for item in ConversationRunMode}:
            raise ValueError("mode must be auto_safe, review_first, or execute_after_approval")
        thread = await self._require_thread(workspace_id=workspace_id, thread_id=thread_id)
        events_before = await self.repository.list_events(workspace_id=workspace_id, thread_id=thread.id, limit=10000)
        message, user_message_id = await self._resolve_turn_message(
            workspace_id=workspace_id,
            thread_id=thread.id,
            run_input=run_input,
        )

        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="conversation_run_started",
            message="Conversation run started",
            payload={"message": message[:500]},
        )
        await self._load_memory_context(workspace_id=workspace_id, thread_id=thread.id, message=message)

        playbook_name = self._playbook_name_from_run_input(run_input)
        if mode == ConversationRunMode.EXECUTE_AFTER_APPROVAL.value:
            approval_probe = await self._approval_from_run_input(workspace_id=workspace_id, run_input=run_input)
            if (approval_probe.approval_metadata or {}).get("playbook_run_id"):
                return await self._run_playbook_after_approval(
                    workspace_id=workspace_id,
                    user_id=user_id,
                    thread=thread,
                    message=message,
                    user_message_id=user_message_id,
                    approval=approval_probe,
                    events_before_count=len(events_before),
                    started_at=started_at,
                )
        if playbook_name:
            return await self._run_playbook_by_name(
                workspace_id=workspace_id,
                user_id=user_id,
                thread=thread,
                message=message,
                user_message_id=user_message_id,
                run_input=run_input,
                playbook_name=playbook_name,
                mode=mode,
                events_before_count=len(events_before),
                started_at=started_at,
            )

        approval: ConversationApproval | None = None
        if mode == ConversationRunMode.EXECUTE_AFTER_APPROVAL.value:
            approval = await self._approval_from_run_input(workspace_id=workspace_id, run_input=run_input)
            if approval.thread_id != thread.id:
                raise ValueError("Conversation approval does not belong to this thread")
            self.approvals.ensure_executable(approval)
            decision = self._decision_from_approval(approval)
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread.id,
                event_type="execution_after_approval_started",
                message="Approved conversation execution started",
                payload={"approval_id": str(approval.id), "approval_status": approval.approval_status},
            )
        else:
            decision = self.router.route(message, metadata=thread.thread_metadata, run_input=run_input)
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="route_selected",
            message=f"Route selected: {decision.route_name}",
            payload=decision.to_payload(),
        )
        risk_level = approval.risk_level if approval is not None else self.risk_policy.assess(decision)

        success = False
        summary = ""
        result_metadata: dict[str, Any] = {}
        output: dict[str, Any] = {
            "route": decision.to_payload(),
            "tool_results": [],
            "agent_results": [],
            "planning_results": [],
            "approval": None,
            "errors": [],
        }

        try:
            if mode in {ConversationRunMode.REVIEW_FIRST.value, ConversationRunMode.AUTO_SAFE.value} and (
                mode == ConversationRunMode.REVIEW_FIRST.value or risk_level != ConversationApprovalRiskLevel.LOW.value
            ):
                approval = await self.approvals.create_approval(
                    workspace_id=workspace_id,
                    thread_id=thread.id,
                    message_id=user_message_id,
                    decision=decision,
                    risk_level=risk_level,
                    source_message=message,
                    metadata={"mode": mode},
                )
                output["approval"] = self._approval_payload(approval)
                await self.repository.append_event(
                    workspace_id=workspace_id,
                    thread_id=thread.id,
                    event_type="execution_blocked_pending_approval",
                    message="Execution blocked pending approval",
                    payload=self._approval_payload(approval),
                )
                success = True
                summary = f"Approval required before executing `{decision.route_name}` ({risk_level} risk)."
                result_metadata = {
                    "approval_required": True,
                    "approval": self._approval_payload(approval),
                    "route": decision.to_payload(),
                    "risk_level": risk_level,
                    "mode": mode,
                }
            else:
                success, summary, result_metadata = await self._execute_decision(
                    decision=decision,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    thread=thread,
                    message=message,
                    output=output,
                )
                result_metadata = {**result_metadata, "risk_level": risk_level, "mode": mode}
                if approval is not None:
                    await self.approvals.mark_executed(workspace_id=workspace_id, approval_id=approval.id, commit=False)
                    output["approval"] = self._approval_payload(approval)
                    result_metadata["approval"] = self._approval_payload(approval)
                    await self.repository.append_event(
                        workspace_id=workspace_id,
                        thread_id=thread.id,
                        event_type="execution_after_approval_completed",
                        message="Approved conversation execution completed",
                        payload={"approval_id": str(approval.id), "success": success, "summary": summary},
                    )
        except Exception as exc:
            success = False
            summary = self._readable_error("Conversation bridge failed", exc)
            result_metadata = {"error": str(exc), "route": decision.to_payload()}
            output["errors"].append(str(exc))
            if approval is not None and mode == ConversationRunMode.EXECUTE_AFTER_APPROVAL.value:
                await self.repository.append_event(
                    workspace_id=workspace_id,
                    thread_id=thread.id,
                    event_type="execution_after_approval_failed",
                    message=summary,
                    payload={"approval_id": str(approval.id), "error": str(exc)},
                )
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread.id,
                event_type="bridge_error",
                message=summary,
                payload={"error": str(exc), "route_name": decision.route_name},
            )

        duration_ms = int((time.perf_counter() - started_at) * 1000)
        assistant_content = self._build_assistant_response(summary=summary, success=success, route_name=decision.route_name)
        assistant_message = await self.repository.append_message(
            workspace_id=workspace_id,
            thread_id=thread.id,
            role=ConversationRole.ASSISTANT.value,
            content=assistant_content,
            metadata={
                "route": decision.route_name,
                "route_name": decision.route_name,
                "selected_tool": decision.selected_tool,
                "success": success,
                "summary": summary,
                "duration_ms": duration_ms,
                "result_metadata": result_metadata,
                "output": output,
                "approval_required": result_metadata.get("approval_required", False),
                "approval_id": str(approval.id) if approval is not None else None,
                "approval_status": approval.approval_status if approval is not None else None,
                "risk_level": risk_level,
            },
        )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="assistant_response",
            message="Assistant response generated",
            payload={
                "message_id": str(assistant_message.id),
                "route_name": decision.route_name,
                "selected_tool": decision.selected_tool,
                "success": success,
                "summary": summary,
            },
        )
        await self.session.commit()
        await self.session.refresh(assistant_message)
        events = await self.repository.list_events(workspace_id=workspace_id, thread_id=thread.id, limit=500)
        events_created = max(0, len(events) - len(events_before))
        logger.info(
            "Conversation run completed",
            extra={
                "workspace_id": workspace_id,
                "thread_id": str(thread.id),
                "route_name": decision.route_name,
                "selected_tool": decision.selected_tool,
                "success": success,
                "duration_ms": duration_ms,
            },
        )
        return ConversationRunResult(
            thread_id=thread.id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message.id,
            assistant_message=assistant_message,
            route=decision.route_name,
            route_name=decision.route_name,
            selected_tool=decision.selected_tool,
            events=events,
            events_created=events_created,
            success=success,
            summary=summary,
            result_metadata=result_metadata,
            output=output,
            approval_required=bool(result_metadata.get("approval_required", False)),
            approval_id=approval.id if approval is not None else None,
            approval_status=approval.approval_status if approval is not None else None,
            risk_level=risk_level,
            proposed_action=approval.proposed_action if approval is not None else None,
        )

    def _playbook_name_from_run_input(self, run_input: dict[str, Any]) -> str | None:
        input_payload = run_input.get("input") if isinstance(run_input.get("input"), dict) else {}
        value = run_input.get("playbook_name") or input_payload.get("playbook_name")
        return str(value).strip() if value else None

    async def _run_playbook_by_name(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        message: str,
        user_message_id: UUID,
        run_input: dict[str, Any],
        playbook_name: str,
        mode: str,
        events_before_count: int,
        started_at: float,
    ) -> ConversationRunResult:
        from app.conversation.services.playbook_service import ConversationPlaybookService

        service = ConversationPlaybookService(self.session)
        result = await service.run_playbook_by_name(
            workspace_id=workspace_id,
            user_id=user_id,
            thread=thread,
            playbook_name=playbook_name,
            input_payload=run_input,
            mode=mode,
            message_id=user_message_id,
            source_message=message,
        )
        return await self._conversation_result_from_playbook(
            workspace_id=workspace_id,
            thread=thread,
            user_message_id=user_message_id,
            playbook_result=result,
            events_before_count=events_before_count,
            started_at=started_at,
        )

    async def _run_playbook_after_approval(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        message: str,
        user_message_id: UUID,
        approval: ConversationApproval,
        events_before_count: int,
        started_at: float,
    ) -> ConversationRunResult:
        from app.conversation.services.playbook_service import ConversationPlaybookService

        service = ConversationPlaybookService(self.session)
        result = await service.resume_after_approval(
            workspace_id=workspace_id,
            user_id=user_id,
            approval=approval,
            source_message=message,
        )
        return await self._conversation_result_from_playbook(
            workspace_id=workspace_id,
            thread=thread,
            user_message_id=user_message_id,
            playbook_result=result,
            events_before_count=events_before_count,
            started_at=started_at,
        )

    async def _conversation_result_from_playbook(
        self,
        *,
        workspace_id: str,
        thread: ConversationThread,
        user_message_id: UUID,
        playbook_result: Any,
        events_before_count: int,
        started_at: float,
    ) -> ConversationRunResult:
        approval_payload = self._approval_payload(playbook_result.approval) if playbook_result.approval is not None else None
        duration_ms = int((time.perf_counter() - started_at) * 1000)
        approval_required = bool(playbook_result.approval is not None and playbook_result.approval.approval_status == ConversationApprovalStatus.PENDING.value)
        summary = playbook_result.summary
        metadata = {
            "playbook_id": str(playbook_result.playbook.id),
            "playbook_name": playbook_result.playbook.name,
            "playbook_run_id": str(playbook_result.run.id),
            "playbook_status": playbook_result.run.status,
            "approval_required": approval_required,
            "approval": approval_payload,
            "output": playbook_result.output,
            "duration_ms": duration_ms,
        }
        assistant_message = await self.repository.append_message(
            workspace_id=workspace_id,
            thread_id=thread.id,
            role=ConversationRole.ASSISTANT.value,
            content=self._build_assistant_response(
                summary=summary,
                success=playbook_result.success,
                route_name=f"playbook:{playbook_result.playbook.name}",
            ),
            metadata={
                "route": f"playbook:{playbook_result.playbook.name}",
                "route_name": f"playbook:{playbook_result.playbook.name}",
                "success": playbook_result.success,
                "summary": summary,
                "duration_ms": duration_ms,
                "result_metadata": metadata,
                "output": playbook_result.output,
                "approval_required": approval_required,
                "approval_id": str(playbook_result.approval.id) if playbook_result.approval is not None else None,
                "approval_status": playbook_result.approval.approval_status if playbook_result.approval is not None else None,
                "risk_level": playbook_result.approval.risk_level if playbook_result.approval is not None else playbook_result.playbook.risk_level,
                "playbook_run_id": str(playbook_result.run.id),
                "playbook_name": playbook_result.playbook.name,
                "playbook_status": playbook_result.run.status,
            },
        )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="assistant_response",
            message="Assistant response generated for playbook run",
            payload={
                "message_id": str(assistant_message.id),
                "playbook_run_id": str(playbook_result.run.id),
                "playbook_name": playbook_result.playbook.name,
                "success": playbook_result.success,
                "summary": summary,
            },
        )
        await self.session.commit()
        await self.session.refresh(assistant_message)
        events = await self.repository.list_events(workspace_id=workspace_id, thread_id=thread.id, limit=500)
        return ConversationRunResult(
            thread_id=thread.id,
            user_message_id=user_message_id,
            assistant_message_id=assistant_message.id,
            assistant_message=assistant_message,
            route=f"playbook:{playbook_result.playbook.name}",
            route_name=f"playbook:{playbook_result.playbook.name}",
            selected_tool=None,
            events=events,
            events_created=max(0, len(events) - events_before_count),
            success=playbook_result.success,
            summary=summary,
            result_metadata=metadata,
            output=playbook_result.output,
            approval_required=approval_required,
            approval_id=playbook_result.approval.id if playbook_result.approval is not None else None,
            approval_status=playbook_result.approval.approval_status if playbook_result.approval is not None else None,
            risk_level=playbook_result.approval.risk_level if playbook_result.approval is not None else playbook_result.playbook.risk_level,
            proposed_action=playbook_result.approval.proposed_action if playbook_result.approval is not None else None,
            playbook_run_id=playbook_result.run.id,
            playbook_name=playbook_result.playbook.name,
            playbook_status=playbook_result.run.status,
        )

    async def _approval_from_run_input(self, *, workspace_id: str, run_input: dict[str, Any]) -> ConversationApproval:
        input_payload = run_input.get("input") if isinstance(run_input.get("input"), dict) else run_input
        approval_id_value = input_payload.get("approval_id") if isinstance(input_payload, dict) else None
        if not approval_id_value:
            raise ValueError("execute_after_approval mode requires input.approval_id")
        return await self.approvals.require_approval(workspace_id=workspace_id, approval_id=UUID(str(approval_id_value)))

    def _decision_from_approval(self, approval: ConversationApproval) -> ConversationRouteDecision:
        decision_payload = approval.proposed_payload.get("decision") if isinstance(approval.proposed_payload, dict) else None
        if not isinstance(decision_payload, dict):
            raise ValueError("Conversation approval is missing proposed decision payload")
        return ConversationRouteDecision(
            route_name=str(decision_payload.get("route_name") or approval.route_name),
            selected_tool=decision_payload.get("selected_tool") or approval.selected_tool,
            reason=str(decision_payload.get("reason") or "Approved conversation action"),
            confidence=float(decision_payload.get("confidence") or 1.0),
            tool_input=decision_payload.get("tool_input") if isinstance(decision_payload.get("tool_input"), dict) else {},
            route_type=decision_payload.get("route_type") or ("tool" if approval.selected_tool else "fallback"),
            fallback_route=str(decision_payload.get("fallback_route") or "default"),
        )

    def _approval_payload(self, approval: ConversationApproval) -> dict[str, Any]:
        return {
            "approval_id": str(approval.id),
            "approval_status": approval.approval_status,
            "risk_level": approval.risk_level,
            "route_name": approval.route_name,
            "selected_tool": approval.selected_tool,
            "proposed_action": approval.proposed_action,
            "proposed_payload": approval.proposed_payload,
        }

    async def _resolve_turn_message(
        self,
        *,
        workspace_id: str,
        thread_id: UUID,
        run_input: dict[str, Any],
    ) -> tuple[str, UUID]:
        """Resolve the current user message and avoid duplicate appends."""

        input_payload = run_input.get("input") if "input" in run_input else run_input
        if not isinstance(input_payload, dict):
            input_payload = {}
        message = str(input_payload.get("message") or "").strip()
        messages = await self.repository.list_messages(workspace_id=workspace_id, thread_id=thread_id, limit=200)
        if message:
            last = messages[-1] if messages else None
            if last is not None and last.role == ConversationRole.USER.value and last.content == message:
                return message, last.id
            user_message = await self.repository.append_message(
                workspace_id=workspace_id,
                thread_id=thread_id,
                role=ConversationRole.USER.value,
                content=message,
                metadata={"source": "run"},
            )
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="message_received",
                message="User message received by run endpoint",
                payload={"message_id": str(user_message.id)},
            )
            return message, user_message.id
        for item in reversed(messages):
            if item.role == ConversationRole.USER.value:
                return item.content, item.id
        raise ValueError("No user message available for conversation run")

    async def _load_memory_context(self, *, workspace_id: str, thread_id: UUID, message: str) -> None:
        """Load lightweight memory context and record a best-effort event."""

        started_at = time.perf_counter()
        try:
            memories = await MemoryService(self.session).search_memory(workspace_id=workspace_id, query=message, limit=3)
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="memory_loaded",
                message="Memory context loaded",
                payload={
                    "retrieved_memories_count": len(memories),
                    "latency_ms": int((time.perf_counter() - started_at) * 1000),
                },
            )
        except Exception as exc:
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="bridge_error",
                message="Memory context load failed",
                payload={"error": str(exc)},
            )

    async def _execute_decision(
        self,
        *,
        decision: ConversationRouteDecision,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        message: str,
        output: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        if decision.route_type == "tool":
            return await self._execute_tool_route(
                decision=decision,
                workspace_id=workspace_id,
                user_id=user_id,
                thread_id=thread.id,
                output=output,
            )
        if decision.route_type == "agent":
            return await self._execute_content_agent_route(
                decision=decision,
                workspace_id=workspace_id,
                user_id=user_id,
                thread_id=thread.id,
                output=output,
            )
        if decision.route_type == "planning":
            return await self._execute_planning_route(
                decision=decision,
                workspace_id=workspace_id,
                user_id=user_id,
                thread=thread,
                output=output,
            )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="bridge_fallback",
            message="No executable route matched",
            payload={"message": message[:500], "route": decision.to_payload()},
        )
        summary = "No tool route matched. The message was stored and the event timeline was updated."
        return True, summary, {"route": decision.to_payload(), "fallback": True}

    async def _execute_tool_route(
        self,
        *,
        decision: ConversationRouteDecision,
        workspace_id: str,
        user_id: str | None,
        thread_id: UUID,
        output: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        if decision.selected_tool == "browser_tool" and decision.tool_input.get("action_type") == "navigate_and_screenshot":
            return await self._execute_browser_bridge(
                decision=decision,
                workspace_id=workspace_id,
                user_id=user_id,
                thread_id=thread_id,
                output=output,
            )
        if decision.selected_tool == "rag_search_tool" and not decision.tool_input.get("collection_name"):
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="bridge_fallback",
                message="RAG search needs a collection_name",
                payload={"route": decision.to_payload()},
            )
            summary = "RAG search needs a collection_name in the conversation metadata or run input."
            metadata = {"route": decision.to_payload(), "missing": "collection_name"}
            output["errors"].append(summary)
            return False, summary, metadata
        return await self._execute_single_tool(
            decision=decision,
            workspace_id=workspace_id,
            user_id=user_id,
            thread_id=thread_id,
            output=output,
        )

    async def _execute_single_tool(
        self,
        *,
        decision: ConversationRouteDecision,
        workspace_id: str,
        user_id: str | None,
        thread_id: UUID,
        output: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        if decision.selected_tool is None:
            raise ValueError("Tool route selected without a tool name")
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="tool_execution_started",
            message=f"{decision.selected_tool} execution started",
            payload={"tool_name": decision.selected_tool, "tool_input": decision.tool_input},
        )
        record = await self._execute_tool(
            tool_name=decision.selected_tool,
            tool_input=decision.tool_input,
            workspace_id=workspace_id,
            user_id=user_id,
        )
        output["tool_results"].append(record.model_dump())
        event_type = "tool_execution_completed" if record.success else "tool_execution_failed"
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type=event_type,
            message=f"{decision.selected_tool} execution {'completed' if record.success else 'failed'}",
            payload=record.model_dump(),
        )
        if record.success:
            summary = self._summarize_tool_result(decision.selected_tool, record.tool_output)
            return True, summary, {"tool_record": record.model_dump(), "route": decision.to_payload()}
        summary = record.error or f"{decision.selected_tool} failed"
        return False, summary, {"tool_record": record.model_dump(), "route": decision.to_payload()}

    async def _execute_browser_bridge(
        self,
        *,
        decision: ConversationRouteDecision,
        workspace_id: str,
        user_id: str | None,
        thread_id: UUID,
        output: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        """Compose browser runtime actions through browser_tool.

        The bridge never performs social-platform automation. It only opens the
        requested URL, captures a screenshot, reads page metadata, and closes the
        runtime session when possible.
        """

        target = str(decision.tool_input.get("target") or decision.tool_input.get("url") or "https://example.com")
        screenshot_name = str(decision.tool_input.get("screenshot_name") or "conversation-browser")
        records: list[dict[str, Any]] = []
        runtime_session_id: str | None = None
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="tool_execution_started",
            message="browser_tool composite execution started",
            payload={"target": target, "screenshot_name": screenshot_name},
        )
        try:
            create_record = await self._execute_tool(
                tool_name="browser_tool",
                tool_input={"action_type": "create_session", "browser": "chromium", "metadata": decision.tool_input.get("metadata") or {}},
                workspace_id=workspace_id,
                user_id=user_id,
            )
            records.append(create_record.model_dump())
            output["tool_results"].append(create_record.model_dump())
            if not create_record.success:
                return await self._browser_bridge_failed(workspace_id, thread_id, output, records, create_record.error)

            runtime_session_id = str(((create_record.tool_output or {}).get("session") or {}).get("id") or "")
            if not runtime_session_id:
                return await self._browser_bridge_failed(workspace_id, thread_id, output, records, "Browser session id missing")

            for action_name, tool_input in (
                (
                    "navigate",
                    {"action_type": "navigate", "runtime_session_id": runtime_session_id, "url": target, "target": target},
                ),
                (
                    "screenshot",
                    {
                        "action_type": "screenshot",
                        "runtime_session_id": runtime_session_id,
                        "full_page": True,
                        "screenshot_name": screenshot_name,
                    },
                ),
                ("get_page", {"action_type": "get_page", "runtime_session_id": runtime_session_id}),
            ):
                await self.repository.append_event(
                    workspace_id=workspace_id,
                    thread_id=thread_id,
                    event_type="worker_action_started",
                    message=f"browser_tool {action_name} started",
                    payload={"action_type": action_name, "runtime_session_id": runtime_session_id},
                )
                record = await self._execute_tool(
                    tool_name="browser_tool",
                    tool_input=tool_input,
                    workspace_id=workspace_id,
                    user_id=user_id,
                )
                records.append(record.model_dump())
                output["tool_results"].append(record.model_dump())
                await self.repository.append_event(
                    workspace_id=workspace_id,
                    thread_id=thread_id,
                    event_type="worker_action_completed" if record.success else "tool_execution_failed",
                    message=f"browser_tool {action_name} {'completed' if record.success else 'failed'}",
                    payload=record.model_dump(),
                )
                if not record.success:
                    close_record = await self._execute_tool(
                        tool_name="browser_tool",
                        tool_input={"action_type": "close_session", "runtime_session_id": runtime_session_id},
                        workspace_id=workspace_id,
                        user_id=user_id,
                    )
                    records.append(close_record.model_dump())
                    output["tool_results"].append(close_record.model_dump())
                    return await self._browser_bridge_failed(workspace_id, thread_id, output, records, record.error)

            close_record = await self._execute_tool(
                tool_name="browser_tool",
                tool_input={"action_type": "close_session", "runtime_session_id": runtime_session_id},
                workspace_id=workspace_id,
                user_id=user_id,
            )
            records.append(close_record.model_dump())
            output["tool_results"].append(close_record.model_dump())

            metadata = {
                "route": decision.to_payload(),
                "runtime_session_id": runtime_session_id,
                "target": target,
                "records": records,
                "screenshot": self._last_output_value(records, "last_screenshot_path") or self._last_output_value(records, "screenshot_path"),
                "page_title": self._last_output_value(records, "page_title") or self._last_output_value(records, "title"),
            }
            summary = f"Browser bridge opened {target}, captured a screenshot, fetched page metadata, and closed the session."
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="tool_execution_completed",
                message="browser_tool composite execution completed",
                payload={"summary": summary, "runtime_session_id": runtime_session_id},
            )
            return True, summary, metadata
        finally:
            if runtime_session_id:
                logger.debug("Conversation browser bridge used runtime session", extra={"runtime_session_id": runtime_session_id})

    async def _browser_bridge_failed(
        self,
        workspace_id: str,
        thread_id: UUID,
        output: dict[str, Any],
        records: list[dict[str, Any]],
        error: str | None,
    ) -> tuple[bool, str, dict[str, Any]]:
        summary = error or "Browser bridge failed"
        output["errors"].append(summary)
        metadata = {"records": records, "error": summary}
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="tool_execution_failed",
            message="browser_tool composite execution failed",
            payload=metadata,
        )
        return False, summary, metadata

    async def _execute_content_agent_route(
        self,
        *,
        decision: ConversationRouteDecision,
        workspace_id: str,
        user_id: str | None,
        thread_id: UUID,
        output: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread_id,
            event_type="agent_execution_started",
            message="ContentAgent execution started",
            payload={"agent_name": "ContentAgent", "input": decision.tool_input},
        )
        try:
            result = await ContentAgent().run(
                {
                    **decision.tool_input,
                    "workspace_id": workspace_id,
                    "user_id": user_id,
                }
            )
            output["agent_results"].append({"agent_name": "ContentAgent", "success": True, "output": result})
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="agent_execution_completed",
                message="ContentAgent execution completed",
                payload={"agent_name": "ContentAgent", "output": result},
            )
            summary = self._summarize_content_result(result)
            return True, summary, {"agent_name": "ContentAgent", "output": result, "route": decision.to_payload()}
        except Exception as exc:
            summary = self._readable_error("ContentAgent execution failed", exc)
            output["errors"].append(summary)
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread_id,
                event_type="agent_execution_completed",
                message="ContentAgent execution completed with fallback",
                payload={"agent_name": "ContentAgent", "success": False, "error": str(exc)},
            )
            fallback = {
                "title": "Content generation fallback",
                "description": f"Request received: {decision.tool_input.get('topic')}",
                "tags": ["ai-ops", "conversation-runtime"],
                "cta": "Add platform and style details to generate a stronger draft.",
                "raw_response": str(exc),
            }
            return False, self._summarize_content_result(fallback), {
                "agent_name": "ContentAgent",
                "output": fallback,
                "error": str(exc),
                "route": decision.to_payload(),
            }

    async def _execute_planning_route(
        self,
        *,
        decision: ConversationRouteDecision,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        output: dict[str, Any],
    ) -> tuple[bool, str, dict[str, Any]]:
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="planning_execution_started",
            message="PlanningService execution started",
            payload={"root_goal": decision.tool_input.get("root_goal")},
        )
        try:
            plan = await PlanningService(self.session).create_plan(
                workspace_id=workspace_id,
                session_id=None,
                root_goal=str(decision.tool_input.get("root_goal") or ""),
                planner_agent="simple_planner",
                metadata={
                    **(decision.tool_input.get("metadata") or {}),
                    "conversation_thread_id": str(thread.id),
                    "user_id": user_id,
                },
                auto_create_steps=True,
            )
            steps = await PlanningService(self.session).list_steps(workspace_id=workspace_id, plan_id=plan.id)
            step_payload = [
                {
                    "id": str(step.id),
                    "step_order": step.step_order,
                    "agent_name": step.agent_name,
                    "tool_name": step.tool_name,
                    "title": step.title,
                    "status": step.status,
                }
                for step in steps
            ]
            metadata = {"plan_id": str(plan.id), "status": plan.status, "steps": step_payload, "route": decision.to_payload()}
            output["planning_results"].append(metadata)
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread.id,
                event_type="planning_execution_completed",
                message="PlanningService created a plan",
                payload=metadata,
            )
            summary = f"Plan created: {plan.id} with {len(step_payload)} step(s)."
            return True, summary, metadata
        except Exception as exc:
            summary = self._readable_error("PlanningService execution failed", exc)
            output["errors"].append(summary)
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread.id,
                event_type="bridge_error",
                message=summary,
                payload={"error": str(exc), "route": decision.to_payload()},
            )
            return False, summary, {"error": str(exc), "route": decision.to_payload()}

    async def _execute_tool(
        self,
        *,
        tool_name: str,
        tool_input: dict[str, Any],
        workspace_id: str,
        user_id: str | None,
    ) -> ToolExecutionRecord:
        registry = build_default_tool_registry()
        return await registry.execute_tool(
            tool_name=tool_name,
            tool_input=tool_input,
            context=ToolExecutionContext(
                workspace_id=workspace_id,
                user_id=user_id,
                session=self.session,
                agent_name="conversation_runtime",
            ),
            agent_name="conversation_runtime",
        )

    def _build_assistant_response(self, *, summary: str, success: bool, route_name: str) -> str:
        status = "completed" if success else "failed"
        return f"Conversation bridge {status} via `{route_name}`.\n\n{summary}".strip()

    def _summarize_tool_result(self, tool_name: str, tool_output: dict[str, Any]) -> str:
        if tool_name == "openclaw_tool":
            mock = tool_output.get("mock") or (tool_output.get("result") or {}).get("mock")
            return f"OpenClaw mock bridge completed. mock={bool(mock)}; no real device action was executed."
        if tool_name == "rag_search_tool":
            chunks = tool_output.get("chunks") or tool_output.get("results") or tool_output.get("items") or []
            return f"RAG bridge completed with {len(chunks) if isinstance(chunks, list) else 0} retrieved chunk(s)."
        if tool_name == "create_task_tool":
            task_id = (tool_output.get("task") or {}).get("id") or tool_output.get("task_id")
            return f"Task bridge created task {task_id or '[unknown]'}."
        return f"{tool_name} bridge completed."

    def _summarize_content_result(self, result: dict[str, Any]) -> str:
        title = str(result.get("title") or "Untitled")
        description = str(result.get("description") or "")
        cta = str(result.get("cta") or "")
        tags = result.get("tags") or []
        return f"{title}\n\n{description}\n\nTags: {tags}\nCTA: {cta}".strip()

    def _last_output_value(self, records: list[dict[str, Any]], key: str) -> Any:
        for record in reversed(records):
            output = record.get("tool_output") or {}
            stack: list[Any] = [output]
            while stack:
                current = stack.pop()
                if isinstance(current, dict):
                    if key in current and current[key] not in (None, ""):
                        return current[key]
                    stack.extend(current.values())
        return None

    def _readable_error(self, prefix: str, exc: Exception) -> str:
        return f"{prefix}: {str(exc) or exc.__class__.__name__}"

    async def _require_thread(self, *, workspace_id: str, thread_id: UUID) -> ConversationThread:
        """Validate that the thread exists in the current workspace."""

        thread = await self.repository.get_thread(workspace_id=workspace_id, thread_id=thread_id)
        if thread is None or thread.status == ConversationThreadStatus.DELETED.value:
            raise ValueError("Conversation thread not found in workspace")
        return thread
