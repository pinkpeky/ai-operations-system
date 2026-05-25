"""ComfyUI runtime adapter contract schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.comfyui_runtime import (
    ComfyUIRuntimeConfigChangeRequest,
    ComfyUIRuntimeDiagnosticSnapshot,
    ComfyUIRuntimeGuardedProbeExecution,
    ComfyUIRuntimeManualApplyEvidence,
    ComfyUIRuntimePostManualReadinessCheck,
)


class ComfyUIRuntimeHealthResponse(BaseModel):
    """Disabled-by-default ComfyUI runtime contract health response."""

    success: bool = True
    provider: str
    enabled: bool
    reachable: bool = False
    guarded: bool = True
    mock: bool = True
    network_allowed: bool = False
    external_request_attempted: bool = False
    runtime_calls_enabled: bool = False
    read_only_probe_enabled: bool = False
    read_only_probe_attempted: bool = False
    health_path: str | None = None
    allowed_health_paths: list[str] = Field(default_factory=list)
    probe_status_code: int | None = None
    probe_latency_ms: float | None = None
    base_url: str
    allowed_hosts: list[str] = Field(default_factory=list)
    timeout_seconds: float
    workspace_id: str | None = None
    error: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeCapabilitiesResponse(BaseModel):
    """ComfyUI runtime adapter contract capabilities response."""

    success: bool = True
    provider: str
    enabled: bool
    guarded: bool = True
    mock: bool = True
    base_url: str
    allowed_hosts: list[str] = Field(default_factory=list)
    health_path: str | None = None
    allowed_health_paths: list[str] = Field(default_factory=list)
    read_only_probe_enabled: bool = False
    available_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    required_configuration: list[str] = Field(default_factory=list)
    workspace_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeDiagnosticCheck(BaseModel):
    """One no-network readiness check for the guarded ComfyUI runtime."""

    key: str
    status: str
    label: str
    detail: str
    current_value: Any = None
    expected_value: Any = None
    remediation: str | None = None


class ComfyUIRuntimeDiagnosticsResponse(BaseModel):
    """No-network ComfyUI runtime readiness diagnostics for operators."""

    success: bool = True
    provider: str
    enabled: bool
    guarded: bool = True
    network_allowed: bool = False
    read_only_probe_enabled: bool = False
    base_url: str
    parsed_host: str | None = None
    scheme_allowed: bool = False
    host_allowed: bool = False
    allowed_hosts: list[str] = Field(default_factory=list)
    health_path: str
    health_path_allowed: bool = False
    allowed_health_paths: list[str] = Field(default_factory=list)
    read_only_probe_ready: bool = False
    external_request_attempted: bool = False
    runtime_calls_enabled: bool = False
    readiness_status: str
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    diagnostics: list[ComfyUIRuntimeDiagnosticCheck] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    workspace_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeMaintenanceStep(BaseModel):
    """One operator-facing ComfyUI runtime maintenance step."""

    key: str
    title: str
    status: str
    audience: str
    detail: str
    action: str | None = None
    blocking: bool = False
    source_check: str | None = None


class ComfyUIRuntimeMaintenanceRunbookResponse(BaseModel):
    """No-network ComfyUI runtime maintenance runbook for server operators."""

    success: bool = True
    phase: str = "62E"
    workspace_id: str | None = None
    title: str
    summary: str
    readiness_status: str
    read_only_probe_ready: bool = False
    external_request_attempted: bool = False
    runtime_calls_enabled: bool = False
    next_operator_action: str
    snapshot_recommended: bool = True
    steps: list[ComfyUIRuntimeMaintenanceStep] = Field(default_factory=list)
    recovery_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    configuration_summary: dict[str, Any] = Field(default_factory=dict)
    diagnostics: ComfyUIRuntimeDiagnosticsResponse
    raw: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeConfigChangeRequestCreateRequest(BaseModel):
    """Create a metadata-only ComfyUI runtime configuration change request."""

    change_reason: str | None = Field(default=None, max_length=2000)
    requested_changes: list[dict[str, Any]] = Field(default_factory=list)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeConfigChangeDecisionRequest(BaseModel):
    """Review a metadata-only ComfyUI runtime configuration change request."""

    reviewer_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeConfigChangeRequestResponse(BaseModel):
    """Persisted ComfyUI runtime configuration change request response."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    change_status: str
    provider: str
    readiness_status: str
    read_only_probe_ready: bool
    external_request_attempted: bool
    runtime_calls_enabled: bool
    config_mutation_performed: bool
    current_configuration: dict[str, Any] = Field(default_factory=dict)
    requested_changes: list[dict[str, Any]] = Field(default_factory=list)
    runbook_steps: list[dict[str, Any]] = Field(default_factory=list)
    recovery_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    runbook_payload: dict[str, Any] = Field(default_factory=dict)
    change_reason: str | None = None
    operator_note: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        request: ComfyUIRuntimeConfigChangeRequest,
    ) -> "ComfyUIRuntimeConfigChangeRequestResponse":
        return cls(
            id=request.id,
            workspace_id=request.workspace_id,
            user_id=request.user_id,
            change_status=request.change_status,
            provider=request.provider,
            readiness_status=request.readiness_status,
            read_only_probe_ready=request.read_only_probe_ready,
            external_request_attempted=request.external_request_attempted,
            runtime_calls_enabled=request.runtime_calls_enabled,
            config_mutation_performed=request.config_mutation_performed,
            current_configuration=request.current_configuration or {},
            requested_changes=request.requested_changes or [],
            runbook_steps=request.runbook_steps or [],
            recovery_actions=request.recovery_actions or [],
            disabled_actions=request.disabled_actions or [],
            runbook_payload=request.runbook_payload or {},
            change_reason=request.change_reason,
            operator_note=request.operator_note,
            reviewer_notes=request.reviewer_notes,
            metadata=request.request_metadata or {},
            created_at=request.created_at,
            updated_at=request.updated_at,
        )


