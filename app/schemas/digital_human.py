"""Digital human production API schemas."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.digital_human import DigitalHumanAsset, DigitalHumanVideoJob


class DigitalHumanCapabilitiesResponse(BaseModel):
    """Digital human provider and safety boundary summary."""

    success: bool = True
    provider: str
    enabled: bool
    external_api_allowed: bool
    provider_calls_enabled: bool
    available_providers: list[str] = Field(default_factory=list)
    recommended_provider_order: list[str] = Field(default_factory=list)
    local_pipeline: list[str] = Field(default_factory=list)
    required_assets: list[str] = Field(default_factory=list)
    disabled_actions: list[str] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    workspace_id: str | None = None
    raw: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanWorkflowTemplateResponse(BaseModel):
    """Built-in digital human ComfyUI workflow template contract."""

    success: bool = True
    template_id: str
    name: str
    workflow_kind: str
    recommended_use: str
    provider: str = "comfyui"
    default_resource_profile: str = "standard"
    recommended_vram_mb: int | None = None
    required_assets: list[str] = Field(default_factory=list)
    required_nodes: list[str] = Field(default_factory=list)
    required_models: list[str] = Field(default_factory=list)
    plugin_installation: list[dict[str, Any]] = Field(default_factory=list)
    model_installation: list[dict[str, Any]] = Field(default_factory=list)
    input_slots: list[dict[str, Any]] = Field(default_factory=list)
    output_slots: list[dict[str, Any]] = Field(default_factory=list)
    guardrails: list[str] = Field(default_factory=list)
    prompt_contract: dict[str, Any] = Field(default_factory=dict)
    workflow_contract: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanWorkflowTemplateListResponse(BaseModel):
    """Built-in digital human workflow template list."""

    success: bool = True
    workspace_id: str | None = None
    items: list[DigitalHumanWorkflowTemplateResponse] = Field(default_factory=list)


class DigitalHumanAssetResponse(BaseModel):
    """Persisted digital human asset."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    asset_type: str
    asset_status: str
    name: str
    source_uri: str
    file_name: str | None = None
    mime_type: str | None = None
    size_bytes: int | None = None
    checksum: str | None = None
    consent_status: str
    usage_scope: str | None = None
    operator_note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, asset: DigitalHumanAsset) -> "DigitalHumanAssetResponse":
        return cls(
            id=asset.id,
            workspace_id=asset.workspace_id,
            user_id=asset.user_id,
            asset_type=asset.asset_type,
            asset_status=asset.asset_status,
            name=asset.name,
            source_uri=asset.source_uri,
            file_name=asset.file_name,
            mime_type=asset.mime_type,
            size_bytes=asset.size_bytes,
            checksum=asset.checksum,
            consent_status=asset.consent_status,
            usage_scope=asset.usage_scope,
            operator_note=asset.operator_note,
            metadata=asset.asset_metadata or {},
            created_at=asset.created_at,
            updated_at=asset.updated_at,
        )


class DigitalHumanAssetListResponse(BaseModel):
    """Workspace-scoped digital human asset list."""

    success: bool = True
    workspace_id: str
    items: list[DigitalHumanAssetResponse] = Field(default_factory=list)


