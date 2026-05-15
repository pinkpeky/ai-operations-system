"""Workflow state and agent memory snapshot service."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.conversation.repositories import ConversationRuntimeRepository
from app.models.enums import (
    AgentMemorySnapshotType,
    WorkflowCheckpointType,
    WorkflowRunStatus,
    WorkflowStepStatus,
)
from app.models.workflow import AgentMemorySnapshot, WorkflowCheckpoint, WorkflowRun, WorkflowStep


class WorkflowStateService:
    """Workspace-scoped workflow state, checkpoints, and memory snapshots."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.conversation_repository = ConversationRuntimeRepository(session)

    async def create_workflow_run(
        self,
        *,
        workspace_id: str,
        source_type: str,
        source_id: str | None = None,
        conversation_thread_id: UUID | None = None,
        playbook_run_id: UUID | None = None,
        task_run_id: UUID | None = None,
        status: str = WorkflowRunStatus.PENDING.value,
        variables: dict[str, Any] | None = None,
        context: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowRun:
        """Create a workflow run without replacing existing execution systems."""

        self._validate_workflow_status(status)
        now = datetime.now(UTC)
        workflow = WorkflowRun(
            workspace_id=workspace_id,
            source_type=source_type,
            source_id=source_id,
            conversation_thread_id=conversation_thread_id,
            playbook_run_id=playbook_run_id,
            task_run_id=task_run_id,
            status=status,
            variables=variables or {},
            context=context or {},
            checkpoints=[],
            workflow_metadata=metadata or {},
            started_at=now if status == WorkflowRunStatus.RUNNING.value else None,
        )
        self.session.add(workflow)
        await self.session.flush()
        await self._append_conversation_event(
            workflow,
            event_type="workflow_run_created",
            message="Workflow run created",
            payload={"workflow_run_id": str(workflow.id), "source_type": source_type, "source_id": source_id},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def get_workflow_run(self, *, workspace_id: str, workflow_run_id: UUID) -> WorkflowRun | None:
        statement = select(WorkflowRun).where(WorkflowRun.workspace_id == workspace_id, WorkflowRun.id == workflow_run_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def require_workflow_run(self, *, workspace_id: str, workflow_run_id: UUID) -> WorkflowRun:
        workflow = await self.get_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        if workflow is None:
            raise ValueError("Workflow run not found in workspace")
        return workflow

    async def list_workflow_runs(
        self,
        *,
        workspace_id: str,
        status: str | None = None,
        source_type: str | None = None,
        conversation_thread_id: UUID | None = None,
        playbook_run_id: UUID | None = None,
        task_run_id: UUID | None = None,
        limit: int = 100,
    ) -> list[WorkflowRun]:
        statement = select(WorkflowRun).where(WorkflowRun.workspace_id == workspace_id)
        if status is not None:
            statement = statement.where(WorkflowRun.status == status)
        if source_type is not None:
            statement = statement.where(WorkflowRun.source_type == source_type)
        if conversation_thread_id is not None:
            statement = statement.where(WorkflowRun.conversation_thread_id == conversation_thread_id)
        if playbook_run_id is not None:
            statement = statement.where(WorkflowRun.playbook_run_id == playbook_run_id)
        if task_run_id is not None:
            statement = statement.where(WorkflowRun.task_run_id == task_run_id)
        result = await self.session.execute(statement.order_by(WorkflowRun.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def update_variables(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        variables: dict[str, Any],
        merge: bool = True,
        commit: bool = True,
    ) -> WorkflowRun:
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        workflow.variables = {**(workflow.variables or {}), **variables} if merge else variables
        flag_modified(workflow, "variables")
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def update_context(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        context: dict[str, Any],
        merge: bool = True,
        commit: bool = True,
    ) -> WorkflowRun:
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        workflow.context = {**(workflow.context or {}), **context} if merge else context
        flag_modified(workflow, "context")
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def start_step(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        step_index: int,
        step_name: str,
        step_type: str,
        input_payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowStep:
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        now = datetime.now(UTC)
        workflow.status = WorkflowRunStatus.RUNNING.value
        workflow.started_at = workflow.started_at or now
        workflow.current_step = step_index
        step = WorkflowStep(
            workspace_id=workspace_id,
            workflow_run_id=workflow.id,
            step_index=step_index,
            step_name=step_name[:255],
            step_type=step_type,
            status=WorkflowStepStatus.RUNNING.value,
            input_payload=input_payload or {},
            output_payload={},
            step_metadata=metadata or {},
            started_at=now,
        )
        self.session.add(step)
        await self.session.flush()
        await self._append_conversation_event(
            workflow,
            event_type="workflow_step_started",
            message=f"Workflow step started: {step.step_name}",
            payload={"workflow_run_id": str(workflow.id), "workflow_step_id": str(step.id), "step_index": step_index},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(step)
        return step

    async def complete_step(
        self,
        *,
        workspace_id: str,
        workflow_step_id: UUID,
        output_payload: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowStep:
        step = await self.require_step(workspace_id=workspace_id, workflow_step_id=workflow_step_id)
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=step.workflow_run_id)
        now = datetime.now(UTC)
        step.status = WorkflowStepStatus.COMPLETED.value
        step.completed_at = now
        step.output_payload = output_payload or {}
        if step.started_at is not None:
            step.duration_ms = self._duration_ms(started_at=step.started_at, completed_at=now)
        if metadata:
            step.step_metadata = {**(step.step_metadata or {}), **metadata}
        flag_modified(step, "output_payload")
        flag_modified(step, "step_metadata")
        workflow.current_step = max(workflow.current_step, step.step_index + 1)
        await self._append_conversation_event(
            workflow,
            event_type="workflow_step_completed",
            message=f"Workflow step completed: {step.step_name}",
            payload={"workflow_run_id": str(workflow.id), "workflow_step_id": str(step.id), "step_index": step.step_index},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(step)
        return step

    async def fail_step(
        self,
        *,
        workspace_id: str,
        workflow_step_id: UUID,
        error: str,
        output_payload: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowStep:
        step = await self.require_step(workspace_id=workspace_id, workflow_step_id=workflow_step_id)
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=step.workflow_run_id)
        now = datetime.now(UTC)
        step.status = WorkflowStepStatus.FAILED.value
        step.error = error
        step.completed_at = now
        step.output_payload = output_payload or {}
        if step.started_at is not None:
            step.duration_ms = self._duration_ms(started_at=step.started_at, completed_at=now)
        flag_modified(step, "output_payload")
        await self._append_conversation_event(
            workflow,
            event_type="workflow_step_failed",
            message=f"Workflow step failed: {step.step_name}",
            payload={"workflow_run_id": str(workflow.id), "workflow_step_id": str(step.id), "error": error},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(step)
        return step

    async def pause_workflow(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        reason: str | None = None,
        waiting_approval: bool = False,
        commit: bool = True,
    ) -> WorkflowRun:
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        workflow.status = WorkflowRunStatus.WAITING_APPROVAL.value if waiting_approval else WorkflowRunStatus.PAUSED.value
        workflow.paused_at = datetime.now(UTC)
        await self._append_conversation_event(
            workflow,
            event_type="workflow_paused",
            message=reason or "Workflow paused",
            payload={"workflow_run_id": str(workflow.id), "status": workflow.status},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def resume_workflow(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        reason: str | None = None,
        commit: bool = True,
    ) -> WorkflowRun:
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        workflow.status = WorkflowRunStatus.RUNNING.value
        workflow.resumed_at = datetime.now(UTC)
        await self._append_conversation_event(
            workflow,
            event_type="workflow_resumed",
            message=reason or "Workflow resumed",
            payload={"workflow_run_id": str(workflow.id)},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def complete_workflow(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        output: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowRun:
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        workflow.status = WorkflowRunStatus.COMPLETED.value
        workflow.completed_at = datetime.now(UTC)
        if output:
            workflow.context = {**(workflow.context or {}), "final_output": output}
            flag_modified(workflow, "context")
        await self._append_conversation_event(
            workflow,
            event_type="workflow_completed",
            message="Workflow completed",
            payload={"workflow_run_id": str(workflow.id)},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def fail_workflow(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        error: str,
        commit: bool = True,
    ) -> WorkflowRun:
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        workflow.status = WorkflowRunStatus.FAILED.value
        workflow.failed_at = datetime.now(UTC)
        workflow.context = {**(workflow.context or {}), "error": error}
        flag_modified(workflow, "context")
        await self._append_conversation_event(
            workflow,
            event_type="workflow_failed",
            message="Workflow failed",
            payload={"workflow_run_id": str(workflow.id), "error": error},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def create_checkpoint(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        checkpoint_name: str,
        checkpoint_type: str = WorkflowCheckpointType.AUTO.value,
        state_payload: dict[str, Any] | None = None,
        variables_snapshot: dict[str, Any] | None = None,
        context_snapshot: dict[str, Any] | None = None,
        created_by: str | None = None,
        commit: bool = True,
    ) -> WorkflowCheckpoint:
        self._validate_checkpoint_type(checkpoint_type)
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        checkpoint = WorkflowCheckpoint(
            workspace_id=workspace_id,
            workflow_run_id=workflow.id,
            checkpoint_name=checkpoint_name[:255],
            checkpoint_type=checkpoint_type,
            state_payload=state_payload or {"status": workflow.status, "current_step": workflow.current_step},
            variables_snapshot=variables_snapshot if variables_snapshot is not None else dict(workflow.variables or {}),
            context_snapshot=context_snapshot if context_snapshot is not None else dict(workflow.context or {}),
            created_by=created_by,
        )
        self.session.add(checkpoint)
        await self.session.flush()
        workflow.checkpoints = [
            *(workflow.checkpoints or []),
            {"id": str(checkpoint.id), "name": checkpoint.checkpoint_name, "type": checkpoint.checkpoint_type},
        ]
        flag_modified(workflow, "checkpoints")
        await self._append_conversation_event(
            workflow,
            event_type="workflow_checkpoint_created",
            message=f"Workflow checkpoint created: {checkpoint.checkpoint_name}",
            payload={"workflow_run_id": str(workflow.id), "checkpoint_id": str(checkpoint.id), "checkpoint_type": checkpoint_type},
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(checkpoint)
        return checkpoint

    async def restore_checkpoint(
        self,
        *,
        workspace_id: str,
        checkpoint_id: UUID,
        commit: bool = True,
    ) -> WorkflowRun:
        checkpoint = await self.require_checkpoint(workspace_id=workspace_id, checkpoint_id=checkpoint_id)
        workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=checkpoint.workflow_run_id)
        workflow.variables = dict(checkpoint.variables_snapshot or {})
        workflow.context = dict(checkpoint.context_snapshot or {})
        workflow.status = WorkflowRunStatus.PAUSED.value
        workflow.paused_at = datetime.now(UTC)
        flag_modified(workflow, "variables")
        flag_modified(workflow, "context")
        await self.create_checkpoint(
            workspace_id=workspace_id,
            workflow_run_id=workflow.id,
            checkpoint_name=f"restore:{checkpoint.checkpoint_name}",
            checkpoint_type=WorkflowCheckpointType.RESUME.value,
            state_payload={"restored_from_checkpoint_id": str(checkpoint.id)},
            created_by="WorkflowStateService",
            commit=False,
        )
        if commit:
            await self.session.commit()
            await self.session.refresh(workflow)
        return workflow

    async def create_memory_snapshot(
        self,
        *,
        workspace_id: str,
        memory_type: str,
        summary: str | None = None,
        memory_payload: dict[str, Any] | None = None,
        workflow_run_id: UUID | None = None,
        conversation_thread_id: UUID | None = None,
        task_run_id: UUID | None = None,
        source_event_ids: list[str] | None = None,
        source_artifact_ids: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> AgentMemorySnapshot:
        self._validate_memory_type(memory_type)
        workflow: WorkflowRun | None = None
        if workflow_run_id is not None:
            workflow = await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
            conversation_thread_id = conversation_thread_id or workflow.conversation_thread_id
            task_run_id = task_run_id or workflow.task_run_id
        snapshot = AgentMemorySnapshot(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            conversation_thread_id=conversation_thread_id,
            task_run_id=task_run_id,
            memory_type=memory_type,
            summary=summary,
            memory_payload=memory_payload or {},
            source_event_ids=source_event_ids or [],
            source_artifact_ids=source_artifact_ids or [],
            snapshot_metadata=metadata or {},
        )
        self.session.add(snapshot)
        await self.session.flush()
        if workflow is not None:
            await self._append_conversation_event(
                workflow,
                event_type="memory_snapshot_created",
                message=f"Agent memory snapshot created: {memory_type}",
                payload={"workflow_run_id": str(workflow.id), "memory_snapshot_id": str(snapshot.id), "memory_type": memory_type},
            )
        elif conversation_thread_id is not None:
            await self.conversation_repository.append_event(
                workspace_id=workspace_id,
                thread_id=conversation_thread_id,
                event_type="memory_snapshot_created",
                message=f"Agent memory snapshot created: {memory_type}",
                payload={"memory_snapshot_id": str(snapshot.id), "memory_type": memory_type},
            )
        if commit:
            await self.session.commit()
            await self.session.refresh(snapshot)
        return snapshot

    async def list_steps(self, *, workspace_id: str, workflow_run_id: UUID, limit: int = 300) -> list[WorkflowStep]:
        await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        result = await self.session.execute(
            select(WorkflowStep)
            .where(WorkflowStep.workspace_id == workspace_id, WorkflowStep.workflow_run_id == workflow_run_id)
            .order_by(WorkflowStep.step_index.asc(), WorkflowStep.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_checkpoints(self, *, workspace_id: str, workflow_run_id: UUID, limit: int = 300) -> list[WorkflowCheckpoint]:
        await self.require_workflow_run(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        result = await self.session.execute(
            select(WorkflowCheckpoint)
            .where(WorkflowCheckpoint.workspace_id == workspace_id, WorkflowCheckpoint.workflow_run_id == workflow_run_id)
            .order_by(WorkflowCheckpoint.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def list_memory_snapshots(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID | None = None,
        conversation_thread_id: UUID | None = None,
        task_run_id: UUID | None = None,
        memory_type: str | None = None,
        limit: int = 300,
    ) -> list[AgentMemorySnapshot]:
        statement = select(AgentMemorySnapshot).where(AgentMemorySnapshot.workspace_id == workspace_id)
        if workflow_run_id is not None:
            statement = statement.where(AgentMemorySnapshot.workflow_run_id == workflow_run_id)
        if conversation_thread_id is not None:
            statement = statement.where(AgentMemorySnapshot.conversation_thread_id == conversation_thread_id)
        if task_run_id is not None:
            statement = statement.where(AgentMemorySnapshot.task_run_id == task_run_id)
        if memory_type is not None:
            statement = statement.where(AgentMemorySnapshot.memory_type == memory_type)
        result = await self.session.execute(statement.order_by(AgentMemorySnapshot.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def require_step(self, *, workspace_id: str, workflow_step_id: UUID) -> WorkflowStep:
        result = await self.session.execute(
            select(WorkflowStep).where(WorkflowStep.workspace_id == workspace_id, WorkflowStep.id == workflow_step_id)
        )
        step = result.scalar_one_or_none()
        if step is None:
            raise ValueError("Workflow step not found in workspace")
        return step

    async def require_checkpoint(self, *, workspace_id: str, checkpoint_id: UUID) -> WorkflowCheckpoint:
        result = await self.session.execute(
            select(WorkflowCheckpoint).where(WorkflowCheckpoint.workspace_id == workspace_id, WorkflowCheckpoint.id == checkpoint_id)
        )
        checkpoint = result.scalar_one_or_none()
        if checkpoint is None:
            raise ValueError("Workflow checkpoint not found in workspace")
        return checkpoint

    async def _append_conversation_event(
        self,
        workflow: WorkflowRun,
        *,
        event_type: str,
        message: str,
        payload: dict[str, Any] | None = None,
    ) -> None:
        if workflow.conversation_thread_id is None:
            return
        await self.conversation_repository.append_event(
            workspace_id=workflow.workspace_id,
            thread_id=workflow.conversation_thread_id,
            event_type=event_type,
            message=message,
            payload=payload or {},
        )

    def _validate_workflow_status(self, status: str) -> None:
        if status not in {item.value for item in WorkflowRunStatus}:
            raise ValueError("Invalid workflow run status")

    def _validate_checkpoint_type(self, checkpoint_type: str) -> None:
        if checkpoint_type not in {item.value for item in WorkflowCheckpointType}:
            raise ValueError("Invalid workflow checkpoint type")

    def _validate_memory_type(self, memory_type: str) -> None:
        if memory_type not in {item.value for item in AgentMemorySnapshotType}:
            raise ValueError("Invalid agent memory snapshot type")

    def _duration_ms(self, *, started_at: datetime, completed_at: datetime) -> int:
        if started_at.tzinfo is None and completed_at.tzinfo is not None:
            started_at = started_at.replace(tzinfo=completed_at.tzinfo)
        elif started_at.tzinfo is not None and completed_at.tzinfo is None:
            completed_at = completed_at.replace(tzinfo=started_at.tzinfo)
        return int((completed_at - started_at).total_seconds() * 1000)
