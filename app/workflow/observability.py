"""Workflow execution trace, diagnostics, analytics, and replay center services."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import (
    OutputArtifactStatus,
    WorkflowDiagnosticSeverity,
    WorkflowReplayMode,
    WorkflowReplaySessionStatus,
    WorkflowRunStatus,
    WorkflowTraceEventType,
)
from app.models.output_artifact import OutputArtifact
from app.models.workflow import (
    WorkflowCheckpoint,
    WorkflowExecutionTrace,
    WorkflowReplaySession,
    WorkflowRuntimeDiagnostic,
    WorkflowRun,
    WorkflowStep,
)
from app.workflow.planner import WorkflowPlannerResult


class WorkflowExecutionTraceService:
    """Best-effort trace writer for workflow runtime observability."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_trace(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        event_type: str,
        workflow_step_id: UUID | None = None,
        node_key: str | None = None,
        execution_phase: str | None = None,
        status: str | None = None,
        input_snapshot: dict[str, Any] | None = None,
        output_snapshot: dict[str, Any] | None = None,
        planner_snapshot: dict[str, Any] | None = None,
        retry_count: int = 0,
        fallback_triggered: bool = False,
        duration_ms: int | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowExecutionTrace:
        trace = WorkflowExecutionTrace(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            workflow_step_id=workflow_step_id,
            node_key=node_key,
            event_type=event_type,
            execution_phase=execution_phase,
            status=status,
            input_snapshot=input_snapshot or {},
            output_snapshot=output_snapshot or {},
            planner_snapshot=planner_snapshot or {},
            retry_count=retry_count,
            fallback_triggered=fallback_triggered,
            duration_ms=duration_ms,
            trace_metadata=metadata or {},
        )
        self.session.add(trace)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(trace)
        return trace

    async def list_traces(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        node_key: str | None = None,
        event_type: str | None = None,
        limit: int = 500,
    ) -> list[WorkflowExecutionTrace]:
        statement = select(WorkflowExecutionTrace).where(
            WorkflowExecutionTrace.workspace_id == workspace_id,
            WorkflowExecutionTrace.workflow_run_id == workflow_run_id,
        )
        if node_key is not None:
            statement = statement.where(WorkflowExecutionTrace.node_key == node_key)
        if event_type is not None:
            statement = statement.where(WorkflowExecutionTrace.event_type == event_type)
        result = await self.session.execute(statement.order_by(WorkflowExecutionTrace.created_at.asc()).limit(limit))
        return list(result.scalars().all())

    async def trace_node_start(self, *, workflow: WorkflowRun, step: WorkflowStep, commit: bool = False) -> WorkflowExecutionTrace:
        return await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            workflow_step_id=step.id,
            node_key=step.node_key,
            event_type=WorkflowTraceEventType.NODE_STARTED.value,
            execution_phase=step.step_type,
            status=step.status,
            input_snapshot=step.input_payload,
            metadata={"step_index": step.step_index, "step_name": step.step_name},
            commit=commit,
        )

    async def trace_node_complete(
        self,
        *,
        workflow: WorkflowRun,
        step: WorkflowStep,
        planner_result: WorkflowPlannerResult | None = None,
        commit: bool = False,
    ) -> WorkflowExecutionTrace:
        return await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            workflow_step_id=step.id,
            node_key=step.node_key,
            event_type=WorkflowTraceEventType.NODE_COMPLETED.value,
            execution_phase=step.step_type,
            status=step.status,
            input_snapshot=step.input_payload,
            output_snapshot=step.output_payload,
            planner_snapshot=planner_result.as_dict() if planner_result is not None else {},
            retry_count=self._retry_count(workflow),
            fallback_triggered=self._fallback_triggered(workflow),
            duration_ms=step.duration_ms,
            metadata={"step_index": step.step_index, "step_name": step.step_name},
            commit=commit,
        )

    async def trace_node_failure(
        self,
        *,
        workflow: WorkflowRun,
        step: WorkflowStep,
        planner_result: WorkflowPlannerResult | None = None,
        error: str | None = None,
        commit: bool = False,
    ) -> WorkflowExecutionTrace:
        return await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            workflow_step_id=step.id,
            node_key=step.node_key,
            event_type=WorkflowTraceEventType.NODE_FAILED.value,
            execution_phase=step.step_type,
            status=step.status,
            input_snapshot=step.input_payload,
            output_snapshot=step.output_payload,
            planner_snapshot=planner_result.as_dict() if planner_result is not None else {},
            retry_count=self._retry_count(workflow),
            fallback_triggered=self._fallback_triggered(workflow),
            duration_ms=step.duration_ms,
            metadata={"step_index": step.step_index, "step_name": step.step_name, "error": error or step.error},
            commit=commit,
        )

    async def trace_retry(self, *, workflow: WorkflowRun, node_key: str | None, retry_count: int, commit: bool = False) -> None:
        await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            node_key=node_key,
            event_type=WorkflowTraceEventType.RETRY_TRIGGERED.value,
            execution_phase="planner",
            status=workflow.status,
            retry_count=retry_count,
            planner_snapshot={"retry_state": workflow.retry_state or {}},
            commit=commit,
        )

    async def trace_fallback(self, *, workflow: WorkflowRun, node_key: str | None, commit: bool = False) -> None:
        await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            node_key=node_key,
            event_type=WorkflowTraceEventType.FALLBACK_TRIGGERED.value,
            execution_phase="planner",
            status=workflow.status,
            fallback_triggered=True,
            planner_snapshot={"fallback_state": workflow.fallback_state or {}},
            commit=commit,
        )

    async def trace_planner_decision(
        self,
        *,
        workflow: WorkflowRun,
        planner_result: WorkflowPlannerResult | None,
        node_key: str | None = None,
        commit: bool = False,
    ) -> None:
        await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            node_key=node_key or workflow.current_node_key,
            event_type=WorkflowTraceEventType.PLANNER_DECISION.value,
            execution_phase="planner",
            status=workflow.status,
            planner_snapshot=planner_result.as_dict() if planner_result is not None else {},
            retry_count=self._retry_count(workflow),
            fallback_triggered=self._fallback_triggered(workflow),
            commit=commit,
        )

    async def trace_approval_wait(self, *, workflow: WorkflowRun, node_key: str | None = None, commit: bool = False) -> None:
        await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            node_key=node_key or workflow.current_node_key,
            event_type=WorkflowTraceEventType.APPROVAL_WAIT.value,
            execution_phase="approval",
            status=workflow.status,
            metadata={"paused_at": workflow.paused_at.isoformat() if workflow.paused_at else None},
            commit=commit,
        )

    async def trace_replay(
        self,
        *,
        workflow: WorkflowRun,
        replay_session: WorkflowReplaySession | None = None,
        event_type: str = WorkflowTraceEventType.REPLAY_STARTED.value,
        commit: bool = False,
    ) -> None:
        await self.create_trace(
            workspace_id=workflow.workspace_id,
            workflow_run_id=workflow.id,
            node_key=replay_session.replay_source_node_key if replay_session else workflow.current_node_key,
            event_type=event_type,
            execution_phase="replay",
            status=replay_session.replay_status if replay_session else workflow.status,
            metadata={"replay_session_id": str(replay_session.id) if replay_session else None},
            commit=commit,
        )

    async def summarize_trace(self, *, workspace_id: str, workflow_run_id: UUID) -> dict[str, Any]:
        traces = await self.list_traces(workspace_id=workspace_id, workflow_run_id=workflow_run_id, limit=1000)
        by_event: dict[str, int] = {}
        failures: dict[str, int] = {}
        for trace in traces:
            by_event[trace.event_type] = by_event.get(trace.event_type, 0) + 1
            if trace.event_type == WorkflowTraceEventType.NODE_FAILED.value:
                key = trace.node_key or "unknown"
                failures[key] = failures.get(key, 0) + 1
        durations = [trace.duration_ms for trace in traces if trace.duration_ms is not None]
        return {
            "trace_count": len(traces),
            "event_counts": by_event,
            "failure_hotspots": failures,
            "avg_trace_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
            "retry_count": sum(trace.retry_count for trace in traces),
            "fallback_count": len([trace for trace in traces if trace.fallback_triggered]),
        }

    def _retry_count(self, workflow: WorkflowRun) -> int:
        paths = (workflow.retry_state or {}).get("paths") or []
        if not isinstance(paths, list):
            return 0
        return len([item for item in paths if isinstance(item, dict) and item.get("matched")])

    def _fallback_triggered(self, workflow: WorkflowRun) -> bool:
        paths = (workflow.fallback_state or {}).get("paths") or []
        return any(isinstance(item, dict) and bool(item.get("matched")) for item in paths)