class DigitalHumanVideoJobCreateRequest(BaseModel):
    """Create a digital human video job plan."""

    objective: str = Field(min_length=1, max_length=8000)
    script: str = Field(min_length=1, max_length=20000)
    provider: str | None = Field(default=None, max_length=64)
    avatar_asset_id: UUID | None = None
    material_asset_ids: list[UUID] = Field(default_factory=list)
    reference_asset_ids: list[UUID] = Field(default_factory=list)
    target_channels: list[str] = Field(default_factory=list)
    voice_profile: dict[str, Any] = Field(default_factory=dict)
    aspect_ratio: str = Field(default="9:16", max_length=32)
    duration_seconds: float | None = Field(default=None, ge=1.0, le=3600.0)
    llm_planning_enabled: bool = False
    planning_context: dict[str, Any] = Field(default_factory=dict)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanVideoJobRefreshRequest(BaseModel):
    """Refresh a digital human job from the configured provider boundary."""

    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanVideoJobExecuteRequest(BaseModel):
    """Execute an approved digital human video job through a guarded handoff."""

    execution_mode: str = Field(default="mock_render", max_length=64)
    submit_immediately: bool = False
    poll_history: bool = True
    prompt: dict[str, Any] = Field(default_factory=dict)
    workflow: dict[str, Any] | None = None
    resource_profile: str = Field(default="standard", max_length=64)
    width: int | None = Field(default=1080, ge=64, le=8192)
    height: int | None = Field(default=1920, ge=64, le=8192)
    frames: int | None = Field(default=None, ge=1, le=20000)
    fps: float | None = Field(default=24.0, ge=1.0, le=240.0)
    estimated_vram_mb: int | None = Field(default=None, ge=256, le=131072)
    reserve_vram_mb: int | None = Field(default=None, ge=0, le=131072)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanComfyUIWorkflowBindingRequest(BaseModel):
    """Bind a digital human job to a ComfyUI workflow template and local assets."""

    template_id: str = Field(default="liveportrait-musetalk-broll", max_length=128)
    material_asset_ids: list[UUID] | None = None
    reference_asset_ids: list[UUID] | None = None
    resource_profile: str | None = Field(default=None, max_length=64)
    width: int | None = Field(default=1080, ge=64, le=8192)
    height: int | None = Field(default=1920, ge=64, le=8192)
    frames: int | None = Field(default=None, ge=1, le=20000)
    fps: float | None = Field(default=24.0, ge=1.0, le=240.0)
    estimated_vram_mb: int | None = Field(default=None, ge=256, le=131072)
    reserve_vram_mb: int | None = Field(default=None, ge=0, le=131072)
    operator_parameters: dict[str, Any] = Field(default_factory=dict)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanComfyUIWorkflowReadinessRequest(BaseModel):
    """Record operator evidence that a bound ComfyUI workflow is ready for guarded execution."""

    operator_imported_workflow: bool = False
    installed_nodes: list[str] = Field(default_factory=list)
    installed_models: list[str] = Field(default_factory=list)
    uploaded_asset_ids: list[UUID] = Field(default_factory=list)
    comfyui_base_url: str | None = Field(default=None, max_length=1024)
    output_watch_path: str | None = Field(default=None, max_length=2048)
    gpu_name: str | None = Field(default=None, max_length=255)
    free_vram_mb: int | None = Field(default=None, ge=0, le=262144)
    queue_depth: int | None = Field(default=None, ge=0, le=100000)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanShotExecutionPlanRequest(BaseModel):
    """Prepare per-shot render contracts from an LLM creative plan."""

    template_id: str = Field(default="wan-i2v-reference-avatar", max_length=128)
    resource_profile: str = Field(default="production", max_length=64)
    width: int = Field(default=1080, ge=64, le=8192)
    height: int = Field(default=1920, ge=64, le=8192)
    fps: float = Field(default=24.0, ge=1.0, le=240.0)
    quality_profile: str = Field(default="production", max_length=64)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanComfyUIOutputIngestionRequest(BaseModel):
    """Ingest linked ComfyUI outputs as a digital human delivery asset."""

    comfyui_video_job_id: UUID | None = None
    refresh_comfyui_job: bool = True
    poll_history: bool = True
    resubmit_if_waiting: bool = False
    asset_name: str | None = Field(default=None, max_length=255)
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanVideoJobActionRequest(BaseModel):
    """Apply a human review action to a digital human job."""

    reviewer_notes: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanVideoJobResponse(BaseModel):
    """Persisted digital human video job."""

    success: bool = True
    id: UUID
    workspace_id: str
    user_id: str | None = None
    job_status: str
    provider: str
    execution_mode: str
    avatar_asset_id: UUID | None = None
    material_asset_ids: list[str] = Field(default_factory=list)
    reference_asset_ids: list[str] = Field(default_factory=list)
    objective: str
    script: str
    target_channels: list[str] = Field(default_factory=list)
    voice_profile: dict[str, Any] = Field(default_factory=dict)
    aspect_ratio: str
    duration_seconds: float | None = None
    scene_plan: list[dict[str, Any]] = Field(default_factory=list)
    provider_request: dict[str, Any] = Field(default_factory=dict)
    provider_response: dict[str, Any] = Field(default_factory=dict)
    outputs: list[dict[str, Any]] = Field(default_factory=list)
    approval_status: str
    consent_required: bool
    consent_status: str
    external_request_attempted: bool
    provider_calls_enabled: bool
    failure_reason: str | None = None
    result_summary: str | None = None
    progress_percent: int = 0
    current_stage: str = "intake"
    next_action: str | None = None
    linked_comfyui_video_job_id: str | None = None
    selected_workflow_template_id: str | None = None
    workflow_binding_status: str | None = None
    workflow_readiness_status: str | None = None
    workflow_asset_upload_status: str | None = None
    workflow_output_watch_status: str | None = None
    workflow_missing_nodes: list[str] = Field(default_factory=list)
    workflow_missing_models: list[str] = Field(default_factory=list)
    shot_execution_plan_status: str | None = None
    shot_execution_plan_count: int = 0
    comfyui_output_ingestion_status: str | None = None
    delivery_asset_id: str | None = None
    delivery_asset_status: str | None = None
    delivery_asset_name: str | None = None
    delivery_source_uri: str | None = None
    delivery_output_count: int = 0
    operator_note: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, job: DigitalHumanVideoJob) -> "DigitalHumanVideoJobResponse":
        return cls(
            id=job.id,
            workspace_id=job.workspace_id,
            user_id=job.user_id,
            job_status=job.job_status,
            provider=job.provider,
            execution_mode=job.execution_mode,
            avatar_asset_id=job.avatar_asset_id,
            material_asset_ids=job.material_asset_ids or [],
            reference_asset_ids=job.reference_asset_ids or [],
            objective=job.objective,
            script=job.script,
            target_channels=job.target_channels or [],
            voice_profile=job.voice_profile or {},
            aspect_ratio=job.aspect_ratio,
            duration_seconds=job.duration_seconds,
            scene_plan=job.scene_plan or [],
            provider_request=job.provider_request or {},
            provider_response=job.provider_response or {},
            outputs=job.outputs or [],
            approval_status=job.approval_status,
            consent_required=job.consent_required,
            consent_status=job.consent_status,
            external_request_attempted=job.external_request_attempted,
            provider_calls_enabled=job.provider_calls_enabled,
            failure_reason=job.failure_reason,
            result_summary=job.result_summary,
            progress_percent=_digital_human_progress_percent(job.job_status),
            current_stage=_digital_human_current_stage(job.job_status),
            next_action=_digital_human_next_action(job.job_status),
            linked_comfyui_video_job_id=_linked_comfyui_video_job_id(job.outputs or []),
            selected_workflow_template_id=_selected_workflow_template_id(job.job_metadata or {}),
            workflow_binding_status=_workflow_binding_status(job.job_metadata or {}),
            workflow_readiness_status=_workflow_readiness_status(job.job_metadata or {}),
            workflow_asset_upload_status=_workflow_asset_upload_status(job.job_metadata or {}),
            workflow_output_watch_status=_workflow_output_watch_status(job.job_metadata or {}),
            workflow_missing_nodes=_workflow_missing_items(job.job_metadata or {}, "missing_nodes"),
            workflow_missing_models=_workflow_missing_items(job.job_metadata or {}, "missing_models"),
            shot_execution_plan_status=_shot_execution_plan_status(job.job_metadata or {}, job.outputs or []),
            shot_execution_plan_count=_shot_execution_plan_count(job.job_metadata or {}, job.outputs or []),
            comfyui_output_ingestion_status=_comfyui_output_ingestion_status(job.job_metadata or {}, job.outputs or []),
            delivery_asset_id=_delivery_output_field(job.outputs or [], "asset_id"),
            delivery_asset_status=_delivery_output_field(job.outputs or [], "status"),
            delivery_asset_name=_delivery_output_field(job.outputs or [], "asset_name"),
            delivery_source_uri=_delivery_output_field(job.outputs or [], "source_uri"),
            delivery_output_count=_delivery_output_count(job.outputs or []),
            operator_note=job.operator_note,
            metadata=job.job_metadata or {},
            created_at=job.created_at,
            updated_at=job.updated_at,
        )


