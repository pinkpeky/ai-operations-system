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
    operator_note: str | None = Field(default=None, max_length=2000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class DigitalHumanVideoJobRefreshRequest(BaseModel):
    """Refresh a digital human job from the configured provider boundary."""

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