class ComfyUIRuntimeConfigChangeRequestListResponse(BaseModel):
    """List response for ComfyUI runtime configuration change requests."""

    success: bool = True
    workspace_id: str
    items: list[ComfyUIRuntimeConfigChangeRequestResponse] = Field(default_factory=list)


class ComfyUIRuntimeManualApplyEvidenceCreateRequest(BaseModel):
    """Record metadata-only evidence for a human-applied ComfyUI runtime configuration change."""

    before_snapshot_id: UUID | None = None
    after_snapshot_id: UUID | None = None
    manual_config_applied: bool = True
    service_restart_reported: bool = False
    manual_apply_steps: list[dict[str, Any]] = Field(default_factory=list)
    restart_evidence: dict[str, Any] = Field(default_factory=dict)
    rollback_notes: str | None = Field(default=None, max_length=4000)
    verification_notes: str | None = Field(default=None, max_length=4000)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeManualApplyEvidenceDecisionRequest(BaseModel):
    """Review metadata-only manual apply evidence."""

    reviewer_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeManualApplyEvidenceResponse(BaseModel):
    """Persisted ComfyUI runtime manual apply evidence response."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    config_change_request_id: UUID
    before_snapshot_id: UUID | None = None
    after_snapshot_id: UUID | None = None
    evidence_status: str
    provider: str
    readiness_status_before: str
    readiness_status_after: str
    read_only_probe_ready_before: bool
    read_only_probe_ready_after: bool
    external_request_attempted: bool
    runtime_calls_enabled: bool
    api_config_mutation_performed: bool
    manual_config_applied: bool
    service_restart_reported: bool
    config_change_request_payload: dict[str, Any] = Field(default_factory=dict)
    current_configuration_before: dict[str, Any] = Field(default_factory=dict)
    current_configuration_after: dict[str, Any] = Field(default_factory=dict)
    requested_changes: list[dict[str, Any]] = Field(default_factory=list)
    manual_apply_steps: list[dict[str, Any]] = Field(default_factory=list)
    restart_evidence: dict[str, Any] = Field(default_factory=dict)
    verification_results: dict[str, Any] = Field(default_factory=dict)
    diagnostics_payload: dict[str, Any] = Field(default_factory=dict)
    rollback_notes: str | None = None
    verification_notes: str | None = None
    operator_note: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        evidence: ComfyUIRuntimeManualApplyEvidence,
    ) -> "ComfyUIRuntimeManualApplyEvidenceResponse":
        return cls(
            id=evidence.id,
            workspace_id=evidence.workspace_id,
            user_id=evidence.user_id,
            config_change_request_id=evidence.config_change_request_id,
            before_snapshot_id=evidence.before_snapshot_id,
            after_snapshot_id=evidence.after_snapshot_id,
            evidence_status=evidence.evidence_status,
            provider=evidence.provider,
            readiness_status_before=evidence.readiness_status_before,
            readiness_status_after=evidence.readiness_status_after,
            read_only_probe_ready_before=evidence.read_only_probe_ready_before,
            read_only_probe_ready_after=evidence.read_only_probe_ready_after,
            external_request_attempted=evidence.external_request_attempted,
            runtime_calls_enabled=evidence.runtime_calls_enabled,
            api_config_mutation_performed=evidence.api_config_mutation_performed,
            manual_config_applied=evidence.manual_config_applied,
            service_restart_reported=evidence.service_restart_reported,
            config_change_request_payload=evidence.config_change_request_payload or {},
            current_configuration_before=evidence.current_configuration_before or {},
            current_configuration_after=evidence.current_configuration_after or {},
            requested_changes=evidence.requested_changes or [],
            manual_apply_steps=evidence.manual_apply_steps or [],
            restart_evidence=evidence.restart_evidence or {},
            verification_results=evidence.verification_results or {},
            diagnostics_payload=evidence.diagnostics_payload or {},
            rollback_notes=evidence.rollback_notes,
            verification_notes=evidence.verification_notes,
            operator_note=evidence.operator_note,
            reviewer_notes=evidence.reviewer_notes,
            metadata=evidence.evidence_metadata or {},
            created_at=evidence.created_at,
            updated_at=evidence.updated_at,
        )


class ComfyUIRuntimeManualApplyEvidenceListResponse(BaseModel):
    """List response for ComfyUI runtime manual apply evidence."""

    success: bool = True
    workspace_id: str
    items: list[ComfyUIRuntimeManualApplyEvidenceResponse] = Field(default_factory=list)


class ComfyUIRuntimePostManualReadinessCheckCreateRequest(BaseModel):
    """Create a metadata-only readiness comparison after manual ComfyUI config apply."""

    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimePostManualReadinessCheckDecisionRequest(BaseModel):
    """Review metadata-only post-manual readiness comparison."""

    reviewer_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimePostManualReadinessCheckResponse(BaseModel):
    """Persisted ComfyUI runtime post-manual readiness comparison response."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    manual_apply_evidence_id: UUID
    config_change_request_id: UUID
    check_status: str
    comparison_status: str
    provider: str
    readiness_status_before: str
    readiness_status_after_evidence: str
    readiness_status_current: str
    read_only_probe_ready_before: bool
    read_only_probe_ready_after_evidence: bool
    read_only_probe_ready_current: bool
    guarded_probe_ready: bool
    manual_evidence_status: str
    manual_config_applied: bool
    service_restart_reported: bool
    external_request_attempted: bool
    runtime_calls_enabled: bool
    health_probe_executed: bool
    api_config_mutation_performed: bool
    requested_changes: list[dict[str, Any]] = Field(default_factory=list)
    manual_apply_steps: list[dict[str, Any]] = Field(default_factory=list)
    restart_evidence: dict[str, Any] = Field(default_factory=dict)
    evidence_payload: dict[str, Any] = Field(default_factory=dict)
    current_diagnostics_payload: dict[str, Any] = Field(default_factory=dict)
    comparison_results: dict[str, Any] = Field(default_factory=dict)
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    next_operator_action: str | None = None
    operator_note: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        check: ComfyUIRuntimePostManualReadinessCheck,
    ) -> "ComfyUIRuntimePostManualReadinessCheckResponse":
        return cls(
            id=check.id,
            workspace_id=check.workspace_id,
            user_id=check.user_id,
            manual_apply_evidence_id=check.manual_apply_evidence_id,
            config_change_request_id=check.config_change_request_id,
            check_status=check.check_status,
            comparison_status=check.comparison_status,
            provider=check.provider,
            readiness_status_before=check.readiness_status_before,
            readiness_status_after_evidence=check.readiness_status_after_evidence,
            readiness_status_current=check.readiness_status_current,
            read_only_probe_ready_before=check.read_only_probe_ready_before,
            read_only_probe_ready_after_evidence=check.read_only_probe_ready_after_evidence,
            read_only_probe_ready_current=check.read_only_probe_ready_current,
            guarded_probe_ready=check.guarded_probe_ready,
            manual_evidence_status=check.manual_evidence_status,
            manual_config_applied=check.manual_config_applied,
            service_restart_reported=check.service_restart_reported,
            external_request_attempted=check.external_request_attempted,
            runtime_calls_enabled=check.runtime_calls_enabled,
            health_probe_executed=check.health_probe_executed,
            api_config_mutation_performed=check.api_config_mutation_performed,
            requested_changes=check.requested_changes or [],
            manual_apply_steps=check.manual_apply_steps or [],
            restart_evidence=check.restart_evidence or {},
            evidence_payload=check.evidence_payload or {},
            current_diagnostics_payload=check.current_diagnostics_payload or {},
            comparison_results=check.comparison_results or {},
            blocking_reasons=check.blocking_reasons or [],
            recommended_actions=check.recommended_actions or [],
            next_operator_action=check.next_operator_action,
            operator_note=check.operator_note,
            reviewer_notes=check.reviewer_notes,
            metadata=check.check_metadata or {},
            created_at=check.created_at,
            updated_at=check.updated_at,
        )