class DigitalHumanVideoJobListResponse(BaseModel):
    """Workspace-scoped digital human job list."""

    success: bool = True
    workspace_id: str
    items: list[DigitalHumanVideoJobResponse] = Field(default_factory=list)


def _digital_human_progress_percent(status: str) -> int:
    return {
        "draft": 5,
        "needs_assets": 10,
        "needs_consent": 20,
        "provider_blocked": 30,
        "planned": 35,
        "ready_for_review": 40,
        "approved": 45,
        "queued_for_comfyui": 60,
        "rendering": 75,
        "completed": 100,
        "failed": 100,
        "cancelled": 100,
        "archived": 100,
    }.get(status, 0)


def _digital_human_current_stage(status: str) -> str:
    return {
        "draft": "intake",
        "needs_assets": "asset_intake",
        "needs_consent": "consent_review",
        "provider_blocked": "runtime_gate",
        "planned": "human_review",
        "ready_for_review": "human_review",
        "approved": "execution_ready",
        "queued_for_comfyui": "comfyui_video_queue",
        "rendering": "video_rendering",
        "completed": "delivery_ready",
        "failed": "recovery",
        "cancelled": "cancelled",
        "archived": "archived",
    }.get(status, "unknown")


def _digital_human_next_action(status: str) -> str:
    return {
        "draft": "Complete the objective, script, portrait, and material inputs.",
        "needs_assets": "Upload and select an authorized portrait asset.",
        "needs_consent": "Confirm explicit portrait authorization before execution.",
        "provider_blocked": "Review provider/runtime gates and retry after configuration is ready.",
        "planned": "Approve the planned digital human video job.",
        "ready_for_review": "Approve or reject the digital human video job.",
        "approved": "Execute mock delivery or create a guarded ComfyUI video handoff.",
        "queued_for_comfyui": "Refresh and ingest the linked ComfyUI video job until output is ready.",
        "rendering": "Ingest generated ComfyUI media as a digital human delivery asset.",
        "completed": "Use the generated delivery asset in the commercial operation loop.",
        "failed": "Review failure reason and retry from the last safe state.",
        "cancelled": "Create a new job if the campaign still needs a video.",
        "archived": "No action required.",
    }.get(status, "Review the digital human job state.")


