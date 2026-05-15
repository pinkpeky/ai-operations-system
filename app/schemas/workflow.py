"""Workflow State API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.workflow import (
    AgentMemorySnapshot,
    WorkflowCheckpoint,
    WorkflowGraph,
    WorkflowGraphEdge,
    WorkflowGraphNode,
    WorkflowReplay,
    WorkflowRun,
    WorkflowStep,
)


WorkflowStatusLiteral = Literal["pending", "running", "paused", "waiting_approval", "completed", "failed", "cancelled"]
WorkflowCheckpointTypeLiteral = Literal["auto", "manual", "approval", "failure", "resume"]
AgentMemorySnapshotTypeLiteral = Literal[
    "conversation_summary",
    "task_context",
    "tool_result",
    "decision",
    "approval_context",
    "artifact_summary",
]
WorkflowEdgeTypeLiteral = Literal["success", "failure", "conditional", "retry", "fallback", "always"]
WorkflowNodeTypeLiteral = Literal[
    "playbook_step",
    "approval_gate",
    "tool_call",
    "artifact_transform",
    "conditional_router",
    "delay",
    "retry",
    "workflow_checkpoint",
    "memory_snapshot",
    "no_op",
]
WorkflowNodeExecutionModeLiteral = Literal["sync", "async", "background"]


class WorkflowRunResponse(BaseModel):
    id: UUID
    workspace_id: str
    source_type: str
    source_id: str | None
    conversation_thread_id: UUID | None
    playbook_run_id: UUID | None
    task_run_id: UUID | None
    workflow_graph_id: UUID | None
    graph_execution: bool
    current_node_key: str | None
    planned_next_nodes: list[str]
    skipped_nodes: list[str]
    retry_state: dict[str, Any]
    fallback_state: dict[str, Any]
    status: str
    current_step: int
    variables: dict[str, Any]
    context: dict[str, Any]
    checkpoints: list[dict[str, Any]]
    metadata: dict[str, Any]
    started_at: datetime | None
    completed_at: datetime | None
    paused_at: datetime | None
    resumed_at: datetime | None
    failed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, workflow: WorkflowRun) -> "WorkflowRunResponse":
        return cls(
            id=workflow.id,
            workspace_id=workflow.workspace_id,
            source_type=workflow.source_type,
            source_id=workflow.source_id,
            conversation_thread_id=workflow.conversation_thread_id,
            playbook_run_id=workflow.playbook_run_id,
            task_run_id=workflow.task_run_id,
            workflow_graph_id=workflow.workflow_graph_id,
            graph_execution=workflow.graph_execution,
            current_node_key=workflow.current_node_key,
            planned_next_nodes=workflow.planned_next_nodes or [],
            skipped_nodes=workflow.skipped_nodes or [],
            retry_state=workflow.retry_state or {},
            fallback_state=workflow.fallback_state or {},
            status=workflow.status,
            current_step=workflow.current_step,
            variables=workflow.variables or {},
            context=workflow.context or {},
            checkpoints=workflow.checkpoints or [],
            metadata=workflow.workflow_metadata or {},
            started_at=workflow.started_at,
            completed_at=workflow.completed_at,
            paused_at=workflow.paused_at,
            resumed_at=workflow.resumed_at,
            failed_at=workflow.failed_at,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
        )


class WorkflowRunListResponse(BaseModel):
    items: list[WorkflowRunResponse]


class WorkflowStepResponse(BaseModel):
    id: UUID
    workspace_id: str
    workflow_run_id: UUID
    step_index: int
    step_name: str
    step_type: str
    node_key: str | None
    parent_node_key: str | None
    dependency_state: dict[str, Any]
    status: str
    input_payload: dict[str, Any]
    output_payload: dict[str, Any]
    error: str | None
    started_at: datetime | None
    completed_at: datetime | None
    duration_ms: int | None
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, step: WorkflowStep) -> "WorkflowStepResponse":
        return cls(
            id=step.id,
            workspace_id=step.workspace_id,
            workflow_run_id=step.workflow_run_id,
            step_index=step.step_index,
            step_name=step.step_name,
            step_type=step.step_type,
            node_key=step.node_key,
            parent_node_key=step.parent_node_key,
            dependency_state=step.dependency_state or {},
            status=step.status,
            input_payload=step.input_payload or {},
            output_payload=step.output_payload or {},
            error=step.error,
            started_at=step.started_at,
            completed_at=step.completed_at,
            duration_ms=step.duration_ms,
            metadata=step.step_metadata or {},
            created_at=step.created_at,
            updated_at=step.updated_at,
        )


class WorkflowStepListResponse(BaseModel):
    workflow_run_id: UUID
    items: list[WorkflowStepResponse]


class WorkflowGraphNodeRequest(BaseModel):
    node_key: str = Field(min_length=1, max_length=128)
    node_type: WorkflowNodeTypeLiteral = "no_op"
    execution_mode: WorkflowNodeExecutionModeLiteral = "sync"
    configuration: dict[str, Any] = Field(default_factory=dict)
    retry_policy: dict[str, Any] = Field(default_factory=dict)
    timeout_seconds: int | None = Field(default=None, ge=1, le=3600)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowGraphEdgeRequest(BaseModel):
    source_node_key: str = Field(min_length=1, max_length=128)
    target_node_key: str = Field(min_length=1, max_length=128)
    edge_type: WorkflowEdgeTypeLiteral = "success"
    condition_expression: str | None = None
    priority: int = Field(default=100, ge=0, le=10000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowGraphCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = None
    version: str = Field(default="1", max_length=64)
    graph_definition: dict[str, Any] = Field(default_factory=dict)
    entry_node: str = Field(min_length=1, max_length=128)
    nodes: list[WorkflowGraphNodeRequest] = Field(default_factory=list)
    edges: list[WorkflowGraphEdgeRequest] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowGraphNodeResponse(BaseModel):
    id: UUID
    workflow_graph_id: UUID
    node_key: str
    node_type: str
    execution_mode: str
    configuration: dict[str, Any]
    retry_policy: dict[str, Any]
    timeout_seconds: int | None
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, node: WorkflowGraphNode) -> "WorkflowGraphNodeResponse":
        return cls(
            id=node.id,
            workflow_graph_id=node.workflow_graph_id,
            node_key=node.node_key,
            node_type=node.node_type,
            execution_mode=node.execution_mode,
            configuration=node.configuration or {},
            retry_policy=node.retry_policy or {},
            timeout_seconds=node.timeout_seconds,
            metadata=node.node_metadata or {},
            created_at=node.created_at,
        )


class WorkflowGraphEdgeResponse(BaseModel):
    id: UUID
    workflow_graph_id: UUID
    source_node_key: str
    target_node_key: str
    edge_type: str
    condition_expression: str | None
    priority: int
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, edge: WorkflowGraphEdge) -> "WorkflowGraphEdgeResponse":
        return cls(
            id=edge.id,
            workflow_graph_id=edge.workflow_graph_id,
            source_node_key=edge.source_node_key,
            target_node_key=edge.target_node_key,
            edge_type=edge.edge_type,
            condition_expression=edge.condition_expression,
            priority=edge.priority,
            metadata=edge.edge_metadata or {},
            created_at=edge.created_at,
        )


class WorkflowGraphResponse(BaseModel):
    id: UUID
    workspace_id: str
    name: str
    description: str | None
    version: str
    graph_definition: dict[str, Any]
    entry_node: str
    metadata: dict[str, Any]
    nodes: list[WorkflowGraphNodeResponse] = Field(default_factory=list)
    edges: list[WorkflowGraphEdgeResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, graph: WorkflowGraph) -> "WorkflowGraphResponse":
        return cls(
            id=graph.id,
            workspace_id=graph.workspace_id,
            name=graph.name,
            description=graph.description,
            version=graph.version,
            graph_definition=graph.graph_definition or {},
            entry_node=graph.entry_node,
            metadata=graph.graph_metadata or {},
            nodes=[WorkflowGraphNodeResponse.from_model(node) for node in sorted(graph.nodes, key=lambda item: item.node_key)],
            edges=[
                WorkflowGraphEdgeResponse.from_model(edge)
                for edge in sorted(graph.edges, key=lambda item: (item.source_node_key, item.priority, item.target_node_key))
            ],
            created_at=graph.created_at,
            updated_at=graph.updated_at,
        )


class WorkflowGraphListResponse(BaseModel):
    items: list[WorkflowGraphResponse]


class WorkflowPlannerResultResponse(BaseModel):
    valid: bool
    errors: list[str] = Field(default_factory=list)
    entry_node: str | None = None
    execution_order: list[str] = Field(default_factory=list)
    current_node: str | None = None
    next_nodes: list[str] = Field(default_factory=list)
    skipped_nodes: list[str] = Field(default_factory=list)
    retry_paths: list[dict[str, Any]] = Field(default_factory=list)
    fallback_paths: list[dict[str, Any]] = Field(default_factory=list)
    condition_results: list[dict[str, Any]] = Field(default_factory=list)
    dependency_state: dict[str, Any] = Field(default_factory=dict)


class WorkflowReplayCreateRequest(BaseModel):
    replay_source_checkpoint_id: UUID | None = None
    replay_reason: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class WorkflowReplayResponse(BaseModel):
    id: UUID
    workflow_run_id: UUID
    replay_source_checkpoint_id: UUID | None
    replay_reason: str | None
    replay_status: str
    metadata: dict[str, Any]
    created_at: datetime

    @classmethod
    def from_model(cls, replay: WorkflowReplay) -> "WorkflowReplayResponse":
        return cls(
            id=replay.id,
            workflow_run_id=replay.workflow_run_id,
            replay_source_checkpoint_id=replay.replay_source_checkpoint_id,
            replay_reason=replay.replay_reason,
            replay_status=replay.replay_status,
            metadata=replay.replay_metadata or {},
            created_at=replay.created_at,
        )


class WorkflowCheckpointCreateRequest(BaseModel):
    checkpoint_name: str = Field(default="manual checkpoint", min_length=1, max_length=255)
    checkpoint_type: WorkflowCheckpointTypeLiteral = "manual"
    state_payload: dict[str, Any] = Field(default_factory=dict)
    variables_snapshot: dict[str, Any] | None = None
    context_snapshot: dict[str, Any] | None = None


class WorkflowCheckpointResponse(BaseModel):
    id: UUID
    workspace_id: str
    workflow_run_id: UUID
    checkpoint_name: str
    checkpoint_type: str
    state_payload: dict[str, Any]
    variables_snapshot: dict[str, Any]
    context_snapshot: dict[str, Any]
    created_by: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, checkpoint: WorkflowCheckpoint) -> "WorkflowCheckpointResponse":
        return cls(
            id=checkpoint.id,
            workspace_id=checkpoint.workspace_id,
            workflow_run_id=checkpoint.workflow_run_id,
            checkpoint_name=checkpoint.checkpoint_name,
            checkpoint_type=checkpoint.checkpoint_type,
            state_payload=checkpoint.state_payload or {},
            variables_snapshot=checkpoint.variables_snapshot or {},
            context_snapshot=checkpoint.context_snapshot or {},
            created_by=checkpoint.created_by,
            created_at=checkpoint.created_at,
            updated_at=checkpoint.updated_at,
        )


class WorkflowCheckpointListResponse(BaseModel):
    workflow_run_id: UUID
    items: list[WorkflowCheckpointResponse]


class WorkflowControlRequest(BaseModel):
    reason: str | None = None


class AgentMemorySnapshotCreateRequest(BaseModel):
    memory_type: AgentMemorySnapshotTypeLiteral = "task_context"
    summary: str | None = None
    node_key: str | None = Field(default=None, max_length=128)
    memory_payload: dict[str, Any] = Field(default_factory=dict)
    source_event_ids: list[str] = Field(default_factory=list)
    source_artifact_ids: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AgentMemorySnapshotResponse(BaseModel):
    id: UUID
    workspace_id: str
    workflow_run_id: UUID | None
    conversation_thread_id: UUID | None
    task_run_id: UUID | None
    node_key: str | None
    memory_type: str
    summary: str | None
    memory_payload: dict[str, Any]
    source_event_ids: list[str]
    source_artifact_ids: list[str]
    metadata: dict[str, Any]
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, snapshot: AgentMemorySnapshot) -> "AgentMemorySnapshotResponse":
        return cls(
            id=snapshot.id,
            workspace_id=snapshot.workspace_id,
            workflow_run_id=snapshot.workflow_run_id,
            conversation_thread_id=snapshot.conversation_thread_id,
            task_run_id=snapshot.task_run_id,
            node_key=snapshot.node_key,
            memory_type=snapshot.memory_type,
            summary=snapshot.summary,
            memory_payload=snapshot.memory_payload or {},
            source_event_ids=snapshot.source_event_ids or [],
            source_artifact_ids=snapshot.source_artifact_ids or [],
            metadata=snapshot.snapshot_metadata or {},
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )


class AgentMemorySnapshotListResponse(BaseModel):
    workflow_run_id: UUID | None = None
    items: list[AgentMemorySnapshotResponse]