class ComfyUIRuntimePostManualReadinessCheckListResponse(BaseModel):
    """List response for post-manual readiness comparisons."""

    success: bool = True
    workspace_id: str
    items: list[ComfyUIRuntimePostManualReadinessCheckResponse] = Field(default_factory=list)


class ComfyUIRuntimeGuardedProbeExecutionCreateRequest(BaseModel):
    """Create an approval-gated read-only ComfyUI probe execution record."""

    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeGuardedProbeExecutionDecisionRequest(BaseModel):
    """Review or execute an approval-gated read-only ComfyUI probe record."""

    reviewer_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeGuardedProbeExecutionResponse(BaseModel):
    """Persisted guarded read-only ComfyUI probe execution response."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    post_manual_readiness_check_id: UUID
    manual_apply_evidence_id: UUID
    config_change_request_id: UUID
    execution_status: str
    provider: str
    readiness_status_current: str
    read_only_probe_ready_current: bool
    guarded_probe_ready: bool
    base_url: str
    health_path: str
    allowed_hosts: list[str] = Field(default_factory=list)
    allowed_health_paths: list[str] = Field(default_factory=list)
    external_request_attempted: bool
    runtime_calls_enabled: bool
    health_probe_executed: bool
    read_only_probe_attempted: bool
    api_config_mutation_performed: bool
    probe_status_code: int | None = None
    probe_latency_ms: float | None = None
    probe_result_status: str
    readiness_check_payload: dict[str, Any] = Field(default_factory=dict)
    current_diagnostics_payload: dict[str, Any] = Field(default_factory=dict)
    probe_request: dict[str, Any] = Field(default_factory=dict)
    probe_response: dict[str, Any] = Field(default_factory=dict)
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    operator_note: str | None = None
    reviewer_notes: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        execution: ComfyUIRuntimeGuardedProbeExecution,
    ) -> "ComfyUIRuntimeGuardedProbeExecutionResponse":
        return cls(
            id=execution.id,
            workspace_id=execution.workspace_id,
            user_id=execution.user_id,
            post_manual_readiness_check_id=execution.post_manual_readiness_check_id,
            manual_apply_evidence_id=execution.manual_apply_evidence_id,
            config_change_request_id=execution.config_change_request_id,
            execution_status=execution.execution_status,
            provider=execution.provider,
            readiness_status_current=execution.readiness_status_current,
            read_only_probe_ready_current=execution.read_only_probe_ready_current,
            guarded_probe_ready=execution.guarded_probe_ready,
            base_url=execution.base_url,
            health_path=execution.health_path,
            allowed_hosts=execution.allowed_hosts or [],
            allowed_health_paths=execution.allowed_health_paths or [],
            external_request_attempted=execution.external_request_attempted,
            runtime_calls_enabled=execution.runtime_calls_enabled,
            health_probe_executed=execution.health_probe_executed,
            read_only_probe_attempted=execution.read_only_probe_attempted,
            api_config_mutation_performed=execution.api_config_mutation_performed,
            probe_status_code=execution.probe_status_code,
            probe_latency_ms=execution.probe_latency_ms,
            probe_result_status=execution.probe_result_status,
            readiness_check_payload=execution.readiness_check_payload or {},
            current_diagnostics_payload=execution.current_diagnostics_payload or {},
            probe_request=execution.probe_request or {},
            probe_response=execution.probe_response or {},
            blocking_reasons=execution.blocking_reasons or [],
            recommended_actions=execution.recommended_actions or [],
            disabled_actions=execution.disabled_actions or [],
            operator_note=execution.operator_note,
            reviewer_notes=execution.reviewer_notes,
            metadata=execution.execution_metadata or {},
            created_at=execution.created_at,
            updated_at=execution.updated_at,
        )


class ComfyUIRuntimeGuardedProbeExecutionListResponse(BaseModel):
    """List response for guarded read-only ComfyUI probe executions."""

    success: bool = True
    workspace_id: str
    items: list[ComfyUIRuntimeGuardedProbeExecutionResponse] = Field(default_factory=list)


class ComfyUIRuntimeDiagnosticSnapshotCreateRequest(BaseModel):
    """Create a persisted no-network ComfyUI runtime diagnostic snapshot."""

    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeDiagnosticSnapshotResponse(BaseModel):
    """Persisted ComfyUI runtime diagnostic snapshot response."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    provider: str
    enabled: bool
    guarded: bool
    network_allowed: bool
    read_only_probe_enabled: bool
    base_url: str
    parsed_host: str | None = None
    scheme_allowed: bool
    host_allowed: bool
    allowed_hosts: list[str] = Field(default_factory=list)
    health_path: str
    health_path_allowed: bool
    allowed_health_paths: list[str] = Field(default_factory=list)
    read_only_probe_ready: bool
    readiness_status: str
    external_request_attempted: bool
    runtime_calls_enabled: bool
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    diagnostics: list[dict[str, Any]] = Field(default_factory=list)
    forbidden_actions: list[str] = Field(default_factory=list)
    snapshot_payload: dict[str, Any] = Field(default_factory=dict)
    operator_note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(
        cls,
        snapshot: ComfyUIRuntimeDiagnosticSnapshot,
    ) -> "ComfyUIRuntimeDiagnosticSnapshotResponse":
        return cls(
            id=snapshot.id,
            workspace_id=snapshot.workspace_id,
            user_id=snapshot.user_id,
            provider=snapshot.provider,
            enabled=snapshot.enabled,
            guarded=snapshot.guarded,
            network_allowed=snapshot.network_allowed,
            read_only_probe_enabled=snapshot.read_only_probe_enabled,
            base_url=snapshot.base_url,
            parsed_host=snapshot.parsed_host,
            scheme_allowed=snapshot.scheme_allowed,
            host_allowed=snapshot.host_allowed,
            allowed_hosts=snapshot.allowed_hosts or [],
            health_path=snapshot.health_path,
            health_path_allowed=snapshot.health_path_allowed,
            allowed_health_paths=snapshot.allowed_health_paths or [],
            read_only_probe_ready=snapshot.read_only_probe_ready,
            readiness_status=snapshot.readiness_status,
            external_request_attempted=snapshot.external_request_attempted,
            runtime_calls_enabled=snapshot.runtime_calls_enabled,
            blocking_reasons=snapshot.blocking_reasons or [],
            recommended_actions=snapshot.recommended_actions or [],
            diagnostics=snapshot.diagnostics or [],
            forbidden_actions=snapshot.forbidden_actions or [],
            snapshot_payload=snapshot.snapshot_payload or {},
            operator_note=snapshot.operator_note,
            metadata=snapshot.snapshot_metadata or {},
            created_at=snapshot.created_at,
            updated_at=snapshot.updated_at,
        )