def _linked_comfyui_video_job_id(outputs: list[dict[str, Any]]) -> str | None:
    for output in reversed(outputs):
        candidate = output.get("comfyui_video_job_id")
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def _selected_workflow_template_id(metadata: dict[str, Any]) -> str | None:
    binding = metadata.get("comfyui_workflow_binding")
    if isinstance(binding, dict):
        template_id = binding.get("template_id")
        if isinstance(template_id, str) and template_id.strip():
            return template_id.strip()
    return None


def _workflow_binding_status(metadata: dict[str, Any]) -> str | None:
    binding = metadata.get("comfyui_workflow_binding")
    if isinstance(binding, dict):
        status = binding.get("status")
        if isinstance(status, str) and status.strip():
            return status.strip()
    return None


def _workflow_readiness(metadata: dict[str, Any]) -> dict[str, Any]:
    readiness = metadata.get("comfyui_workflow_readiness")
    return readiness if isinstance(readiness, dict) else {}


def _workflow_readiness_status(metadata: dict[str, Any]) -> str | None:
    status = _workflow_readiness(metadata).get("status")
    if isinstance(status, str) and status.strip():
        return status.strip()
    return None


def _workflow_asset_upload_status(metadata: dict[str, Any]) -> str | None:
    status = _workflow_readiness(metadata).get("asset_upload_status")
    if isinstance(status, str) and status.strip():
        return status.strip()
    return None


def _workflow_output_watch_status(metadata: dict[str, Any]) -> str | None:
    output_watch = _workflow_readiness(metadata).get("output_watch")
    if isinstance(output_watch, dict):
        status = output_watch.get("status")
        if isinstance(status, str) and status.strip():
            return status.strip()
    return None


def _workflow_missing_items(metadata: dict[str, Any], key: str) -> list[str]:
    items = _workflow_readiness(metadata).get(key)
    if not isinstance(items, list):
        return []
    return [str(item) for item in items if str(item).strip()]


def _shot_execution_plan(metadata: dict[str, Any], outputs: list[dict[str, Any]]) -> dict[str, Any]:
    plan = metadata.get("shot_execution_plan")
    if isinstance(plan, dict):
        return plan
    for output in reversed(outputs):
        if output.get("output_type") == "digital_human_shot_execution_plan":
            nested = output.get("shot_execution_plan")
            return nested if isinstance(nested, dict) else output
    return {}


def _shot_execution_plan_status(metadata: dict[str, Any], outputs: list[dict[str, Any]]) -> str | None:
    plan = _shot_execution_plan(metadata, outputs)
    status = plan.get("status")
    if isinstance(status, str) and status.strip():
        return status.strip()
    return None


def _shot_execution_plan_count(metadata: dict[str, Any], outputs: list[dict[str, Any]]) -> int:
    plan = _shot_execution_plan(metadata, outputs)
    shots = plan.get("shots")
    if isinstance(shots, list):
        return len(shots)
    count = plan.get("shot_count")
    return count if isinstance(count, int) else 0


def _delivery_output(outputs: list[dict[str, Any]]) -> dict[str, Any]:
    for output in reversed(outputs):
        if output.get("output_type") == "digital_human_comfyui_delivery_asset":
            return output
    for output in reversed(outputs):
        if output.get("output_type") == "digital_human_delivery_manifest":
            return output
    return {}


def _delivery_output_field(outputs: list[dict[str, Any]], key: str) -> str | None:
    value = _delivery_output(outputs).get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _delivery_output_count(outputs: list[dict[str, Any]]) -> int:
    delivery = _delivery_output(outputs)
    output_count = delivery.get("output_count")
    if isinstance(output_count, int):
        return max(0, output_count)
    nested = delivery.get("outputs")
    if isinstance(nested, list):
        return len(nested)
    return 1 if delivery else 0


def _comfyui_output_ingestion_status(metadata: dict[str, Any], outputs: list[dict[str, Any]]) -> str | None:
    ingestion = metadata.get("comfyui_output_ingestion")
    if isinstance(ingestion, dict):
        status = ingestion.get("status")
        if isinstance(status, str) and status.strip():
            return status.strip()
    for output in reversed(outputs):
        if output.get("output_type") in {"digital_human_comfyui_delivery_asset", "digital_human_comfyui_output_ingestion"}:
            status = output.get("status")
            if isinstance(status, str) and status.strip():
                return status.strip()
    return None
