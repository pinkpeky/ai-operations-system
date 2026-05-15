"""Conversation Playbook service and step executor."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
import logging
import re
import time
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.conversation.playbook_definitions import BUILTIN_PLAYBOOKS
from app.conversation.repositories import ConversationRuntimeRepository
from app.conversation.risk_policy import ConversationRiskPolicy
from app.conversation.services.approval_service import ConversationApprovalService
from app.conversation.tool_router import ConversationRouteDecision
from app.models.conversation import ConversationApproval, ConversationPlaybook, ConversationPlaybookRun, ConversationThread
from app.models.enums import ConversationPlaybookRunStatus, ConversationPlaybookStatus, ConversationRunMode
from app.services.output_artifact_service import OutputArtifactService
from app.workflow.services import WorkflowStateService

logger = logging.getLogger(__name__)


@dataclass(slots=True)
class PlaybookExecutionResult:
    """Result returned by PlaybookService."""

    playbook: ConversationPlaybook
    run: ConversationPlaybookRun
    success: bool
    summary: str
    output: dict[str, Any]
    approval: ConversationApproval | None = None
    workflow_run_id: UUID | None = None
    checkpoint_id: UUID | None = None
    memory_snapshot_id: UUID | None = None


class ConversationPlaybookService:
    """Workspace-scoped Playbook manager."""

    URL_PATTERN = re.compile(r"https?://[^\s\u3002\uff0c,]+", flags=re.IGNORECASE)

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ConversationRuntimeRepository(session)
        self.approvals = ConversationApprovalService(session)
        self.risk_policy = ConversationRiskPolicy()

    async def list_playbooks(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        category: str | None = None,
        limit: int = 100,
    ) -> list[ConversationPlaybook]:
        """List playbooks and seed built-ins for this workspace."""

        await self.ensure_builtin_playbooks(workspace_id=workspace_id)
        playbooks = await self.repository.list_playbooks(
            workspace_id=workspace_id,
            status=status,
            category=category,
            limit=limit,
        )
        await self.session.commit()
        return playbooks

    async def get_playbook(self, *, workspace_id: str, playbook_id: UUID) -> ConversationPlaybook | None:
        """Get one playbook."""

        await self.ensure_builtin_playbooks(workspace_id=workspace_id)
        playbook = await self.repository.get_playbook(workspace_id=workspace_id, playbook_id=playbook_id)
        await self.session.commit()
        return playbook

    async def get_playbook_by_name(self, *, workspace_id: str, name: str) -> ConversationPlaybook | None:
        """Get one playbook by name."""

        await self.ensure_builtin_playbooks(workspace_id=workspace_id)
        playbook = await self.repository.get_playbook_by_name(workspace_id=workspace_id, name=name)
        await self.session.commit()
        return playbook

    async def create_playbook(
        self,
        *,
        workspace_id: str,
        name: str,
        description: str | None,
        category: str | None,
        risk_level: str,
        steps: list[dict[str, Any]],
        default_inputs: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        status: str = ConversationPlaybookStatus.ACTIVE.value,
    ) -> ConversationPlaybook:
        """Create a custom playbook."""

        existing = await self.repository.get_playbook_by_name(workspace_id=workspace_id, name=name)
        if existing is not None:
            raise ValueError("Conversation playbook name already exists in workspace")
        playbook = await self.repository.create_playbook(
            workspace_id=workspace_id,
            name=name,
            description=description,
            category=category,
            risk_level=risk_level,
            steps=steps,
            default_inputs=default_inputs,
            metadata=metadata,
            status=status,
        )
        await self.session.commit()
        await self.session.refresh(playbook)
        return playbook

    async def update_playbook(
        self,
        *,
        workspace_id: str,
        playbook_id: UUID,
        patch: dict[str, Any],
    ) -> ConversationPlaybook:
        """Patch a playbook."""

        playbook = await self.require_playbook(workspace_id=workspace_id, playbook_id=playbook_id)
        for field in ("name", "description", "category", "status", "risk_level", "steps", "default_inputs"):
            if field in patch and patch[field] is not None:
                setattr(playbook, field, patch[field])
        if "metadata" in patch and patch["metadata"] is not None:
            playbook.playbook_metadata = patch["metadata"]
        await self.session.commit()
        await self.session.refresh(playbook)
        return playbook

    async def disable_playbook(self, *, workspace_id: str, playbook_id: UUID) -> ConversationPlaybook:
        """Disable a playbook without deleting history."""

        playbook = await self.require_playbook(workspace_id=workspace_id, playbook_id=playbook_id)
        playbook.status = ConversationPlaybookStatus.DISABLED.value
        await self.session.commit()
        await self.session.refresh(playbook)
        return playbook

    async def run_playbook_by_name(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        playbook_name: str,
        input_payload: dict[str, Any],
        mode: str,
        message_id: UUID | None,
        source_message: str,
    ) -> PlaybookExecutionResult:
        """Run a named playbook."""

        playbook = await self.get_playbook_by_name(workspace_id=workspace_id, name=playbook_name)
        if playbook is None:
            raise ValueError(f"Conversation playbook not found: {playbook_name}")
        return await self.run_playbook(
            workspace_id=workspace_id,
            user_id=user_id,
            thread=thread,
            playbook=playbook,
            input_payload=input_payload,
            mode=mode,
            message_id=message_id,
            source_message=source_message,
        )

    async def run_playbook(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        playbook: ConversationPlaybook,
        input_payload: dict[str, Any],
        mode: str,
        message_id: UUID | None,
        source_message: str,
    ) -> PlaybookExecutionResult:
        """Create and execute a playbook run until completion or approval gate."""

        if playbook.status != ConversationPlaybookStatus.ACTIVE.value:
            raise ValueError("Conversation playbook is not active")
        merged_input = self._merge_inputs(playbook, input_payload, source_message)
        run = await self.repository.create_playbook_run(
            workspace_id=workspace_id,
            playbook_id=playbook.id,
            thread_id=thread.id,
            input_payload=merged_input,
            output_payload={"playbook_name": playbook.name, "steps": [], "summary": None},
        )
        run.started_at = datetime.now(UTC)
        run.status = ConversationPlaybookRunStatus.RUNNING.value
        workflow = await WorkflowStateService(self.session).create_workflow_run(
            workspace_id=workspace_id,
            source_type="playbook",
            source_id=str(run.id),
            conversation_thread_id=thread.id,
            playbook_run_id=run.id,
            status="running",
            variables={"playbook_name": playbook.name},
            context={"input": merged_input, "mode": mode},
            metadata={"playbook_id": str(playbook.id), "playbook_run_id": str(run.id)},
            commit=False,
        )
        run.output_payload = {**(run.output_payload or {}), "workflow_run_id": str(workflow.id)}
        flag_modified(run, "output_payload")
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="playbook_selected",
            message=f"Playbook selected: {playbook.name}",
            payload={"playbook_id": str(playbook.id), "playbook_name": playbook.name, "mode": mode},
        )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="playbook_run_started",
            message=f"Playbook run started: {playbook.name}",
            payload={"playbook_run_id": str(run.id), "playbook_name": playbook.name},
        )
        result = await ConversationPlaybookExecutor(self.session).execute(
            workspace_id=workspace_id,
            user_id=user_id,
            thread=thread,
            playbook=playbook,
            run=run,
            mode=mode,
            message_id=message_id,
            source_message=source_message,
            workflow_run_id=workflow.id,
        )
        await self.session.commit()
        await self.session.refresh(run)
        return result

    async def resume_after_approval(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        approval: ConversationApproval,
        source_message: str,
    ) -> PlaybookExecutionResult:
        """Resume a waiting playbook run after an approval is approved."""

        metadata = approval.approval_metadata or {}
        run_id = metadata.get("playbook_run_id")
        if not run_id:
            raise ValueError("Approval is not linked to a playbook run")
        self.approvals.ensure_executable(approval)
        run = await self.require_playbook_run(workspace_id=workspace_id, run_id=UUID(str(run_id)))
        playbook = await self.require_playbook(workspace_id=workspace_id, playbook_id=run.playbook_id)
        thread = await self.repository.get_thread(workspace_id=workspace_id, thread_id=run.thread_id)
        if thread is None:
            raise ValueError("Conversation thread not found for playbook run")
        run.status = ConversationPlaybookRunStatus.RUNNING.value
        workflow_run_id = self._uuid_or_none((run.output_payload or {}).get("workflow_run_id"))
        if workflow_run_id is not None:
            await WorkflowStateService(self.session).resume_workflow(
                workspace_id=workspace_id,
                workflow_run_id=workflow_run_id,
                reason="Playbook resumed after approval",
                commit=False,
            )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="playbook_resumed_after_approval",
            message="Playbook run resumed after approval",
            payload={"playbook_run_id": str(run.id), "approval_id": str(approval.id)},
        )
        result = await ConversationPlaybookExecutor(self.session).execute(
            workspace_id=workspace_id,
            user_id=user_id,
            thread=thread,
            playbook=playbook,
            run=run,
            mode=ConversationRunMode.AUTO_SAFE.value,
            message_id=approval.message_id,
            source_message=source_message,
            approved_step_index=int(metadata.get("playbook_step_index", run.current_step)),
            workflow_run_id=workflow_run_id,
        )
        await self.approvals.mark_executed(workspace_id=workspace_id, approval_id=approval.id, commit=False)
        result.approval = approval
        await self.session.commit()
        await self.session.refresh(run)
        return result

    async def list_playbook_runs(
        self,
        *,
        workspace_id: str,
        thread_id: UUID | None = None,
        status: str | None = None,
        limit: int = 100,
    ) -> list[ConversationPlaybookRun]:
        """List playbook runs."""

        return await self.repository.list_playbook_runs(
            workspace_id=workspace_id,
            thread_id=thread_id,
            status=status,
            limit=limit,
        )

    async def get_playbook_run(self, *, workspace_id: str, run_id: UUID) -> ConversationPlaybookRun | None:
        """Get one playbook run."""

        return await self.repository.get_playbook_run(workspace_id=workspace_id, run_id=run_id)

    async def require_playbook(self, *, workspace_id: str, playbook_id: UUID) -> ConversationPlaybook:
        """Return a playbook or raise."""

        playbook = await self.repository.get_playbook(workspace_id=workspace_id, playbook_id=playbook_id)
        if playbook is None:
            raise ValueError("Conversation playbook not found in workspace")
        return playbook

    async def require_playbook_run(self, *, workspace_id: str, run_id: UUID) -> ConversationPlaybookRun:
        """Return a playbook run or raise."""

        run = await self.repository.get_playbook_run(workspace_id=workspace_id, run_id=run_id)
        if run is None:
            raise ValueError("Conversation playbook run not found in workspace")
        return run

    async def cancel_playbook_run(self, *, workspace_id: str, run_id: UUID) -> ConversationPlaybookRun:
        """Cancel a pending/running/waiting playbook run."""

        run = await self.require_playbook_run(workspace_id=workspace_id, run_id=run_id)
        if run.status in {ConversationPlaybookRunStatus.COMPLETED.value, ConversationPlaybookRunStatus.FAILED.value}:
            raise ValueError("Completed or failed playbook runs cannot be cancelled")
        run.status = ConversationPlaybookRunStatus.CANCELLED.value
        run.completed_at = datetime.now(UTC)
        output = dict(run.output_payload or {})
        output["cancelled_at"] = run.completed_at.isoformat()
        run.output_payload = output
        flag_modified(run, "output_payload")
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=run.thread_id,
            event_type="playbook_cancelled",
            message="Playbook run cancelled",
            payload={"playbook_run_id": str(run.id)},
        )
        await self.session.commit()
        await self.session.refresh(run)
        return run

    async def ensure_builtin_playbooks(self, *, workspace_id: str) -> None:
        """Seed missing built-in playbooks for a workspace."""

        for definition in BUILTIN_PLAYBOOKS:
            existing = await self.repository.get_playbook_by_name(workspace_id=workspace_id, name=definition["name"])
            if existing is not None:
                continue
            await self.repository.create_playbook(
                workspace_id=workspace_id,
                name=definition["name"],
                description=definition.get("description"),
                category=definition.get("category"),
                risk_level=definition["risk_level"],
                steps=definition["steps"],
                default_inputs=definition.get("default_inputs") or {},
                metadata=definition.get("metadata") or {},
            )

    def _merge_inputs(self, playbook: ConversationPlaybook, input_payload: dict[str, Any], source_message: str) -> dict[str, Any]:
        input_body = input_payload.get("input") if isinstance(input_payload.get("input"), dict) else input_payload
        merged: dict[str, Any] = {**(playbook.default_inputs or {}), **(input_body or {})}
        if "message" not in merged and source_message:
            merged["message"] = source_message
        url = self._extract_url(str(merged.get("message") or source_message or ""))
        if url and (not merged.get("url") or merged.get("url") == "https://example.com"):
            merged["url"] = url
        if not merged.get("query"):
            merged["query"] = str(merged.get("message") or source_message or merged.get("topic") or "")
        return merged

    def _extract_url(self, message: str) -> str | None:
        match = self.URL_PATTERN.search(message)
        return match.group(0).rstrip("。,.，") if match else None


    def _uuid_or_none(self, value: Any) -> UUID | None:
        try:
            return UUID(str(value)) if value else None
        except (TypeError, ValueError):
            return None


class ConversationPlaybookExecutor:
    """Execute playbook steps and stop at approval gates."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repository = ConversationRuntimeRepository(session)
        self.approvals = ConversationApprovalService(session)
        self.risk_policy = ConversationRiskPolicy()

    async def execute(
        self,
        *,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        playbook: ConversationPlaybook,
        run: ConversationPlaybookRun,
        mode: str,
        message_id: UUID | None,
        source_message: str,
        approved_step_index: int | None = None,
        workflow_run_id: UUID | None = None,
    ) -> PlaybookExecutionResult:
        """Execute steps until completion, failure, or approval is required."""

        output = dict(run.output_payload or {"steps": []})
        output.setdefault("steps", [])
        workflow_run_id = workflow_run_id or self._uuid_or_none(output.get("workflow_run_id"))
        workflow_service = WorkflowStateService(self.session)
        last_checkpoint_id: UUID | None = None
        last_memory_snapshot_id: UUID | None = None
        start_index = max(0, int(run.current_step or 0))
        for index in range(start_index, len(playbook.steps or [])):
            run.current_step = index
            step = playbook.steps[index]
            started_at = time.perf_counter()
            step_record = self._existing_or_new_step_record(output=output, index=index, step=step)
            workflow_step_id: UUID | None = None
            if workflow_run_id is not None:
                workflow_step = await workflow_service.start_step(
                    workspace_id=workspace_id,
                    workflow_run_id=workflow_run_id,
                    step_index=index,
                    step_name=step_record["title"],
                    step_type=step_record["step_type"],
                    input_payload=step,
                    metadata={"playbook_run_id": str(run.id), "playbook_name": playbook.name},
                    commit=False,
                )
                workflow_step_id = workflow_step.id
                step_record["workflow_step_id"] = str(workflow_step.id)
            run.output_payload = output
            flag_modified(run, "output_payload")
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread.id,
                event_type="playbook_step_started",
                message=f"Playbook step started: {step_record['title']}",
                payload={"playbook_run_id": str(run.id), "step_index": index, "step_type": step_record["step_type"]},
            )
            try:
                decision = self._decision_from_step(step=step, inputs=run.input_payload)
                risk_level = self.risk_policy.assess(decision)
                needs_approval = mode == ConversationRunMode.REVIEW_FIRST.value or (
                    mode == ConversationRunMode.AUTO_SAFE.value and risk_level != "low"
                )
                if needs_approval and approved_step_index != index:
                    approval = await self.approvals.create_approval(
                        workspace_id=workspace_id,
                        thread_id=thread.id,
                        message_id=message_id,
                        decision=decision,
                        risk_level=risk_level,
                        source_message=source_message,
                        metadata={
                            "mode": mode,
                            "playbook_run_id": str(run.id),
                            "playbook_id": str(playbook.id),
                            "playbook_name": playbook.name,
                            "playbook_step_index": index,
                        },
                    )
                    step_record.update(
                        {
                            "status": "waiting_approval",
                            "approval_id": str(approval.id),
                            "risk_level": risk_level,
                            "duration_ms": int((time.perf_counter() - started_at) * 1000),
                        }
                    )
                    run.status = ConversationPlaybookRunStatus.WAITING_APPROVAL.value
                    run.current_step = index
                    output["summary"] = f"Playbook `{playbook.name}` is waiting for approval at step {index}."
                    run.output_payload = output
                    flag_modified(run, "output_payload")
                    if workflow_run_id is not None:
                        await workflow_service.pause_workflow(
                            workspace_id=workspace_id,
                            workflow_run_id=workflow_run_id,
                            reason="Playbook step requires approval",
                            waiting_approval=True,
                            commit=False,
                        )
                        if workflow_step_id is not None:
                            workflow_step.status = "waiting_approval"
                        last_checkpoint = await workflow_service.create_checkpoint(
                            workspace_id=workspace_id,
                            workflow_run_id=workflow_run_id,
                            checkpoint_name=f"approval-step-{index}",
                            checkpoint_type="approval",
                            state_payload={"playbook_run_id": str(run.id), "approval_id": str(approval.id), "step_index": index},
                            created_by=user_id or "ConversationPlaybookExecutor",
                            commit=False,
                        )
                        last_checkpoint_id = last_checkpoint.id
                        output["checkpoint_id"] = str(last_checkpoint.id)
                        run.output_payload = output
                        flag_modified(run, "output_payload")
                    await self.repository.append_event(
                        workspace_id=workspace_id,
                        thread_id=thread.id,
                        event_type="playbook_approval_required",
                        message="Playbook step requires approval",
                        payload={"playbook_run_id": str(run.id), "approval_id": str(approval.id), "step_index": index},
                    )
                    await self.repository.append_event(
                        workspace_id=workspace_id,
                        thread_id=thread.id,
                        event_type="playbook_waiting_approval",
                        message="Playbook run is waiting for approval",
                        payload={"playbook_run_id": str(run.id), "approval_id": str(approval.id)},
                    )
                    return PlaybookExecutionResult(playbook, run, True, output["summary"], output, approval, workflow_run_id, last_checkpoint_id, None)

                success, summary, metadata = await self._execute_step_decision(
                    decision=decision,
                    workspace_id=workspace_id,
                    user_id=user_id,
                    thread=thread,
                    source_message=source_message,
                )
                step_record.update(
                    {
                        "status": "completed" if success else "failed",
                        "output": {"summary": summary, "metadata": metadata},
                        "duration_ms": int((time.perf_counter() - started_at) * 1000),
                        "risk_level": risk_level,
                    }
                )
                if workflow_step_id is not None:
                    if success:
                        await workflow_service.complete_step(
                            workspace_id=workspace_id,
                            workflow_step_id=workflow_step_id,
                            output_payload={"summary": summary, "metadata": metadata},
                            commit=False,
                        )
                    else:
                        await workflow_service.fail_step(
                            workspace_id=workspace_id,
                            workflow_step_id=workflow_step_id,
                            error=summary,
                            output_payload={"summary": summary, "metadata": metadata},
                            commit=False,
                        )
                await self.repository.append_event(
                    workspace_id=workspace_id,
                    thread_id=thread.id,
                    event_type="playbook_step_completed" if success else "playbook_step_failed",
                    message=f"Playbook step {'completed' if success else 'failed'}: {step_record['title']}",
                    payload={"playbook_run_id": str(run.id), "step_index": index, "summary": summary, "metadata": metadata},
                )
                if not success:
                    run.status = ConversationPlaybookRunStatus.FAILED.value
                    run.error = summary
                    run.completed_at = datetime.now(UTC)
                    output["summary"] = summary
                    run.output_payload = output
                    flag_modified(run, "output_payload")
                    await self.repository.append_event(
                        workspace_id=workspace_id,
                        thread_id=thread.id,
                        event_type="playbook_failed",
                        message=summary,
                        payload={"playbook_run_id": str(run.id), "step_index": index},
                    )
                    if workflow_run_id is not None:
                        last_checkpoint = await workflow_service.create_checkpoint(
                            workspace_id=workspace_id,
                            workflow_run_id=workflow_run_id,
                            checkpoint_name=f"failure-step-{index}",
                            checkpoint_type="failure",
                            state_payload={"playbook_run_id": str(run.id), "step_index": index, "error": summary},
                            created_by=user_id or "ConversationPlaybookExecutor",
                            commit=False,
                        )
                        last_checkpoint_id = last_checkpoint.id
                        await workflow_service.fail_workflow(
                            workspace_id=workspace_id,
                            workflow_run_id=workflow_run_id,
                            error=summary,
                            commit=False,
                        )
                    return PlaybookExecutionResult(playbook, run, False, summary, output, None, workflow_run_id, last_checkpoint_id, None)
            except Exception as exc:
                summary = f"Playbook step failed: {str(exc) or exc.__class__.__name__}"
                step_record.update(
                    {
                        "status": "failed",
                        "error": str(exc),
                        "duration_ms": int((time.perf_counter() - started_at) * 1000),
                    }
                )
                run.status = ConversationPlaybookRunStatus.FAILED.value
                run.error = summary
                run.completed_at = datetime.now(UTC)
                output["summary"] = summary
                run.output_payload = output
                flag_modified(run, "output_payload")
                if workflow_step_id is not None:
                    await workflow_service.fail_step(
                        workspace_id=workspace_id,
                        workflow_step_id=workflow_step_id,
                        error=str(exc),
                        output_payload={"summary": summary},
                        commit=False,
                    )
                if workflow_run_id is not None:
                    last_checkpoint = await workflow_service.create_checkpoint(
                        workspace_id=workspace_id,
                        workflow_run_id=workflow_run_id,
                        checkpoint_name=f"failure-step-{index}",
                        checkpoint_type="failure",
                        state_payload={"playbook_run_id": str(run.id), "step_index": index, "error": str(exc)},
                        created_by=user_id or "ConversationPlaybookExecutor",
                        commit=False,
                    )
                    last_checkpoint_id = last_checkpoint.id
                    await workflow_service.fail_workflow(
                        workspace_id=workspace_id,
                        workflow_run_id=workflow_run_id,
                        error=summary,
                        commit=False,
                    )
                await self.repository.append_event(
                    workspace_id=workspace_id,
                    thread_id=thread.id,
                    event_type="playbook_failed",
                    message=summary,
                    payload={"playbook_run_id": str(run.id), "step_index": index, "error": str(exc)},
                )
                return PlaybookExecutionResult(playbook, run, False, summary, output, None, workflow_run_id, last_checkpoint_id, None)

        run.status = ConversationPlaybookRunStatus.COMPLETED.value
        run.current_step = len(playbook.steps or [])
        run.completed_at = datetime.now(UTC)
        output["summary"] = self._summarize_run(playbook=playbook, output=output)
        run.output_payload = output
        flag_modified(run, "output_payload")
        if workflow_run_id is not None:
            last_checkpoint = await workflow_service.create_checkpoint(
                workspace_id=workspace_id,
                workflow_run_id=workflow_run_id,
                checkpoint_name="playbook-final",
                checkpoint_type="auto",
                state_payload={"playbook_run_id": str(run.id), "status": run.status, "summary": output["summary"]},
                created_by=user_id or "ConversationPlaybookExecutor",
                commit=False,
            )
            last_checkpoint_id = last_checkpoint.id
            memory_snapshot = await workflow_service.create_memory_snapshot(
                workspace_id=workspace_id,
                workflow_run_id=workflow_run_id,
                memory_type="task_context",
                summary=output["summary"],
                memory_payload={"playbook_run_id": str(run.id), "steps": output.get("steps", [])},
                metadata={"checkpoint_id": str(last_checkpoint.id), "playbook_name": playbook.name},
                commit=False,
            )
            last_memory_snapshot_id = memory_snapshot.id
            output["checkpoint_id"] = str(last_checkpoint.id)
            output["memory_snapshot_id"] = str(memory_snapshot.id)
            await workflow_service.complete_workflow(
                workspace_id=workspace_id,
                workflow_run_id=workflow_run_id,
                output={"playbook_run_id": str(run.id), "summary": output["summary"]},
                commit=False,
            )
            run.output_payload = output
            flag_modified(run, "output_payload")
        try:
            artifacts = await OutputArtifactService(self.session).create_from_playbook_run(
                workspace_id=workspace_id,
                run_id=run.id,
                created_by=user_id or "conversation_playbook",
                commit=False,
            )
            output["artifacts"] = [
                {"id": str(artifact.id), "artifact_type": artifact.artifact_type, "title": artifact.title}
                for artifact in artifacts
            ]
            run.output_payload = output
            flag_modified(run, "output_payload")
        except Exception as exc:
            logger.exception(
                "Playbook artifact creation failed",
                extra={"workspace_id": workspace_id, "playbook_run_id": str(run.id)},
            )
            await self.repository.append_event(
                workspace_id=workspace_id,
                thread_id=thread.id,
                event_type="bridge_error",
                message="Playbook completed but artifact creation failed",
                payload={"playbook_run_id": str(run.id), "error": str(exc)},
            )
        await self.repository.append_event(
            workspace_id=workspace_id,
            thread_id=thread.id,
            event_type="playbook_completed",
            message=f"Playbook completed: {playbook.name}",
            payload={"playbook_run_id": str(run.id), "playbook_name": playbook.name, "summary": output["summary"]},
        )
        return PlaybookExecutionResult(playbook, run, True, output["summary"], output, None, workflow_run_id, last_checkpoint_id, last_memory_snapshot_id)

    async def _execute_step_decision(
        self,
        *,
        decision: ConversationRouteDecision,
        workspace_id: str,
        user_id: str | None,
        thread: ConversationThread,
        source_message: str,
    ) -> tuple[bool, str, dict[str, Any]]:
        if decision.route_type == "fallback":
            return True, f"Playbook note: {decision.tool_input.get('message') or source_message}", {"route": decision.to_payload()}
        from app.conversation.services.conversation_service import ConversationService

        output: dict[str, Any] = {"route": decision.to_payload(), "tool_results": [], "agent_results": [], "planning_results": [], "errors": []}
        return await ConversationService(self.session)._execute_decision(
            decision=decision,
            workspace_id=workspace_id,
            user_id=user_id,
            thread=thread,
            message=source_message,
            output=output,
        )

    def _decision_from_step(self, *, step: dict[str, Any], inputs: dict[str, Any]) -> ConversationRouteDecision:
        step_type = str(step.get("step_type") or "message")
        if step_type == "summarize":
            return ConversationRouteDecision(
                route_name="playbook_summarize",
                selected_tool=None,
                reason="Playbook summarize step.",
                confidence=1.0,
                tool_input={"message": step.get("title") or "Summarize playbook output"},
                route_type="fallback",
            )
        if step_type == "message":
            return ConversationRouteDecision(
                route_name="playbook_message",
                selected_tool=None,
                reason="Playbook message step.",
                confidence=1.0,
                tool_input={"message": self._render_value(step.get("message") or step.get("title") or "", inputs)},
                route_type="fallback",
            )
        return ConversationRouteDecision(
            route_name=str(step.get("route_name") or step_type),
            selected_tool=step.get("selected_tool"),
            reason=f"Playbook step: {step.get('title') or step_type}",
            confidence=1.0,
            tool_input=self._render_value(step.get("tool_input") or {}, inputs),
            route_type=step.get("route_type") or ("tool" if step.get("selected_tool") else step_type),
            fallback_route="playbook",
        )

    def _new_step_record(self, *, index: int, step: dict[str, Any]) -> dict[str, Any]:
        return {
            "step_index": index,
            "step_type": step.get("step_type") or "message",
            "title": step.get("title") or f"Step {index + 1}",
            "status": "running",
            "input": step,
            "output": None,
            "error": None,
            "duration_ms": None,
        }

    def _existing_or_new_step_record(self, *, output: dict[str, Any], index: int, step: dict[str, Any]) -> dict[str, Any]:
        steps = output.setdefault("steps", [])
        for item in steps:
            if item.get("step_index") == index and item.get("status") == "waiting_approval":
                item["status"] = "running"
                item["error"] = None
                return item
        step_record = self._new_step_record(index=index, step=step)
        steps.append(step_record)
        return step_record

    def _uuid_or_none(self, value: Any) -> UUID | None:
        try:
            return UUID(str(value)) if value else None
        except (TypeError, ValueError):
            return None

    def _render_value(self, value: Any, inputs: dict[str, Any]) -> Any:
        if isinstance(value, str):
            if value.startswith("{") and value.endswith("}") and value.count("{") == 1:
                key = value[1:-1]
                return inputs.get(key)
            try:
                return value.format(**{key: "" if item is None else item for key, item in inputs.items()})
            except Exception:
                return value
        if isinstance(value, dict):
            return {key: self._render_value(item, inputs) for key, item in value.items()}
        if isinstance(value, list):
            return [self._render_value(item, inputs) for item in value]
        return value

    def _summarize_run(self, *, playbook: ConversationPlaybook, output: dict[str, Any]) -> str:
        completed = [item for item in output.get("steps", []) if item.get("status") == "completed"]
        return f"Playbook `{playbook.name}` completed with {len(completed)} completed step(s)."
