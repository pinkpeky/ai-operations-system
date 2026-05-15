"""Task orchestration service.

This layer wraps Conversation and Playbook execution with background task
state, retry, approval pause/resume, and artifact linkage. It intentionally
does not modify the legacy Scheduler or TaskExecutor.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.conversation.services import ConversationApprovalService, ConversationService
from app.models.enums import ConversationApprovalStatus, TaskRunPriority, TaskRunStatus
from app.models.task_run import TaskRun, TaskRunEvent
from app.services.output_artifact_service import OutputArtifactService
from app.task_orchestration.retry_policy import TaskRetryPolicy

logger = logging.getLogger(__name__)


class TaskOrchestratorService:
    """Workspace-scoped task orchestration manager."""

    TERMINAL_STATUSES = {
        TaskRunStatus.COMPLETED.value,
        TaskRunStatus.FAILED.value,
        TaskRunStatus.CANCELLED.value,
        TaskRunStatus.EXPIRED.value,
    }

    def __init__(self, session: AsyncSession, *, retry_policy: TaskRetryPolicy | None = None) -> None:
        self.session = session
        self.retry_policy = retry_policy or TaskRetryPolicy()

    async def enqueue_task(
        self,
        *,
        workspace_id: str,
        task_type: str,
        source_type: str,
        source_id: str | None,
        input_payload: dict[str, Any],
        created_by: str | None = None,
        priority: str = TaskRunPriority.NORMAL.value,
        max_retries: int = 3,
        scheduled_at: datetime | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> TaskRun:
        """Create a task run and place it in pending/queued state."""

        now = datetime.now(UTC)
        if scheduled_at is not None and scheduled_at.tzinfo is None:
            scheduled_at = scheduled_at.replace(tzinfo=UTC)
        status = TaskRunStatus.PENDING.value if scheduled_at and scheduled_at > now else TaskRunStatus.QUEUED.value
        task = TaskRun(
            workspace_id=workspace_id,
            task_type=task_type,
            source_type=source_type,
            source_id=source_id,
            status=status,
            priority=priority,
            max_retries=max_retries,
            scheduled_at=scheduled_at,
            input_payload=input_payload,
            output_payload={},
            task_metadata=metadata or {},
            created_by=created_by,
        )
        self.session.add(task)
        await self.session.flush()
        await self.append_event(
            workspace_id=workspace_id,
            task_run_id=task.id,
            event_type="task_created",
            status=task.status,
            message="Task run created",
            payload={"task_type": task_type, "source_type": source_type, "source_id": source_id},
            commit=False,
        )
        await self.append_event(
            workspace_id=workspace_id,
            task_run_id=task.id,
            event_type="task_queued" if status == TaskRunStatus.QUEUED.value else "task_scheduled",
            status=task.status,
            message="Task run queued" if status == TaskRunStatus.QUEUED.value else "Task run scheduled",
            payload={"scheduled_at": scheduled_at.isoformat() if scheduled_at else None, "priority": priority},
            commit=False,
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(task)
        logger.info("Task run enqueued", extra={"workspace_id": workspace_id, "task_run_id": str(task.id), "status": status})
        return task

    async def schedule_task(self, **kwargs: Any) -> TaskRun:
        """Alias for enqueue_task with scheduled_at provided."""

        return await self.enqueue_task(**kwargs)

    async def get_task(self, *, workspace_id: str, task_run_id: UUID) -> TaskRun | None:
        statement = select(TaskRun).where(TaskRun.workspace_id == workspace_id, TaskRun.id == task_run_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def require_task(self, *, workspace_id: str, task_run_id: UUID) -> TaskRun:
        task = await self.get_task(workspace_id=workspace_id, task_run_id=task_run_id)
        if task is None:
            raise ValueError("Task run not found in workspace")
        return task

    async def list_tasks(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        task_type: str | None = None,
        source_type: str | None = None,
        created_from: datetime | None = None,
        created_to: datetime | None = None,
        limit: int = 100,
    ) -> list[TaskRun]:
        statement = select(TaskRun).where(TaskRun.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(TaskRun.status == status)
        if task_type is not None:
            statement = statement.where(TaskRun.task_type == task_type)
        if source_type is not None:
            statement = statement.where(TaskRun.source_type == source_type)
        if created_from is not None:
            statement = statement.where(TaskRun.created_at >= created_from)
        if created_to is not None:
            statement = statement.where(TaskRun.created_at <= created_to)
        statement = statement.order_by(TaskRun.created_at.desc()).limit(limit)
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def list_events(self, *, workspace_id: str, task_run_id: UUID, limit: int = 300) -> list[TaskRunEvent]:
        await self.require_task(workspace_id=workspace_id, task_run_id=task_run_id)
        statement = (
            select(TaskRunEvent)
            .where(TaskRunEvent.workspace_id == workspace_id, TaskRunEvent.task_run_id == task_run_id)
            .order_by(TaskRunEvent.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def append_event(
        self,
        *,
        workspace_id: str,
        task_run_id: UUID,
        event_type: str,
        status: str | None = None,
        message: str | None = None,
        payload: dict[str, Any] | None = None,
        error: str | None = None,
        commit: bool = True,
    ) -> TaskRunEvent:
        event = TaskRunEvent(
            workspace_id=workspace_id,
            task_run_id=task_run_id,
            event_type=event_type,
            status=status,
            message=message,
            payload=payload or {},
            error=error,
        )
        self.session.add(event)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(event)
        return event

    async def start_task(self, *, task: TaskRun, commit: bool = True) -> TaskRun:
        if task.status == TaskRunStatus.CANCELLED.value:
            raise ValueError("Cancelled task runs cannot be started")
        task.status = TaskRunStatus.RUNNING.value
        task.started_at = datetime.now(UTC)
        await self.append_event(
            workspace_id=task.workspace_id,
            task_run_id=task.id,
            event_type="task_started",
            status=task.status,
            message="Task run started",
            payload={"retry_count": task.retry_count},
            commit=False,
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(task)
        return task

    async def complete_task(self, *, task: TaskRun, output_payload: dict[str, Any] | None = None, commit: bool = True) -> TaskRun:
        now = datetime.now(UTC)
        task.status = TaskRunStatus.COMPLETED.value
        task.completed_at = now
        if output_payload is not None:
            task.output_payload = output_payload
            flag_modified(task, "output_payload")
        await self.append_event(
            workspace_id=task.workspace_id,
            task_run_id=task.id,
            event_type="task_completed",
            status=task.status,
            message="Task run completed",
            payload={"output_summary": self._summary_from_output(task.output_payload)},
            commit=False,
        )
        await self._link_artifacts(task=task)
        if commit:
            await self.session.commit()
            await self.session.refresh(task)
        return task

    async def fail_task(self, *, task: TaskRun, error: str, output_payload: dict[str, Any] | None = None, commit: bool = True) -> TaskRun:
        if self.retry_policy.should_retry(error=error, retry_count=task.retry_count, max_retries=task.max_retries):
            return await self.retry_task(task=task, reason=error, commit=commit)
        task.status = TaskRunStatus.FAILED.value
        task.failed_at = datetime.now(UTC)
        task.error = error
        if output_payload is not None:
            task.output_payload = output_payload
            flag_modified(task, "output_payload")
        await self.append_event(
            workspace_id=task.workspace_id,
            task_run_id=task.id,
            event_type="task_failed",
            status=task.status,
            message="Task run failed",
            error=error,
            payload={"retry_count": task.retry_count, "max_retries": task.max_retries},
            commit=False,
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(task)
        return task

    async def retry_task(self, *, task: TaskRun, reason: str | None = None, commit: bool = True) -> TaskRun:
        if task.status not in {TaskRunStatus.FAILED.value, TaskRunStatus.RETRYING.value, TaskRunStatus.RUNNING.value}:
            raise ValueError("Only failed/retryable task runs can be retried")
        if task.retry_count >= task.max_retries:
            raise ValueError("Task run retry limit reached")
        delay = self.retry_policy.next_delay_seconds(task.retry_count)
        task.retry_count += 1
        task.status = TaskRunStatus.RETRYING.value
        task.scheduled_at = datetime.now(UTC) + timedelta(seconds=delay)
        task.error = reason
        await self.append_event(
            workspace_id=task.workspace_id,
            task_run_id=task.id,
            event_type="task_retry_scheduled",
            status=task.status,
            message="Task run retry scheduled",
            error=reason,
            payload={"retry_count": task.retry_count, "next_retry_delay_seconds": delay, "retry_reason": reason},
            commit=False,
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(task)
        return task

    async def cancel_task(self, *, workspace_id: str, task_run_id: UUID, reason: str | None = None) -> TaskRun:
        task = await self.require_task(workspace_id=workspace_id, task_run_id=task_run_id)
        if task.status in {TaskRunStatus.COMPLETED.value, TaskRunStatus.CANCELLED.value}:
            raise ValueError("Completed or cancelled task runs cannot be cancelled")
        task.status = TaskRunStatus.CANCELLED.value
        task.cancelled_at = datetime.now(UTC)
        task.error = reason
        await self.append_event(
            workspace_id=workspace_id,
            task_run_id=task.id,
            event_type="task_cancelled",
            status=task.status,
            message="Task run cancelled",
            error=reason,
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def poll_pending_tasks(self, *, limit: int = 10) -> list[TaskRun]:
        now = datetime.now(UTC)
        statement = (
            select(TaskRun)
            .where(
                TaskRun.status.in_([TaskRunStatus.PENDING.value, TaskRunStatus.QUEUED.value, TaskRunStatus.RETRYING.value]),
                ((TaskRun.scheduled_at.is_(None)) | (TaskRun.scheduled_at <= now)),
            )
            .order_by(TaskRun.priority.desc(), TaskRun.created_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def execute_task(self, *, task: TaskRun) -> TaskRun:
        """Run a task once. The caller owns the AsyncSession lifecycle."""

        if task.status == TaskRunStatus.CANCELLED.value:
            return task
        try:
            await self.start_task(task=task, commit=False)
            await self.append_event(
                workspace_id=task.workspace_id,
                task_run_id=task.id,
                event_type="task_step_started",
                status=task.status,
                message="Conversation/Playbook execution started",
                payload={"task_type": task.task_type, "source_type": task.source_type},
                commit=False,
            )
            result_payload = await self._execute_payload(task)
            task.current_step = int(result_payload.get("current_step") or task.current_step)
            if result_payload.get("approval_required"):
                task.status = TaskRunStatus.WAITING_APPROVAL.value
                task.output_payload = result_payload
                flag_modified(task, "output_payload")
                await self.append_event(
                    workspace_id=task.workspace_id,
                    task_run_id=task.id,
                    event_type="task_waiting_approval",
                    status=task.status,
                    message="Task run is waiting for approval",
                    payload={
                        "approval_id": result_payload.get("approval_id"),
                        "playbook_run_id": result_payload.get("playbook_run_id"),
                    },
                    commit=False,
                )
                await self.session.commit()
                await self.session.refresh(task)
                return task
            await self.append_event(
                workspace_id=task.workspace_id,
                task_run_id=task.id,
                event_type="task_step_completed",
                status=TaskRunStatus.RUNNING.value,
                message="Conversation/Playbook execution completed",
                payload={"summary": result_payload.get("summary"), "playbook_run_id": result_payload.get("playbook_run_id")},
                commit=False,
            )
            return await self.complete_task(task=task, output_payload=result_payload)
        except Exception as exc:
            logger.exception("Task run execution failed", extra={"task_run_id": str(task.id), "workspace_id": task.workspace_id})
            return await self.fail_task(task=task, error=str(exc) or exc.__class__.__name__)

    async def resume_waiting_approval_task(self, *, workspace_id: str, task_run_id: UUID) -> TaskRun:
        task = await self.require_task(workspace_id=workspace_id, task_run_id=task_run_id)
        if task.status != TaskRunStatus.WAITING_APPROVAL.value:
            raise ValueError("Only waiting_approval task runs can be resumed")
        approval_id = (task.output_payload or {}).get("approval_id")
        if not approval_id:
            raise ValueError("Task run has no linked approval")
        approval = await ConversationApprovalService(self.session).require_approval(
            workspace_id=workspace_id,
            approval_id=UUID(str(approval_id)),
        )
        if approval.approval_status != ConversationApprovalStatus.APPROVED.value:
            raise ValueError("Linked approval must be approved before resume")
        payload = dict(task.input_payload or {})
        payload["mode"] = "execute_after_approval"
        payload["input"] = {**(payload.get("input") or {}), "approval_id": str(approval.id)}
        if isinstance(payload.get("run_input"), dict):
            run_input = dict(payload["run_input"])
            run_input["mode"] = "execute_after_approval"
            run_input["input"] = {**(run_input.get("input") or {}), "approval_id": str(approval.id)}
            payload["run_input"] = run_input
        task.input_payload = payload
        task.status = TaskRunStatus.QUEUED.value
        flag_modified(task, "input_payload")
        await self.append_event(
            workspace_id=workspace_id,
            task_run_id=task.id,
            event_type="task_resumed",
            status=task.status,
            message="Task run resumed after approval",
            payload={"approval_id": str(approval.id)},
            commit=False,
        )
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def retry_task_by_id(self, *, workspace_id: str, task_run_id: UUID, reason: str | None = "manual retry") -> TaskRun:
        task = await self.require_task(workspace_id=workspace_id, task_run_id=task_run_id)
        return await self.retry_task(task=task, reason=reason)

    async def _execute_payload(self, task: TaskRun) -> dict[str, Any]:
        payload = dict(task.input_payload or {})
        task_type = str(task.task_type)
        if task_type not in {"conversation", "playbook"}:
            raise ValueError(f"Unsupported task_type: {task_type}")
        thread_id_value = payload.get("thread_id") or task.source_id
        if not thread_id_value:
            raise ValueError("Task run requires thread_id/source_id")
        thread_id = UUID(str(thread_id_value))
        run_input = payload.get("run_input") if isinstance(payload.get("run_input"), dict) else payload
        result = await ConversationService(self.session).run_conversation_turn(
            workspace_id=task.workspace_id,
            user_id=task.created_by,
            thread_id=thread_id,
            run_input=run_input,
        )
        return {
            "thread_id": str(result.thread_id),
            "user_message_id": str(result.user_message_id),
            "assistant_message_id": str(result.assistant_message_id),
            "route_name": result.route_name,
            "selected_tool": result.selected_tool,
            "success": result.success,
            "summary": result.summary,
            "result_metadata": result.result_metadata,
            "output": result.output,
            "approval_required": result.approval_required,
            "approval_id": str(result.approval_id) if result.approval_id else None,
            "approval_status": result.approval_status,
            "risk_level": result.risk_level,
            "playbook_run_id": str(result.playbook_run_id) if result.playbook_run_id else None,
            "playbook_name": result.playbook_name,
            "playbook_status": result.playbook_status,
            "events_created": result.events_created,
            "current_step": self._current_step_from_result(result.output),
        }

    async def _link_artifacts(self, *, task: TaskRun) -> None:
        playbook_run_id_value = (task.output_payload or {}).get("playbook_run_id")
        thread_id_value = (task.output_payload or {}).get("thread_id") or task.source_id
        playbook_run_id = UUID(str(playbook_run_id_value)) if playbook_run_id_value else None
        thread_id = UUID(str(thread_id_value)) if thread_id_value else None
        artifacts = await OutputArtifactService(self.session).link_artifacts_to_task_run(
            workspace_id=task.workspace_id,
            task_run_id=task.id,
            playbook_run_id=playbook_run_id,
            thread_id=thread_id,
            commit=False,
        )
        for artifact in artifacts:
            await self.append_event(
                workspace_id=task.workspace_id,
                task_run_id=task.id,
                event_type="artifact_created",
                status=task.status,
                message="Artifact linked to task run",
                payload={"artifact_id": str(artifact.id), "artifact_type": artifact.artifact_type, "title": artifact.title},
                commit=False,
            )

    def _summary_from_output(self, output: dict[str, Any] | None) -> str | None:
        if not output:
            return None
        return output.get("summary") or output.get("playbook_status") or output.get("route_name")

    def _current_step_from_result(self, output: dict[str, Any] | None) -> int:
        if not output:
            return 0
        steps = output.get("steps") or output.get("output", {}).get("steps")
        if isinstance(steps, list):
            return len([step for step in steps if step.get("status") in {"completed", "failed", "waiting_approval"}])
        return 0
