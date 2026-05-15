"""Task scheduler persistence, recovery, and diagnostics services."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.models.enums import TaskRunStatus, TaskSchedulerStatus
from app.models.task_run import TaskRun, TaskRunEvent, TaskSchedulerState
from app.task_orchestration.retry_policy import TaskRetryPolicy
from app.task_orchestration.service import TaskOrchestratorService


class TaskRecoveryService:
    """Recover scheduled, retrying, and stuck in-process task runs."""

    TERMINAL_STATUSES = {
        TaskRunStatus.COMPLETED.value,
        TaskRunStatus.FAILED.value,
        TaskRunStatus.CANCELLED.value,
        TaskRunStatus.EXPIRED.value,
    }

    def __init__(
        self,
        session: AsyncSession,
        *,
        scheduler_name: str = "api-in-process-task-scheduler",
        lease_seconds: int = 120,
        stuck_timeout_seconds: int = 300,
        retry_policy: TaskRetryPolicy | None = None,
    ) -> None:
        self.session = session
        self.scheduler_name = scheduler_name
        self.lease_seconds = lease_seconds
        self.stuck_timeout_seconds = stuck_timeout_seconds
        self.retry_policy = retry_policy or TaskRetryPolicy()

    async def get_scheduler_state(self, *, workspace_id: str, create: bool = True) -> TaskSchedulerState | None:
        statement = select(TaskSchedulerState).where(
            TaskSchedulerState.workspace_id == workspace_id,
            TaskSchedulerState.scheduler_name == self.scheduler_name,
        )
        result = await self.session.execute(statement)
        state = result.scalars().first()
        if state is None and create:
            now = datetime.now(UTC)
            state = TaskSchedulerState(
                workspace_id=workspace_id,
                scheduler_name=self.scheduler_name,
                status=TaskSchedulerStatus.ACTIVE.value,
                heartbeat_at=now,
                last_scan_at=None,
                active_task_count=0,
                recovered_task_count=0,
                scheduler_metadata={
                    "type": "in_process",
                    "not_celery": True,
                    "not_kubernetes": True,
                    "not_production_ha": True,
                },
            )
            self.session.add(state)
            await self.session.flush()
        return state

    async def heartbeat_scheduler(self, *, workspace_id: str, status: str = TaskSchedulerStatus.ACTIVE.value) -> TaskSchedulerState:
        state = await self.get_scheduler_state(workspace_id=workspace_id, create=True)
        assert state is not None
        state.status = status
        state.heartbeat_at = datetime.now(UTC)
        state.active_task_count = await self._active_task_count(workspace_id=workspace_id)
        await self.session.flush()
        return state

    async def recover_scheduled_tasks(self, *, workspace_id: str | None = None) -> int:
        now = datetime.now(UTC)
        statement = select(TaskRun).where(TaskRun.status == TaskRunStatus.PENDING.value, TaskRun.scheduled_at <= now)
        if workspace_id is not None:
            statement = statement.where(TaskRun.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        tasks = list(result.scalars().all())
        orchestrator = TaskOrchestratorService(self.session, retry_policy=self.retry_policy, lease_seconds=self.lease_seconds)
        for task in tasks:
            task.status = TaskRunStatus.QUEUED.value
            task.recovery_count += 1
            task.last_recovered_at = now
            task.recovery_reason = "scheduled task due"
            task.recoverable = False
            await orchestrator.append_event(
                workspace_id=task.workspace_id,
                task_run_id=task.id,
                event_type="task_queued",
                status=task.status,
                message="Scheduled task is due and has been queued",
                payload={"scheduled_at": task.scheduled_at.isoformat() if task.scheduled_at else None},
                commit=False,
            )
        return len(tasks)

    async def recover_retrying_tasks(self, *, workspace_id: str | None = None) -> int:
        now = datetime.now(UTC)
        statement = select(TaskRun).where(TaskRun.status == TaskRunStatus.RETRYING.value, TaskRun.scheduled_at <= now)
        if workspace_id is not None:
            statement = statement.where(TaskRun.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        tasks = list(result.scalars().all())
        orchestrator = TaskOrchestratorService(self.session, retry_policy=self.retry_policy, lease_seconds=self.lease_seconds)
        for task in tasks:
            task.status = TaskRunStatus.QUEUED.value
            task.recovery_count += 1
            task.last_recovered_at = now
            task.recovery_reason = "retry delay elapsed"
            await orchestrator.append_event(
                workspace_id=task.workspace_id,
                task_run_id=task.id,
                event_type="task_retry_started",
                status=task.status,
                message="Retry delay elapsed; task has been re-queued",
                payload={"retry_count": task.retry_count},
                commit=False,
            )
        return len(tasks)

    async def recover_expired_leases(self, *, workspace_id: str | None = None) -> int:
        now = datetime.now(UTC)
        statement = select(TaskRun).where(
            TaskRun.status == TaskRunStatus.RUNNING.value,
            or_(TaskRun.lease_expires_at.is_(None), TaskRun.lease_expires_at <= now),
        )
        if workspace_id is not None:
            statement = statement.where(TaskRun.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        return await self._recover_running_tasks(list(result.scalars().all()), reason="task lease expired")

    async def recover_stuck_running_tasks(self, *, workspace_id: str | None = None) -> int:
        cutoff = datetime.now(UTC) - timedelta(seconds=self.stuck_timeout_seconds)
        statement = select(TaskRun).where(
            TaskRun.status == TaskRunStatus.RUNNING.value,
            or_(TaskRun.heartbeat_at.is_(None), TaskRun.heartbeat_at <= cutoff),
        )
        if workspace_id is not None:
            statement = statement.where(TaskRun.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        return await self._recover_running_tasks(list(result.scalars().all()), reason="task heartbeat stale")

    async def scan_once(self, *, workspace_id: str | None = None) -> dict[str, int]:
        """Run one persistence/recovery scan."""

        details = {
            "scheduled_recovered": await self.recover_scheduled_tasks(workspace_id=workspace_id),
            "retrying_recovered": await self.recover_retrying_tasks(workspace_id=workspace_id),
            "expired_leases_recovered": await self.recover_expired_leases(workspace_id=workspace_id),
            "stuck_running_recovered": await self.recover_stuck_running_tasks(workspace_id=workspace_id),
        }
        recovered_count = sum(details.values())
        workspaces = [workspace_id] if workspace_id else await self._workspace_ids()
        for current_workspace in workspaces:
            state = await self.get_scheduler_state(workspace_id=current_workspace, create=True)
            assert state is not None
            state.status = TaskSchedulerStatus.ACTIVE.value
            state.heartbeat_at = datetime.now(UTC)
            state.last_scan_at = state.heartbeat_at
            state.active_task_count = await self._active_task_count(workspace_id=current_workspace)
            state.recovered_task_count += recovered_count if workspace_id else await self._recent_recovery_count(current_workspace)
            state.scheduler_metadata = {
                **(state.scheduler_metadata or {}),
                "last_scan_details": details,
                "not_celery": True,
                "not_kubernetes": True,
                "not_production_ha": True,
            }
            flag_modified(state, "scheduler_metadata")
        await self.session.commit()
        return details

    async def mark_executor_degraded(self, *, workspace_id: str, error_message: str) -> TaskSchedulerState:
        state = await self.get_scheduler_state(workspace_id=workspace_id, create=True)
        assert state is not None
        state.status = TaskSchedulerStatus.DEGRADED.value
        state.heartbeat_at = datetime.now(UTC)
        state.scheduler_metadata = {**(state.scheduler_metadata or {}), "error_message": error_message}
        flag_modified(state, "scheduler_metadata")
        await self.session.commit()
        await self.session.refresh(state)
        return state

    async def release_executor_leases(self) -> int:
        """Best-effort release of leases owned by this in-process executor."""

        result = await self.session.execute(
            select(TaskRun).where(TaskRun.status == TaskRunStatus.RUNNING.value, TaskRun.lease_owner == self.scheduler_name)
        )
        tasks = list(result.scalars().all())
        orchestrator = TaskOrchestratorService(self.session, retry_policy=self.retry_policy, lease_seconds=self.lease_seconds)
        for task in tasks:
            task.lease_owner = None
            task.lease_token = None
            task.lease_expires_at = None
            task.heartbeat_at = None
            await orchestrator.append_event(
                workspace_id=task.workspace_id,
                task_run_id=task.id,
                event_type="task_lease_released",
                status=task.status,
                message="Executor shutdown released task lease",
                payload={"scheduler_name": self.scheduler_name},
                commit=False,
            )
        if tasks:
            await self.session.commit()
        return len(tasks)

    async def recover_task_by_id(self, *, workspace_id: str, task_run_id: UUID, reason: str = "manual recovery") -> TaskRun:
        orchestrator = TaskOrchestratorService(self.session, retry_policy=self.retry_policy, lease_seconds=self.lease_seconds)
        task = await orchestrator.require_task(workspace_id=workspace_id, task_run_id=task_run_id)
        if task.status in self.TERMINAL_STATUSES and task.status != TaskRunStatus.FAILED.value:
            raise ValueError("Completed, cancelled, or expired tasks cannot be recovered")
        if task.status == TaskRunStatus.WAITING_APPROVAL.value:
            raise ValueError("Waiting approval tasks must be resumed through approval flow")
        if task.status == TaskRunStatus.FAILED.value:
            task.recovery_count += 1
            task.last_recovered_at = datetime.now(UTC)
            task.recovery_reason = reason
            return await orchestrator.retry_task(task=task, reason=reason)
        if task.status == TaskRunStatus.RUNNING.value:
            await self._recover_running_tasks([task], reason=reason)
        else:
            task.status = TaskRunStatus.QUEUED.value
            task.recovery_count += 1
            task.last_recovered_at = datetime.now(UTC)
            task.recovery_reason = reason
            await orchestrator.append_event(
                workspace_id=workspace_id,
                task_run_id=task.id,
                event_type="task_recovered",
                status=task.status,
                message="Task run manually recovered and queued",
                payload={"reason": reason},
                commit=False,
            )
            await self.session.commit()
        await self.session.refresh(task)
        return task

    async def diagnostics_for_task(self, *, task: TaskRun) -> dict[str, Any]:
        now = datetime.now(UTC)
        event_statement = (
            select(TaskRunEvent)
            .where(TaskRunEvent.workspace_id == task.workspace_id, TaskRunEvent.task_run_id == task.id)
            .order_by(TaskRunEvent.created_at.desc())
            .limit(1)
        )
        result = await self.session.execute(event_statement)
        event = result.scalar_one_or_none()
        error = task.error or task.failure_reason or (event.error if event else None)
        recoverable = (
            task.status in {TaskRunStatus.FAILED.value, TaskRunStatus.RETRYING.value, TaskRunStatus.RUNNING.value}
            and self.retry_policy.should_retry(error=error, retry_count=task.retry_count, max_retries=task.max_retries)
        )
        if task.status == TaskRunStatus.WAITING_APPROVAL.value:
            recoverable = False
        effective_recoverable = bool(task.recoverable or recoverable)
        return {
            "task_run_id": task.id,
            "status": task.status,
            "failure_category": task.failure_category or self.retry_policy.category_for_error(error),
            "failure_reason": task.failure_reason or error,
            "recoverable": effective_recoverable,
            "suggested_action": task.suggested_action
            or self.retry_policy.suggested_action_for_error(error=error, recoverable=effective_recoverable),
            "last_event_summary": task.last_event_summary or (event.message if event else None),
            "lease_expired": bool(
                task.status == TaskRunStatus.RUNNING.value
                and (task.lease_expires_at is None or self._datetime_due(task.lease_expires_at, now))
            ),
            "scheduled_due": bool(
                task.scheduled_at is not None
                and self._datetime_due(task.scheduled_at, now)
                and task.status in {TaskRunStatus.PENDING.value, TaskRunStatus.RETRYING.value}
            ),
            "retry_count": task.retry_count,
            "max_retries": task.max_retries,
        }

    async def _recover_running_tasks(self, tasks: list[TaskRun], *, reason: str) -> int:
        orchestrator = TaskOrchestratorService(self.session, retry_policy=self.retry_policy, lease_seconds=self.lease_seconds)
        recovered = 0
        for task in tasks:
            if task.status != TaskRunStatus.RUNNING.value:
                continue
            task.recovery_count += 1
            task.last_recovered_at = datetime.now(UTC)
            task.recovery_reason = reason
            task.lease_owner = None
            task.lease_token = None
            task.lease_expires_at = None
            task.heartbeat_at = None
            if task.retry_count < task.max_retries:
                await orchestrator.retry_task(task=task, reason=reason, commit=False)
                await orchestrator.append_event(
                    workspace_id=task.workspace_id,
                    task_run_id=task.id,
                    event_type="task_recovered",
                    status=task.status,
                    message="Running task recovered and scheduled for retry",
                    payload={"reason": reason, "recovery_count": task.recovery_count},
                    commit=False,
                )
            else:
                task.status = TaskRunStatus.FAILED.value
                task.failed_at = datetime.now(UTC)
                task.error = reason
                task.failure_category = self.retry_policy.category_for_error(reason)
                task.failure_reason = reason
                task.recoverable = False
                task.suggested_action = self.retry_policy.suggested_action_for_error(error=reason, recoverable=False)
                await orchestrator.append_event(
                    workspace_id=task.workspace_id,
                    task_run_id=task.id,
                    event_type="task_failed",
                    status=task.status,
                    message="Running task exceeded retry budget during recovery",
                    error=reason,
                    payload={"recovery_count": task.recovery_count},
                    commit=False,
                )
            recovered += 1
        return recovered

    async def _active_task_count(self, *, workspace_id: str) -> int:
        statement = select(func.count()).select_from(TaskRun).where(
            TaskRun.workspace_id == workspace_id,
            TaskRun.status.in_([TaskRunStatus.RUNNING.value, TaskRunStatus.QUEUED.value, TaskRunStatus.RETRYING.value]),
        )
        result = await self.session.execute(statement)
        return int(result.scalar_one())

    async def _workspace_ids(self) -> list[str]:
        result = await self.session.execute(select(TaskRun.workspace_id).distinct())
        return [str(item) for item in result.scalars().all()]

    async def _recent_recovery_count(self, workspace_id: str) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(TaskRun).where(TaskRun.workspace_id == workspace_id, TaskRun.recovery_count > 0)
        )
        return int(result.scalar_one())

    def _datetime_due(self, value: datetime, now: datetime) -> bool:
        """Compare datetimes safely across Postgres and SQLite test backends."""

        if value.tzinfo is None and now.tzinfo is not None:
            value = value.replace(tzinfo=UTC)
        if value.tzinfo is not None and now.tzinfo is None:
            now = now.replace(tzinfo=UTC)
        return value <= now