class ComfyUIRuntimeDiagnosticSnapshotListResponse(BaseModel):
    """List response for persisted ComfyUI runtime diagnostic snapshots."""

    success: bool = True
    workspace_id: str
    items: list[ComfyUIRuntimeDiagnosticSnapshotResponse] = Field(default_factory=list)


class ComfyUIRuntimePromptJobSubmitRequest(BaseModel):
    """Submit one guarded real ComfyUI prompt workflow."""

    prompt: dict[str, Any] = Field(default_factory=dict)
    client_id: str | None = Field(default=None, max_length=200)
    extra_data: dict[str, Any] = Field(default_factory=dict)
    workflow: dict[str, Any] | None = None
    media_type: str = Field(default="image", max_length=32)
    resource_profile: str = Field(default="standard", max_length=64)
    width: int | None = Field(default=None, ge=64, le=8192)
    height: int | None = Field(default=None, ge=64, le=8192)
    frames: int | None = Field(default=None, ge=1, le=20000)
    fps: float | None = Field(default=None, ge=1.0, le=240.0)
    duration_seconds: float | None = Field(default=None, ge=0.1, le=3600.0)
    estimated_vram_mb: int | None = Field(default=None, ge=256, le=131072)
    reserve_vram_mb: int | None = Field(default=None, ge=0, le=131072)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimePromptJobSubmitResponse(BaseModel):
    """Response from a guarded real ComfyUI /prompt submission."""

    success: bool
    workspace_id: str | None = None
    provider: str
    enabled: bool
    base_url: str
    path: str = "/prompt"
    external_request_attempted: bool
    runtime_calls_enabled: bool
    prompt_submission_enabled: bool
    status_code: int | None = None
    prompt_id: str | None = None
    number: int | float | None = None
    node_errors: dict[str, Any] = Field(default_factory=dict)
    response_payload: dict[str, Any] = Field(default_factory=dict)
    request_payload: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimePromptHistoryResponse(BaseModel):
    """Response from a guarded real ComfyUI /history/{prompt_id} read."""

    success: bool
    workspace_id: str | None = None
    provider: str
    base_url: str
    path: str
    prompt_id: str
    external_request_attempted: bool
    runtime_calls_enabled: bool
    prompt_submission_enabled: bool
    status_code: int | None = None
    response_payload: dict[str, Any] = Field(default_factory=dict)
    outputs: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None