class WorkflowDiagnosticsService:
    """Workflow diagnostics, analytics, and Replay Center orchestration."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.traces = WorkflowExecutionTraceService(session)

    async def create_diagnostic(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        diagnostic_type: str,
        severity: str,
        summary: str,
        details: dict[str, Any] | None = None,
        suggested_action: str | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowRuntimeDiagnostic:
        diagnostic = WorkflowRuntimeDiagnostic(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            diagnostic_type=diagnostic_type,
            severity=severity,
            summary=summary[:512],
            details=details or {},
            suggested_action=suggested_action,
            diagnostic_metadata=metadata or {},
        )
        self.session.add(diagnostic)
        await self.session.flush()
        if commit:
            await self.session.commit()
            await self.session.refresh(diagnostic)
        return diagnostic

    async def list_diagnostics(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        severity: str | None = None,
        limit: int = 200,
    ) -> list[WorkflowRuntimeDiagnostic]:
        statement = select(WorkflowRuntimeDiagnostic).where(
            WorkflowRuntimeDiagnostic.workspace_id == workspace_id,
            WorkflowRuntimeDiagnostic.workflow_run_id == workflow_run_id,
        )
        if severity is not None:
            statement = statement.where(WorkflowRuntimeDiagnostic.severity == severity)
        result = await self.session.execute(statement.order_by(WorkflowRuntimeDiagnostic.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def analyze_failed_workflow(self, *, workspace_id: str, workflow_run_id: UUID, commit: bool = True) -> list[WorkflowRuntimeDiagnostic]:
        workflow = await self._require_workflow(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        diagnostics: list[WorkflowRuntimeDiagnostic] = []
        failed_steps = await self._failed_steps(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        if workflow.status == WorkflowRunStatus.FAILED.value or failed_steps:
            diagnostics.append(
                await self.create_diagnostic(
                    workspace_id=workspace_id,
                    workflow_run_id=workflow_run_id,
                    diagnostic_type="workflow_failure",
                    severity=WorkflowDiagnosticSeverity.ERROR.value,
                    summary="Workflow has failed execution state or failed steps",
                    details={"failed_step_count": len(failed_steps), "current_node_key": workflow.current_node_key},
                    suggested_action="Inspect node input/output, latest task events, and create a metadata-only replay session from the nearest checkpoint.",
                    commit=False,
                )
            )
        diagnostics.extend(await self.detect_retry_loop(workspace_id=workspace_id, workflow_run_id=workflow_run_id, commit=False))
        diagnostics.extend(await self.detect_fallback_chain(workspace_id=workspace_id, workflow_run_id=workflow_run_id, commit=False))
        diagnostics.extend(await self.detect_missing_artifacts(workspace_id=workspace_id, workflow_run_id=workflow_run_id, commit=False))
        diagnostics.extend(await self.detect_checkpoint_gap(workspace_id=workspace_id, workflow_run_id=workflow_run_id, commit=False))
        if commit:
            await self.session.commit()
            for item in diagnostics:
                await self.session.refresh(item)
        return diagnostics

    async def detect_retry_loop(self, *, workspace_id: str, workflow_run_id: UUID, commit: bool = True) -> list[WorkflowRuntimeDiagnostic]:
        traces = await self.traces.list_traces(workspace_id=workspace_id, workflow_run_id=workflow_run_id, limit=1000)
        retry_count = len([trace for trace in traces if trace.event_type == WorkflowTraceEventType.RETRY_TRIGGERED.value or trace.retry_count > 0])
        if retry_count < 3:
            return []
        diagnostic = await self.create_diagnostic(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            diagnostic_type="retry_loop",
            severity=WorkflowDiagnosticSeverity.WARNING.value,
            summary="Workflow shows repeated retry signals",
            details={"retry_signal_count": retry_count},
            suggested_action="Review retry policy and node failure output before resuming.",
            commit=commit,
        )
        return [diagnostic]

    async def detect_excessive_runtime(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        threshold_ms: int = 300000,
        commit: bool = True,
    ) -> list[WorkflowRuntimeDiagnostic]:
        workflow = await self._require_workflow(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        runtime_ms = self._workflow_runtime_ms(workflow)
        if runtime_ms <= threshold_ms:
            return []
        diagnostic = await self.create_diagnostic(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            diagnostic_type="excessive_runtime",
            severity=WorkflowDiagnosticSeverity.WARNING.value,
            summary="Workflow runtime exceeded expected threshold",
            details={"runtime_ms": runtime_ms, "threshold_ms": threshold_ms},
            suggested_action="Inspect slow node traces and task lease/heartbeat history.",
            commit=commit,
        )
        return [diagnostic]

    async def detect_fallback_chain(self, *, workspace_id: str, workflow_run_id: UUID, commit: bool = True) -> list[WorkflowRuntimeDiagnostic]:
        traces = await self.traces.list_traces(workspace_id=workspace_id, workflow_run_id=workflow_run_id, limit=1000)
        fallback_count = len([trace for trace in traces if trace.event_type == WorkflowTraceEventType.FALLBACK_TRIGGERED.value or trace.fallback_triggered])
        if fallback_count == 0:
            return []
        diagnostic = await self.create_diagnostic(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            diagnostic_type="fallback_chain",
            severity=WorkflowDiagnosticSeverity.INFO.value,
            summary="Workflow used fallback routing",
            details={"fallback_count": fallback_count},
            suggested_action="Confirm fallback output is acceptable before packaging artifacts.",
            commit=commit,
        )
        return [diagnostic]

    async def detect_missing_artifacts(self, *, workspace_id: str, workflow_run_id: UUID, commit: bool = True) -> list[WorkflowRuntimeDiagnostic]:
        artifact_count = await self._artifact_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        workflow = await self._require_workflow(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        if artifact_count > 0 or workflow.status not in {WorkflowRunStatus.COMPLETED.value, WorkflowRunStatus.FAILED.value}:
            return []
        diagnostic = await self.create_diagnostic(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            diagnostic_type="missing_artifacts",
            severity=WorkflowDiagnosticSeverity.WARNING.value,
            summary="Workflow has no linked output artifacts",
            details={"artifact_count": artifact_count, "status": workflow.status},
            suggested_action="Check artifact pipeline linkage or save relevant messages as artifacts.",
            commit=commit,
        )
        return [diagnostic]

    async def detect_checkpoint_gap(self, *, workspace_id: str, workflow_run_id: UUID, commit: bool = True) -> list[WorkflowRuntimeDiagnostic]:
        checkpoint_count = await self._checkpoint_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        if checkpoint_count > 0:
            return []
        diagnostic = await self.create_diagnostic(
            workspace_id=workspace_id,
            workflow_run_id=workflow_run_id,
            diagnostic_type="checkpoint_gap",
            severity=WorkflowDiagnosticSeverity.INFO.value,
            summary="Workflow has no checkpoints available for replay",
            details={"checkpoint_count": checkpoint_count},
            suggested_action="Create a manual checkpoint before high-risk resume/replay operations.",
            commit=commit,
        )
        return [diagnostic]

    async def generate_runtime_summary(self, *, workspace_id: str, workflow_run_id: UUID) -> dict[str, Any]:
        workflow = await self._require_workflow(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        trace_summary = await self.traces.summarize_trace(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        step_count = await self._step_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        artifact_count = await self._artifact_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        checkpoint_count = await self._checkpoint_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        replay_count = await self._replay_session_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        return {
            "workflow_run_id": str(workflow.id),
            "status": workflow.status,
            "source_type": workflow.source_type,
            "current_node_key": workflow.current_node_key,
            "planned_next_nodes": workflow.planned_next_nodes or [],
            "retry_state": workflow.retry_state or {},
            "fallback_state": workflow.fallback_state or {},
            "runtime_ms": self._workflow_runtime_ms(workflow),
            "step_count": step_count,
            "artifact_count": artifact_count,
            "checkpoint_count": checkpoint_count,
            "replay_session_count": replay_count,
            "trace_summary": trace_summary,
            "recoverability": self._recoverability_hint(workflow),
            "replay_recommendation": "metadata_only replay from latest checkpoint" if checkpoint_count else "create checkpoint before replay",
        }

    async def analytics(self, *, workspace_id: str, workflow_run_id: UUID) -> dict[str, Any]:
        workflow = await self._require_workflow(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        traces = await self.traces.list_traces(workspace_id=workspace_id, workflow_run_id=workflow_run_id, limit=1000)
        durations = [trace.duration_ms for trace in traces if trace.duration_ms is not None]
        fallback_count = len([trace for trace in traces if trace.fallback_triggered])
        approval_wait_count = len([trace for trace in traces if trace.event_type == WorkflowTraceEventType.APPROVAL_WAIT.value])
        replay_count = await self._replay_session_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        artifact_count = await self._artifact_count(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        failure_hotspots: dict[str, int] = {}
        for trace in traces:
            if trace.event_type == WorkflowTraceEventType.NODE_FAILED.value:
                key = trace.node_key or "unknown"
                failure_hotspots[key] = failure_hotspots.get(key, 0) + 1
        success_rate = 1.0 if workflow.status == WorkflowRunStatus.COMPLETED.value else 0.0 if workflow.status == WorkflowRunStatus.FAILED.value else None
        return {
            "workflow_success_rate": success_rate,
            "avg_runtime_ms": self._workflow_runtime_ms(workflow),
            "avg_trace_duration_ms": round(sum(durations) / len(durations), 2) if durations else 0,
            "avg_retries": round(sum(trace.retry_count for trace in traces) / len(traces), 2) if traces else 0,
            "fallback_frequency": fallback_count,
            "approval_wait_frequency": approval_wait_count,
            "replay_frequency": replay_count,
            "artifact_generation_rate": 1.0 if artifact_count else 0.0,
            "artifact_count": artifact_count,
            "node_failure_hotspots": failure_hotspots,
        }

    async def create_replay_session(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID,
        replay_source_checkpoint_id: UUID | None = None,
        replay_source_node_key: str | None = None,
        replay_mode: str = WorkflowReplayMode.METADATA_ONLY.value,
        initiated_by: str | None = None,
        metadata: dict[str, Any] | None = None,
        commit: bool = True,
    ) -> WorkflowReplaySession:
        if replay_mode == WorkflowReplayMode.REPLAY_EXECUTION.value:
            raise ValueError("replay_execution is reserved for future deterministic replay and is not enabled")
        if replay_mode not in {WorkflowReplayMode.DRY_RUN.value, WorkflowReplayMode.METADATA_ONLY.value}:
            raise ValueError("replay_mode must be dry_run or metadata_only")
        workflow = await self._require_workflow(workspace_id=workspace_id, workflow_run_id=workflow_run_id)
        checkpoint_payload: dict[str, Any] = {}
        if replay_source_checkpoint_id is not None:
            checkpoint = await self._require_checkpoint(workspace_id=workspace_id, checkpoint_id=replay_source_checkpoint_id)
            if checkpoint.workflow_run_id != workflow.id:
                raise ValueError("Replay checkpoint does not belong to workflow")
            checkpoint_payload = {
                "checkpoint_name": checkpoint.checkpoint_name,
                "checkpoint_type": checkpoint.checkpoint_type,
                "state_payload": checkpoint.state_payload or {},
            }
        now = datetime.now(UTC)
        replay_session = WorkflowReplaySession(
            workspace_id=workspace_id,
            workflow_run_id=workflow.id,
            replay_source_checkpoint_id=replay_source_checkpoint_id,
            replay_source_node_key=replay_source_node_key or workflow.current_node_key,
            replay_status=WorkflowReplaySessionStatus.COMPLETED.value,
            replay_mode=replay_mode,
            initiated_by=initiated_by,
            replay_metadata={
                **(metadata or {}),
                "workflow_run_id": str(workflow.id),
                "replay_lineage": {
                    "source_workflow_run_id": str(workflow.id),
                    "source_checkpoint_id": str(replay_source_checkpoint_id) if replay_source_checkpoint_id else None,
                    "source_node_key": replay_source_node_key or workflow.current_node_key,
                },
                "checkpoint": checkpoint_payload,
                "dry_run": replay_mode == WorkflowReplayMode.DRY_RUN.value,
                "metadata_only": replay_mode == WorkflowReplayMode.METADATA_ONLY.value,
                "no_runtime_reexecution": True,
            },
            started_at=now,
            completed_at=now,
        )
        self.session.add(replay_session)
        await self.session.flush()
        await self.traces.trace_replay(workflow=workflow, replay_session=replay_session, event_type=WorkflowTraceEventType.REPLAY_STARTED.value, commit=False)
        await self.traces.trace_replay(workflow=workflow, replay_session=replay_session, event_type=WorkflowTraceEventType.REPLAY_COMPLETED.value, commit=False)
        if commit:
            await self.session.commit()
            await self.session.refresh(replay_session)
        return replay_session

    async def list_replay_sessions(
        self,
        *,
        workspace_id: str,
        workflow_run_id: UUID | None = None,
        replay_status: str | None = None,
        limit: int = 100,
    ) -> list[WorkflowReplaySession]:
        statement = select(WorkflowReplaySession).where(WorkflowReplaySession.workspace_id == workspace_id)
        if workflow_run_id is not None:
            statement = statement.where(WorkflowReplaySession.workflow_run_id == workflow_run_id)
        if replay_status is not None:
            statement = statement.where(WorkflowReplaySession.replay_status == replay_status)
        result = await self.session.execute(statement.order_by(WorkflowReplaySession.created_at.desc()).limit(limit))
        return list(result.scalars().all())

    async def get_replay_session(self, *, workspace_id: str, replay_session_id: UUID) -> WorkflowReplaySession | None:
        result = await self.session.execute(
            select(WorkflowReplaySession).where(
                WorkflowReplaySession.workspace_id == workspace_id,
                WorkflowReplaySession.id == replay_session_id,
            )
        )
        return result.scalar_one_or_none()

    async def _require_workflow(self, *, workspace_id: str, workflow_run_id: UUID) -> WorkflowRun:
        result = await self.session.execute(select(WorkflowRun).where(WorkflowRun.workspace_id == workspace_id, WorkflowRun.id == workflow_run_id))
        workflow = result.scalar_one_or_none()
        if workflow is None:
            raise ValueError("Workflow run not found in workspace")
        return workflow

    async def _require_checkpoint(self, *, workspace_id: str, checkpoint_id: UUID) -> WorkflowCheckpoint:
        result = await self.session.execute(select(WorkflowCheckpoint).where(WorkflowCheckpoint.workspace_id == workspace_id, WorkflowCheckpoint.id == checkpoint_id))
        checkpoint = result.scalar_one_or_none()
        if checkpoint is None:
            raise ValueError("Workflow checkpoint not found in workspace")
        return checkpoint

    async def _failed_steps(self, *, workspace_id: str, workflow_run_id: UUID) -> list[WorkflowStep]:
        result = await self.session.execute(
            select(WorkflowStep).where(
                WorkflowStep.workspace_id == workspace_id,
                WorkflowStep.workflow_run_id == workflow_run_id,
                WorkflowStep.status == "failed",
            )
        )
        return list(result.scalars().all())

    async def _step_count(self, *, workspace_id: str, workflow_run_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(WorkflowStep).where(
                WorkflowStep.workspace_id == workspace_id,
                WorkflowStep.workflow_run_id == workflow_run_id,
            )
        )
        return int(result.scalar_one() or 0)

    async def _artifact_count(self, *, workspace_id: str, workflow_run_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(OutputArtifact).where(
                OutputArtifact.workspace_id == workspace_id,
                OutputArtifact.workflow_run_id == workflow_run_id,
                OutputArtifact.status != OutputArtifactStatus.DELETED.value,
            )
        )
        return int(result.scalar_one() or 0)

    async def _checkpoint_count(self, *, workspace_id: str, workflow_run_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(WorkflowCheckpoint).where(
                WorkflowCheckpoint.workspace_id == workspace_id,
                WorkflowCheckpoint.workflow_run_id == workflow_run_id,
            )
        )
        return int(result.scalar_one() or 0)

    async def _replay_session_count(self, *, workspace_id: str, workflow_run_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count()).select_from(WorkflowReplaySession).where(
                WorkflowReplaySession.workspace_id == workspace_id,
                WorkflowReplaySession.workflow_run_id == workflow_run_id,
            )
        )
        return int(result.scalar_one() or 0)

    def _workflow_runtime_ms(self, workflow: WorkflowRun) -> int:
        start = workflow.started_at or workflow.created_at
        end = workflow.completed_at or workflow.failed_at or workflow.paused_at or datetime.now(UTC)
        if start.tzinfo is None and end.tzinfo is not None:
            start = start.replace(tzinfo=end.tzinfo)
        elif start.tzinfo is not None and end.tzinfo is None:
            end = end.replace(tzinfo=start.tzinfo)
        return max(0, int((end - start).total_seconds() * 1000))

    def _recoverability_hint(self, workflow: WorkflowRun) -> dict[str, Any]:
        return {
            "recoverable": workflow.status in {WorkflowRunStatus.FAILED.value, WorkflowRunStatus.PAUSED.value, WorkflowRunStatus.WAITING_APPROVAL.value},
            "requires_approval": workflow.status == WorkflowRunStatus.WAITING_APPROVAL.value,
            "current_node_key": workflow.current_node_key,
        }