class ComfyUIRuntimeQueueResponse(BaseModel):
    """Response from a guarded real ComfyUI /queue read."""

    success: bool
    workspace_id: str | None = None
    provider: str
    base_url: str
    path: str = "/queue"
    external_request_attempted: bool
    runtime_calls_enabled: bool
    prompt_submission_enabled: bool
    status_code: int | None = None
    response_payload: dict[str, Any] = Field(default_factory=dict)
    queue_running: list[Any] = Field(default_factory=list)
    queue_pending: list[Any] = Field(default_factory=list)
    error: str | None = None


class ComfyUIRuntimeVideoResourcePlanRequest(BaseModel):
    """Plan GPU and queue admission for one ComfyUI video generation request."""

    resource_profile: str = Field(default="standard", max_length=64)
    width: int = Field(default=1280, ge=64, le=8192)
    height: int = Field(default=720, ge=64, le=8192)
    frames: int = Field(default=96, ge=1, le=20000)
    fps: float = Field(default=24.0, ge=1.0, le=240.0)
    duration_seconds: float | None = Field(default=None, ge=0.1, le=3600.0)
    estimated_vram_mb: int | None = Field(default=None, ge=256, le=131072)
    reserve_vram_mb: int | None = Field(default=None, ge=0, le=131072)
    priority: str = Field(default="normal", max_length=32)
    allow_queue: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class ComfyUIRuntimeVideoResourcePlanResponse(BaseModel):
    """GPU/queue admission plan for ComfyUI video generation."""

    success: bool
    workspace_id: str | None = None
    provider: str
    base_url: str
    media_type: str = "video"
    resource_profile: str
    width: int
    height: int
    frames: int
    fps: float
    duration_seconds: float | None = None
    estimated_vram_mb: int
    reserve_vram_mb: int
    required_free_vram_mb: int
    max_concurrent_video_jobs: int
    queue_pending_limit: int
    admission_status: str
    should_submit_now: bool = False
    external_request_attempted: bool = False
    system_stats_attempted: bool = False
    queue_status_attempted: bool = False
    runtime_calls_enabled: bool = False
    prompt_submission_enabled: bool = False
    selected_endpoint: dict[str, Any] | None = None
    endpoint_plans: list[dict[str, Any]] = Field(default_factory=list)
    selected_gpu: dict[str, Any] | None = None
    gpu_devices: list[dict[str, Any]] = Field(default_factory=list)
    queue_running_count: int = 0
    queue_pending_count: int = 0
    blocking_reasons: list[str] = Field(default_factory=list)
    recommended_actions: list[str] = Field(default_factory=list)
    queue_payload: dict[str, Any] = Field(default_factory=dict)
    raw: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
