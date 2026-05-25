"""Digital human production service foundation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.comfyui_runtime import ComfyUIRuntimeService
from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.models.digital_human import DigitalHumanAsset, DigitalHumanVideoJob
from app.schemas.digital_human import (
    DigitalHumanAssetListResponse,
    DigitalHumanAssetResponse,
    DigitalHumanCapabilitiesResponse,
    DigitalHumanWorkflowTemplateListResponse,
    DigitalHumanWorkflowTemplateResponse,
    DigitalHumanVideoJobListResponse,
    DigitalHumanVideoJobResponse,
)


DIGITAL_HUMAN_ASSET_TYPES = {
    "portrait",
    "material",
    "product_image",
    "reference_image",
    "background",
    "script",
    "audio",
    "video",
    "broll",
}
DIGITAL_HUMAN_CONSENT_STATUSES = {"authorized", "unverified", "missing", "revoked"}
DIGITAL_HUMAN_JOB_STATUSES = {
    "draft",
    "needs_assets",
    "needs_consent",
    "planned",
    "provider_blocked",
    "ready_for_review",
    "approved",
    "queued_for_comfyui",
    "rendering",
    "completed",
    "failed",
    "cancelled",
    "archived",
}
DIGITAL_HUMAN_PROVIDER_ORDER = ["heygen", "tavus", "local_musetalk_liveportrait", "mock"]
DIGITAL_HUMAN_WORKFLOW_TEMPLATES: list[dict[str, Any]] = [
    {
        "template_id": "liveportrait-musetalk-broll",
        "name": "LivePortrait + MuseTalk product b-roll",
        "workflow_kind": "portrait_photo_script_to_short_video",
        "recommended_use": "A product-facing short video from one authorized portrait, script audio, and product/reference images.",
        "default_resource_profile": "standard",
        "recommended_vram_mb": 12288,
        "required_assets": ["authorized portrait image", "script or generated voice audio", "product/reference images"],
        "required_nodes": [
            "ComfyUI-AdvancedLivePortrait",
            "ComfyUI-MuseTalk",
            "ComfyUI-VideoHelperSuite",
            "ComfyUI-Impact-Pack",
            "ComfyUI-Manager",
        ],
        "required_models": [
            "LivePortrait base models",
            "MuseTalk sync model",
            "face landmark / face detector models",
            "SDXL or FLUX image model for product b-roll",
            "video interpolation or frame composition model as selected by operator",
        ],
        "plugin_installation": [
            {"name": "ComfyUI-Manager", "purpose": "install and audit custom nodes"},
            {"name": "ComfyUI-AdvancedLivePortrait", "purpose": "drive portrait animation from reference motion"},
            {"name": "ComfyUI-MuseTalk", "purpose": "audio/lip-sync pass for talking-head segments"},
            {"name": "ComfyUI-VideoHelperSuite", "purpose": "load, combine, and export frame/video sequences"},
            {"name": "ComfyUI-Impact-Pack", "purpose": "face detection, segmentation, and crop helpers"},
        ],
        "model_installation": [
            {"name": "LivePortrait", "target": "ComfyUI/models/liveportrait", "required": True},
            {"name": "MuseTalk", "target": "ComfyUI/models/musetalk", "required": True},
            {"name": "face_analysis", "target": "ComfyUI/models/insightface", "required": True},
            {"name": "base image/video model", "target": "ComfyUI/models/checkpoints", "required": True},
        ],
        "input_slots": [
            {"slot": "avatar_portrait", "asset_types": ["portrait"], "required": True, "comfyui_upload_kind": "image", "node_hint": "LoadImage.image"},
            {"slot": "script_text", "asset_types": ["script"], "required": True, "comfyui_upload_kind": "text", "node_hint": "TTS.prompt"},
            {"slot": "product_materials", "asset_types": ["material", "product_image", "reference_image", "background"], "required": False, "comfyui_upload_kind": "image_or_video", "node_hint": "LoadImage/LoadVideo"},
            {"slot": "voice_audio", "asset_types": ["audio", "voice"], "required": False, "comfyui_upload_kind": "audio", "node_hint": "LoadAudio.audio"},
        ],
        "output_slots": [
            {"slot": "avatar_segment", "media_type": "video"},
            {"slot": "product_broll", "media_type": "video"},
            {"slot": "composited_delivery", "media_type": "video"},
        ],
        "guardrails": [
            "Do not submit until the operator verifies installed custom nodes and model paths.",
            "Portrait consent must remain authorized.",
            "Generated media still requires human review before publishing.",
        ],
    },
    {
        "template_id": "wan-i2v-reference-avatar",
        "name": "Reference image to video avatar / b-roll",
        "workflow_kind": "reference_image_to_video",
        "recommended_use": "Higher-motion product/avatar clips when the server has enough VRAM and a WAN/I2V workflow installed.",
        "default_resource_profile": "high_vram",
        "recommended_vram_mb": 24576,
        "required_assets": ["authorized portrait image", "reference/product image", "script direction"],
        "required_nodes": ["ComfyUI-VideoHelperSuite", "WAN video custom nodes or operator-imported I2V workflow", "ComfyUI-Manager"],
        "required_models": ["WAN image-to-video model", "VAE/text encoder pair required by the chosen WAN workflow"],
        "plugin_installation": [
            {"name": "ComfyUI-Manager", "purpose": "install and audit custom nodes"},
            {"name": "WAN/I2V workflow nodes", "purpose": "operator-selected image-to-video pipeline"},
            {"name": "ComfyUI-VideoHelperSuite", "purpose": "video combine/export"},
        ],
        "model_installation": [
            {"name": "WAN/I2V model", "target": "ComfyUI/models/diffusion_models or workflow-specific model folder", "required": True},
            {"name": "matching VAE/text encoder", "target": "ComfyUI/models/vae and text_encoders", "required": True},
        ],
        "input_slots": [
            {"slot": "avatar_portrait", "asset_types": ["portrait"], "required": True, "comfyui_upload_kind": "image", "node_hint": "LoadImage.image"},
            {"slot": "reference_image", "asset_types": ["reference_image", "product_image", "material"], "required": True, "comfyui_upload_kind": "image", "node_hint": "LoadImage.image"},
            {"slot": "script_direction", "asset_types": ["script"], "required": True, "comfyui_upload_kind": "text", "node_hint": "Prompt.text"},
        ],
        "output_slots": [
            {"slot": "generated_motion_clip", "media_type": "video"},
            {"slot": "delivery_candidate", "media_type": "video"},
        ],
        "guardrails": [
            "Use only when GPU admission shows enough free VRAM.",
            "Keep prompt submission disabled until the real imported workflow graph has been reviewed.",
            "No publishing or account control is included.",
        ],
    },
    {
        "template_id": "talking-head-fast-proof",
        "name": "Fast talking-head proof",
        "workflow_kind": "fast_avatar_proof",
        "recommended_use": "A lower-cost proof pass to validate portrait authorization, script timing, and review flow before high-VRAM generation.",
        "default_resource_profile": "low_vram",
        "recommended_vram_mb": 8192,
        "required_assets": ["authorized portrait image", "script"],
        "required_nodes": ["ComfyUI-VideoHelperSuite", "operator-selected talking-head workflow"],
        "required_models": ["operator-selected talking-head or lip-sync model"],
        "plugin_installation": [
            {"name": "ComfyUI-VideoHelperSuite", "purpose": "video combine/export"},
            {"name": "talking-head workflow nodes", "purpose": "operator-installed lightweight proof workflow"},
        ],
        "model_installation": [
            {"name": "talking-head proof model", "target": "workflow-specific model folder", "required": True},
        ],
        "input_slots": [
            {"slot": "avatar_portrait", "asset_types": ["portrait"], "required": True, "comfyui_upload_kind": "image", "node_hint": "LoadImage.image"},
            {"slot": "script_text", "asset_types": ["script"], "required": True, "comfyui_upload_kind": "text", "node_hint": "Prompt.text"},
        ],
        "output_slots": [{"slot": "proof_video", "media_type": "video"}],
        "guardrails": [
            "Use as a validation pass before high-cost video generation.",
            "Do not treat proof output as final without human review.",
        ],
    },
]


class DigitalHumanService:
    """Workspace-scoped digital human asset and video job service."""

    def __init__(self, *, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()

    def capabilities(self, *, workspace_id: str | None = None) -> DigitalHumanCapabilitiesResponse:
        """Return provider readiness and safety boundary without external calls."""

        provider = self._provider()
        enabled = bool(getattr(self.settings, "digital_human_enabled", False))
        external_allowed = bool(getattr(self.settings, "digital_human_allow_external_api", False))
        provider_calls_enabled = bool(enabled and (provider == "mock" or external_allowed or provider.startswith("local_")))
        disabled_actions = []
        if not enabled:
            disabled_actions.append("execute_digital_human_provider")
        if not external_allowed:
            disabled_actions.extend(["call_heygen_api", "call_tavus_api", "call_did_api"])
        if provider == "mock":
            disabled_actions.append("mark_video_completed_from_mock")
        return DigitalHumanCapabilitiesResponse(
            provider=provider,
            enabled=enabled,
            external_api_allowed=external_allowed,
            provider_calls_enabled=provider_calls_enabled,
            available_providers=["mock", "heygen", "tavus", "did", "local_musetalk_liveportrait"],
            recommended_provider_order=DIGITAL_HUMAN_PROVIDER_ORDER,
            local_pipeline=["tts", "liveportrait", "musetalk", "comfyui_broll", "ffmpeg_compose"],
            required_assets=["authorized portrait", "script", "voice profile", "product/reference materials"],
            disabled_actions=disabled_actions,
            guardrails=[
                "Portrait assets require explicit authorization before provider execution.",
                "Default mode stores plans and assets but does not call external avatar APIs.",
                "ComfyUI workflow templates are binding contracts until an operator imports and verifies the real graph.",
                "Generated videos must go through human review before publishing.",
            ],
            workspace_id=workspace_id,
            raw={
                "phase": "67C",
                "no_external_call_performed": True,
                "asset_types": sorted(DIGITAL_HUMAN_ASSET_TYPES),
                "execution_modes": ["mock_render", "comfyui_handoff"],
                "workflow_template_ids": [str(template["template_id"]) for template in DIGITAL_HUMAN_WORKFLOW_TEMPLATES],
            },
        )

    def list_workflow_templates(self, *, workspace_id: str | None = None) -> DigitalHumanWorkflowTemplateListResponse:
        """Return built-in ComfyUI workflow template contracts without calling ComfyUI."""

        return DigitalHumanWorkflowTemplateListResponse(
            workspace_id=workspace_id,
            items=[self._workflow_template_response(template) for template in DIGITAL_HUMAN_WORKFLOW_TEMPLATES],
        )

    def get_workflow_template(self, *, template_id: str) -> DigitalHumanWorkflowTemplateResponse:
        """Return one built-in ComfyUI workflow template contract."""

        return self._workflow_template_response(self._workflow_template(template_id))

    async def create_asset(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        user_id: str | None,
        asset_type: str,
        name: str | None,
        file_name: str,
        mime_type: str | None,
        content: bytes,
        consent_status: str = "unverified",
        usage_scope: str | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> DigitalHumanAssetResponse:
        """Persist an uploaded person/material asset and write its binary payload to local storage."""

        normalized_type = self._normalize_asset_type(asset_type)
        normalized_consent = self._normalize_consent_status(consent_status)
        if not content:
            raise AppError("Digital human asset upload is empty", status_code=400)
        if normalized_type == "portrait" and mime_type and not mime_type.lower().startswith("image/"):
            raise AppError("Portrait assets must be image files", status_code=400)

        storage_root = Path(str(getattr(self.settings, "digital_human_asset_dir", "storage/digital_human_assets")))
        workspace_dir = storage_root / self._safe_path_part(workspace_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        suffix = Path(file_name).suffix.lower()[:16]
        stored_name = f"{uuid4()}{suffix}"
        stored_path = workspace_dir / stored_name
        stored_path.write_bytes(content)
        checksum = sha256(content).hexdigest()

        asset = DigitalHumanAsset(
            workspace_id=workspace_id,
            user_id=user_id,
            asset_type=normalized_type,
            asset_status="available",
            name=(name or Path(file_name).stem or normalized_type).strip()[:255],
            source_uri=str(stored_path.as_posix()),
            file_name=file_name,
            mime_type=mime_type,
            size_bytes=len(content),
            checksum=checksum,
            consent_status=normalized_consent,
            usage_scope=usage_scope,
            operator_note=operator_note,
            asset_metadata={
                **dict(metadata or {}),
                "phase": "67A",
                "source": "digital_human_asset_upload",
                "stored_name": stored_name,
            },
        )
        session.add(asset)
        await session.commit()
        await session.refresh(asset)
        return DigitalHumanAssetResponse.from_model(asset)

    async def list_assets(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        asset_type: str | None = None,
        limit: int = 50,
    ) -> DigitalHumanAssetListResponse:
        """List digital human assets for a workspace."""

        statement = select(DigitalHumanAsset).where(DigitalHumanAsset.workspace_id == workspace_id)
        if asset_type:
            statement = statement.where(DigitalHumanAsset.asset_type == self._normalize_asset_type(asset_type))
        statement = statement.order_by(DigitalHumanAsset.created_at.desc()).limit(limit)
        result = await session.execute(statement)
        return DigitalHumanAssetListResponse(
            workspace_id=workspace_id,
            items=[DigitalHumanAssetResponse.from_model(asset) for asset in result.scalars().all()],
        )

    async def get_asset(self, session: AsyncSession, *, workspace_id: str, asset_id: UUID) -> DigitalHumanAssetResponse:
        """Return one digital human asset by id."""

        asset = await self._get_asset_model(session, workspace_id=workspace_id, asset_id=asset_id)
        return DigitalHumanAssetResponse.from_model(asset)

    async def create_video_job(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        user_id: str | None,
        objective: str,
        script: str,
        provider: str | None = None,
        avatar_asset_id: UUID | None = None,
        material_asset_ids: Sequence[UUID] | None = None,
        reference_asset_ids: Sequence[UUID] | None = None,
        target_channels: Sequence[str] | None = None,
        voice_profile: Mapping[str, object] | None = None,
        aspect_ratio: str = "9:16",
        duration_seconds: float | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> DigitalHumanVideoJobResponse:
        """Create a recoverable digital human video job plan."""

        normalized_provider = self._normalize_provider(provider)
        avatar_asset = None
        if avatar_asset_id:
            avatar_asset = await self._get_asset_model(session, workspace_id=workspace_id, asset_id=avatar_asset_id)
        material_ids = [str(asset_id) for asset_id in material_asset_ids or []]
        reference_ids = [str(asset_id) for asset_id in reference_asset_ids or []]
        consent_status = avatar_asset.consent_status if avatar_asset else "missing"
        job_status = self._initial_job_status(provider=normalized_provider, avatar_asset=avatar_asset)
        provider_calls_enabled = self._provider_calls_enabled(normalized_provider)
        scene_plan = self._build_scene_plan(
            status=job_status,
            provider=normalized_provider,
            has_avatar=avatar_asset is not None,
            material_count=len(material_ids),
            reference_count=len(reference_ids),
        )
        provider_request = {
            "provider": normalized_provider,
            "objective": objective.strip(),
            "script": script.strip(),
            "avatar_asset_id": str(avatar_asset_id) if avatar_asset_id else None,
            "material_asset_ids": material_ids,
            "reference_asset_ids": reference_ids,
            "target_channels": list(target_channels or []),
            "voice_profile": dict(voice_profile or {}),
            "aspect_ratio": aspect_ratio,
            "duration_seconds": duration_seconds,
            "pipeline": ["script", "tts", "avatar_motion", "broll", "ffmpeg_compose", "human_review"],
        }
        job = DigitalHumanVideoJob(
            workspace_id=workspace_id,
            user_id=user_id,
            job_status=job_status,
            provider=normalized_provider,
            execution_mode="provider_ready" if provider_calls_enabled and job_status == "planned" else "plan_only",
            avatar_asset_id=avatar_asset_id,
            material_asset_ids=material_ids,
            reference_asset_ids=reference_ids,
            objective=objective.strip(),
            script=script.strip(),
            target_channels=list(target_channels or []),
            voice_profile=dict(voice_profile or {}),
            aspect_ratio=aspect_ratio,
            duration_seconds=duration_seconds,
            scene_plan=scene_plan,
            provider_request=provider_request,
            provider_response=self._provider_response_stub(status=job_status, provider=normalized_provider),
            outputs=[],
            approval_status="pending",
            consent_required=True,
            consent_status=consent_status,
            external_request_attempted=False,
            provider_calls_enabled=provider_calls_enabled,
            failure_reason=self._failure_reason(status=job_status, provider=normalized_provider, consent_status=consent_status),
            result_summary=self._result_summary(status=job_status, provider=normalized_provider),
            operator_note=operator_note,
            job_metadata={
                **dict(metadata or {}),
                "phase": "67A",
                "source": "digital_human_video_job",
            },
        )
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return DigitalHumanVideoJobResponse.from_model(job)

    async def list_video_jobs(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        status: str | None = None,
        limit: int = 50,
    ) -> DigitalHumanVideoJobListResponse:
        """List digital human video jobs for a workspace."""

        statement = select(DigitalHumanVideoJob).where(DigitalHumanVideoJob.workspace_id == workspace_id)
        if status:
            statement = statement.where(DigitalHumanVideoJob.job_status == status)
        statement = statement.order_by(DigitalHumanVideoJob.created_at.desc()).limit(limit)
        result = await session.execute(statement)
        return DigitalHumanVideoJobListResponse(
            workspace_id=workspace_id,
            items=[DigitalHumanVideoJobResponse.from_model(job) for job in result.scalars().all()],
        )

    async def get_video_job(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
    ) -> DigitalHumanVideoJobResponse:
        """Return one digital human video job by id."""

        job = await self._get_video_job_model(session, workspace_id=workspace_id, job_id=job_id)
        return DigitalHumanVideoJobResponse.from_model(job)

    async def bind_comfyui_workflow(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
        template_id: str,
        material_asset_ids: Sequence[UUID] | None = None,
        reference_asset_ids: Sequence[UUID] | None = None,
        resource_profile: str | None = None,
        width: int | None = 1080,
        height: int | None = 1920,
        frames: int | None = None,
        fps: float | None = 24.0,
        estimated_vram_mb: int | None = None,
        reserve_vram_mb: int | None = None,
        operator_parameters: Mapping[str, Any] | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> DigitalHumanVideoJobResponse:
        """Bind a digital human job to a ComfyUI workflow template and local input assets."""

        job = await self._get_video_job_model(session, workspace_id=workspace_id, job_id=job_id)
        if job.job_status in {"completed", "failed", "cancelled", "archived"}:
            raise AppError("Terminal digital human jobs cannot be rebound to a ComfyUI workflow", status_code=400)
        if not job.avatar_asset_id:
            raise AppError("Workflow binding requires an uploaded portrait asset", status_code=400)
        avatar_asset = await self._get_asset_model(session, workspace_id=workspace_id, asset_id=job.avatar_asset_id)
        if avatar_asset.consent_status != "authorized":
            raise AppError("Workflow binding requires authorized portrait consent", status_code=400)

        template = self._workflow_template(template_id)
        material_ids = [str(asset_id) for asset_id in material_asset_ids] if material_asset_ids is not None else list(job.material_asset_ids or [])
        reference_ids = [str(asset_id) for asset_id in reference_asset_ids] if reference_asset_ids is not None else list(job.reference_asset_ids or [])
        bound_material_assets = await self._load_assets_by_ids(session, workspace_id=workspace_id, asset_ids=material_ids)
        bound_reference_assets = await self._load_assets_by_ids(session, workspace_id=workspace_id, asset_ids=reference_ids)
        binding = self._build_comfyui_workflow_binding(
            job=job,
            template=template,
            avatar_asset=avatar_asset,
            material_assets=bound_material_assets,
            reference_assets=bound_reference_assets,
            resource_profile=resource_profile,
            width=width,
            height=height,
            frames=frames,
            fps=fps,
            estimated_vram_mb=estimated_vram_mb,
            reserve_vram_mb=reserve_vram_mb,
            operator_parameters=operator_parameters,
            operator_note=operator_note,
            metadata=metadata,
        )
        output_record = {
            "output_type": "digital_human_comfyui_input_binding",
            "media_type": "video",
            "status": binding["status"],
            "workflow_template_id": binding["template_id"],
            "workflow_template_name": binding["template_name"],
            "input_asset_count": len(binding["input_assets"]),
            "missing_inputs": binding["missing_inputs"],
            "required_nodes": template.get("required_nodes", []),
            "required_models": template.get("required_models", []),
            "created_at": binding["created_at"],
        }
        job.material_asset_ids = material_ids
        job.reference_asset_ids = reference_ids
        job.outputs = self._upsert_output(
            job.outputs or [],
            output_record,
            key="output_type",
            value="digital_human_comfyui_input_binding",
        )
        job.provider_request = {
            **(job.provider_request or {}),
            "comfyui_workflow_binding": {
                "template_id": binding["template_id"],
                "template_name": binding["template_name"],
                "status": binding["status"],
                "resource_profile": binding["resource_plan"]["resource_profile"],
                "input_asset_count": len(binding["input_assets"]),
                "submit_policy": binding["submit_policy"],
            },
        }
        job.provider_response = {
            "phase": "67C",
            "provider": job.provider,
            "execution_mode": job.execution_mode,
            "workflow_template_id": binding["template_id"],
            "workflow_binding_status": binding["status"],
            "external_request_attempted": False,
        }
        job.external_request_attempted = False
        job.failure_reason = None if binding["status"] == "ready_for_operator_review" else "; ".join(binding["missing_inputs"])
        job.result_summary = (
            "ComfyUI workflow inputs are bound and ready for operator graph verification."
            if binding["status"] == "ready_for_operator_review"
            else "ComfyUI workflow binding needs missing inputs before handoff."
        )
        job.operator_note = operator_note or job.operator_note
        job.job_metadata = {
            **(job.job_metadata or {}),
            **dict(metadata or {}),
            "phase": "67C",
            "comfyui_workflow_binding": binding,
            "workflow_binding_status": binding["status"],
            "selected_workflow_template_id": binding["template_id"],
        }
        job.scene_plan = self._build_scene_plan(
            status=job.job_status,
            provider=job.provider,
            has_avatar=True,
            material_count=len(material_ids),
            reference_count=len(reference_ids),
        )
        await session.commit()
        await session.refresh(job)
        return DigitalHumanVideoJobResponse.from_model(job)

    async def refresh_video_job(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
        metadata: Mapping[str, object] | None = None,
    ) -> DigitalHumanVideoJobResponse:
        """Refresh a digital human job without performing external provider calls by default."""

        job = await self._get_video_job_model(session, workspace_id=workspace_id, job_id=job_id)
        provider_calls_enabled = self._provider_calls_enabled(job.provider)
        job.provider_calls_enabled = provider_calls_enabled
        job.external_request_attempted = False
        if job.job_status not in {"completed", "failed", "cancelled", "archived"}:
            if job.consent_status != "authorized":
                job.job_status = "needs_consent" if job.avatar_asset_id else "needs_assets"
            elif job.provider != "mock" and not provider_calls_enabled:
                job.job_status = "provider_blocked"
            elif job.job_status in {"draft", "needs_assets", "needs_consent", "provider_blocked"}:
                job.job_status = "planned"
        job.scene_plan = self._build_scene_plan(
            status=job.job_status,
            provider=job.provider,
            has_avatar=job.avatar_asset_id is not None,
            material_count=len(job.material_asset_ids or []),
            reference_count=len(job.reference_asset_ids or []),
        )
        job.provider_response = self._provider_response_stub(status=job.job_status, provider=job.provider)
        job.failure_reason = self._failure_reason(
            status=job.job_status,
            provider=job.provider,
            consent_status=job.consent_status,
        )
        job.result_summary = self._result_summary(status=job.job_status, provider=job.provider)
        job.job_metadata = {
            **(job.job_metadata or {}),
            **dict(metadata or {}),
            "phase": "67A",
            "refresh_attempted": True,
        }
        await session.commit()
        await session.refresh(job)
        return DigitalHumanVideoJobResponse.from_model(job)

    async def update_video_job_review(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
        action: str,
        reviewer_notes: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> DigitalHumanVideoJobResponse:
        """Approve or reject a digital human job for the next execution phase."""

        normalized_action = action.strip().lower()
        if normalized_action not in {"approve", "reject", "cancel"}:
            raise AppError("Unsupported digital human review action", status_code=400)
        job = await self._get_video_job_model(session, workspace_id=workspace_id, job_id=job_id)
        if normalized_action == "approve":
            if job.job_status not in {"planned", "ready_for_review"}:
                raise AppError("Only planned digital human jobs can be approved", status_code=400)
            job.approval_status = "approved"
            job.job_status = "approved"
        elif normalized_action == "reject":
            job.approval_status = "rejected"
            job.job_status = "planned"
        else:
            job.approval_status = "cancelled"
            job.job_status = "cancelled"
        job.job_metadata = {
            **(job.job_metadata or {}),
            **dict(metadata or {}),
            "reviewer_notes": reviewer_notes,
            "review_action": normalized_action,
        }
        job.result_summary = self._result_summary(status=job.job_status, provider=job.provider)
        await session.commit()
        await session.refresh(job)
        return DigitalHumanVideoJobResponse.from_model(job)

    async def execute_video_job(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job_id: UUID,
        execution_mode: str = "mock_render",
        submit_immediately: bool = False,
        poll_history: bool = True,
        prompt: Mapping[str, Any] | None = None,
        workflow: Mapping[str, Any] | None = None,
        resource_profile: str = "standard",
        width: int | None = 1080,
        height: int | None = 1920,
        frames: int | None = None,
        fps: float | None = 24.0,
        estimated_vram_mb: int | None = None,
        reserve_vram_mb: int | None = None,
        operator_note: str | None = None,
        metadata: Mapping[str, object] | None = None,
    ) -> DigitalHumanVideoJobResponse:
        """Execute an approved job as a local delivery artifact or a guarded ComfyUI video handoff."""

        job = await self._get_video_job_model(session, workspace_id=workspace_id, job_id=job_id)
        if job.approval_status != "approved" or job.job_status not in {"approved", "rendering", "queued_for_comfyui"}:
            raise AppError("Only approved digital human jobs can be executed", status_code=400)
        if job.consent_status != "authorized":
            raise AppError("Digital human execution requires authorized portrait consent", status_code=400)

        normalized_mode = str(execution_mode or "mock_render").strip().lower()
        if normalized_mode in {"mock", "local_manifest", "delivery_manifest"}:
            normalized_mode = "mock_render"
        if normalized_mode in {"comfyui", "comfyui_video", "comfyui_video_job"}:
            normalized_mode = "comfyui_handoff"
        if normalized_mode not in {"mock_render", "comfyui_handoff"}:
            raise AppError("Unsupported digital human execution_mode", status_code=400)

        if normalized_mode == "mock_render":
            await self._execute_mock_render(
                session,
                job=job,
                operator_note=operator_note,
                metadata=metadata,
            )
        else:
            await self._execute_comfyui_handoff(
                session,
                workspace_id=workspace_id,
                job=job,
                submit_immediately=submit_immediately,
                poll_history=poll_history,
                prompt=prompt,
                workflow=workflow,
                resource_profile=resource_profile,
                width=width,
                height=height,
                frames=frames,
                fps=fps,
                estimated_vram_mb=estimated_vram_mb,
                reserve_vram_mb=reserve_vram_mb,
                operator_note=operator_note,
                metadata=metadata,
            )
        await session.commit()
        await session.refresh(job)
        return DigitalHumanVideoJobResponse.from_model(job)

    async def _execute_mock_render(
        self,
        session: AsyncSession,
        *,
        job: DigitalHumanVideoJob,
        operator_note: str | None,
        metadata: Mapping[str, object] | None,
    ) -> None:
        now = datetime.now(timezone.utc)
        output_root = Path(str(getattr(self.settings, "digital_human_output_dir", "storage/digital_human_outputs")))
        workspace_dir = output_root / self._safe_path_part(job.workspace_id)
        workspace_dir.mkdir(parents=True, exist_ok=True)
        file_name = f"digital-human-{job.id}-delivery-manifest.json"
        output_path = workspace_dir / file_name
        merged_metadata = {**(job.job_metadata or {}), **dict(metadata or {})}
        commercial_operation_id = self._string_from_mapping(merged_metadata, "commercial_operation_id")
        manifest = {
            "phase": "67B",
            "generated_at": now.isoformat(),
            "workspace_id": job.workspace_id,
            "job_id": str(job.id),
            "commercial_operation_id": commercial_operation_id,
            "objective": job.objective,
            "script": job.script,
            "provider": job.provider,
            "avatar_asset_id": str(job.avatar_asset_id) if job.avatar_asset_id else None,
            "material_asset_ids": job.material_asset_ids or [],
            "reference_asset_ids": job.reference_asset_ids or [],
            "target_channels": job.target_channels or [],
            "voice_profile": job.voice_profile or {},
            "aspect_ratio": job.aspect_ratio,
            "duration_seconds": job.duration_seconds,
            "scene_plan": self._build_scene_plan(
                status="completed",
                provider=job.provider,
                has_avatar=job.avatar_asset_id is not None,
                material_count=len(job.material_asset_ids or []),
                reference_count=len(job.reference_asset_ids or []),
            ),
            "delivery_assets": [
                {
                    "type": "script",
                    "title": "Approved digital human script",
                    "status": "ready",
                },
                {
                    "type": "video_manifest",
                    "title": "Digital human delivery manifest",
                    "status": "ready",
                },
            ],
            "execution_boundary": "Local delivery manifest only; no external avatar provider, no ComfyUI prompt submission, and no publishing action was performed.",
        }
        content = json.dumps(manifest, ensure_ascii=False, indent=2).encode("utf-8")
        output_path.write_bytes(content)
        checksum = sha256(content).hexdigest()
        asset = DigitalHumanAsset(
            workspace_id=job.workspace_id,
            user_id=job.user_id,
            asset_type="video",
            asset_status="generated",
            name=self._truncate_text(f"{job.objective} delivery manifest", 255),
            source_uri=str(output_path.as_posix()),
            file_name=file_name,
            mime_type="application/json",
            size_bytes=len(content),
            checksum=checksum,
            consent_status=job.consent_status,
            usage_scope="digital human generated delivery output",
            operator_note=operator_note,
            asset_metadata={
                "phase": "67B",
                "source": "digital_human_mock_render",
                "digital_human_video_job_id": str(job.id),
                "commercial_operation_id": commercial_operation_id,
                "output_kind": "delivery_manifest",
            },
        )
        session.add(asset)
        await session.flush()
        output_record = {
            "output_type": "digital_human_delivery_manifest",
            "media_type": "video",
            "status": "ready",
            "asset_id": str(asset.id),
            "source_uri": asset.source_uri,
            "file_name": file_name,
            "checksum": checksum,
            "commercial_operation_id": commercial_operation_id,
            "progress_percent": 100,
            "execution_boundary": manifest["execution_boundary"],
            "created_at": now.isoformat(),
        }
        job.job_status = "completed"
        job.execution_mode = "mock_render"
        job.scene_plan = manifest["scene_plan"]
        job.outputs = [*(job.outputs or []), output_record]
        job.provider_response = {
            "phase": "67B",
            "provider": job.provider,
            "execution_mode": "mock_render",
            "external_request_attempted": False,
            "output_asset_id": str(asset.id),
            "output_manifest": str(output_path.as_posix()),
        }
        job.external_request_attempted = False
        job.failure_reason = None
        job.result_summary = "Digital human delivery manifest is ready and assetized for the commercial operation loop."
        job.operator_note = operator_note or job.operator_note
        job.job_metadata = {
            **merged_metadata,
            "phase": "67B",
            "execution_mode": "mock_render",
            "progress_percent": 100,
            "current_stage": "delivery_ready",
            "last_execution_at": now.isoformat(),
        }

    async def _execute_comfyui_handoff(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        job: DigitalHumanVideoJob,
        submit_immediately: bool,
        poll_history: bool,
        prompt: Mapping[str, Any] | None,
        workflow: Mapping[str, Any] | None,
        resource_profile: str,
        width: int | None,
        height: int | None,
        frames: int | None,
        fps: float | None,
        estimated_vram_mb: int | None,
        reserve_vram_mb: int | None,
        operator_note: str | None,
        metadata: Mapping[str, object] | None,
    ) -> None:
        now = datetime.now(timezone.utc)
        workflow_binding = self._workflow_binding_from_job(job)
        handoff_phase = "67C" if workflow_binding else "67B"
        binding_resource_plan = workflow_binding.get("resource_plan") if isinstance(workflow_binding.get("resource_plan"), Mapping) else {}
        supplied_prompt = bool(prompt)
        prompt_payload = dict(prompt or workflow_binding.get("prompt") or self._build_comfyui_handoff_prompt(job))
        workflow_payload = dict(workflow or workflow_binding.get("workflow") or self._build_comfyui_handoff_workflow(job))
        effective_submit = bool(submit_immediately and supplied_prompt)
        duration_seconds = job.duration_seconds or self._duration_from_frames(frames=frames, fps=fps)
        handoff_resource_profile = resource_profile or str(binding_resource_plan.get("resource_profile") or "standard")
        handoff_width = width if width is not None else binding_resource_plan.get("width")
        handoff_height = height if height is not None else binding_resource_plan.get("height")
        handoff_frames = frames or binding_resource_plan.get("frames")
        handoff_fps = fps if fps is not None else binding_resource_plan.get("fps")
        handoff_estimated_vram_mb = estimated_vram_mb or binding_resource_plan.get("estimated_vram_mb")
        handoff_reserve_vram_mb = reserve_vram_mb if reserve_vram_mb is not None else binding_resource_plan.get("reserve_vram_mb")
        comfyui_job = await ComfyUIRuntimeService(settings=self.settings).create_video_job(
            session,
            workspace_id=workspace_id,
            user_id=job.user_id,
            prompt=prompt_payload,
            workflow=workflow_payload,
            extra_data={
                "digital_human": {
                    "job_id": str(job.id),
                    "objective": job.objective,
                    "avatar_asset_id": str(job.avatar_asset_id) if job.avatar_asset_id else None,
                    "material_asset_ids": job.material_asset_ids or [],
                    "target_channels": job.target_channels or [],
                    "workflow_template_id": workflow_binding.get("template_id"),
                    "workflow_binding_status": workflow_binding.get("status"),
                },
                "aiops_digital_human_handoff": True,
            },
            client_id=f"digital-human-{job.id}",
            resource_profile=str(handoff_resource_profile),
            width=int(handoff_width) if handoff_width is not None else None,
            height=int(handoff_height) if handoff_height is not None else None,
            frames=int(handoff_frames) if handoff_frames is not None else self._frames_from_duration(duration_seconds=duration_seconds, fps=handoff_fps),
            fps=float(handoff_fps) if handoff_fps is not None else None,
            duration_seconds=duration_seconds,
            estimated_vram_mb=int(handoff_estimated_vram_mb) if handoff_estimated_vram_mb is not None else None,
            reserve_vram_mb=int(handoff_reserve_vram_mb) if handoff_reserve_vram_mb is not None else None,
            submit_immediately=effective_submit,
            poll_history=poll_history,
            operator_note=operator_note,
            metadata={
                "phase": handoff_phase,
                "source": "digital_human_comfyui_handoff",
                "digital_human_video_job_id": str(job.id),
                "generated_prompt_submission_skipped": bool(submit_immediately and not supplied_prompt),
                "workflow_template_id": workflow_binding.get("template_id"),
                "workflow_binding_status": workflow_binding.get("status"),
                **dict(metadata or {}),
            },
        )
        output_record = {
            "output_type": "comfyui_video_job",
            "media_type": "video",
            "status": comfyui_job.job_status,
            "comfyui_video_job_id": str(comfyui_job.id),
            "runtime_prompt_id": comfyui_job.runtime_prompt_id,
            "runtime_base_url": comfyui_job.runtime_base_url,
            "resource_plan": comfyui_job.resource_plan,
            "selected_gpu": comfyui_job.selected_gpu,
            "outputs": comfyui_job.outputs,
            "external_request_attempted": comfyui_job.external_request_attempted,
            "prompt_submission_enabled": comfyui_job.prompt_submission_enabled,
            "submit_immediately_requested": submit_immediately,
            "submit_immediately_effective": effective_submit,
            "workflow_template_id": workflow_binding.get("template_id"),
            "workflow_binding_status": workflow_binding.get("status"),
            "created_at": now.isoformat(),
        }
        job.execution_mode = "comfyui_handoff"
        job.job_status = self._digital_status_from_comfyui_status(comfyui_job.job_status)
        job.scene_plan = self._build_scene_plan(
            status=job.job_status,
            provider=job.provider,
            has_avatar=job.avatar_asset_id is not None,
            material_count=len(job.material_asset_ids or []),
            reference_count=len(job.reference_asset_ids or []),
        )
        job.outputs = self._upsert_output(job.outputs or [], output_record, key="output_type", value="comfyui_video_job")
        job.provider_response = {
            "phase": handoff_phase,
            "provider": job.provider,
            "execution_mode": "comfyui_handoff",
            "comfyui_video_job_id": str(comfyui_job.id),
            "comfyui_job_status": comfyui_job.job_status,
            "resource_plan": comfyui_job.resource_plan,
            "external_request_attempted": comfyui_job.external_request_attempted,
            "generated_prompt_submission_skipped": bool(submit_immediately and not supplied_prompt),
            "workflow_template_id": workflow_binding.get("template_id"),
            "workflow_binding_status": workflow_binding.get("status"),
        }
        job.external_request_attempted = comfyui_job.external_request_attempted
        job.failure_reason = comfyui_job.failure_reason or self._comfyui_resource_block_reason(comfyui_job.resource_plan)
        job.result_summary = self._digital_handoff_result_summary(comfyui_status=comfyui_job.job_status)
        job.operator_note = operator_note or job.operator_note
        job.job_metadata = {
            **(job.job_metadata or {}),
            **dict(metadata or {}),
            "phase": handoff_phase,
            "execution_mode": "comfyui_handoff",
            "linked_comfyui_video_job_id": str(comfyui_job.id),
            "selected_workflow_template_id": workflow_binding.get("template_id"),
            "workflow_binding_status": workflow_binding.get("status"),
            "progress_percent": 60 if job.job_status == "queued_for_comfyui" else 75,
            "current_stage": "comfyui_video_queue" if job.job_status == "queued_for_comfyui" else "video_rendering",
            "last_execution_at": now.isoformat(),
        }

    def _workflow_template_response(self, template: Mapping[str, Any]) -> DigitalHumanWorkflowTemplateResponse:
        prompt_contract = {
            "template_id": template["template_id"],
            "contract_type": "operator_verified_comfyui_prompt",
            "input_slots": template.get("input_slots", []),
            "submission_policy": "requires operator-imported graph and guarded ComfyUI runtime gates",
        }
        workflow_contract = {
            "template_id": template["template_id"],
            "workflow_kind": template["workflow_kind"],
            "default_resource_profile": template.get("default_resource_profile", "standard"),
            "output_slots": template.get("output_slots", []),
        }
        return DigitalHumanWorkflowTemplateResponse(
            template_id=str(template["template_id"]),
            name=str(template["name"]),
            workflow_kind=str(template["workflow_kind"]),
            recommended_use=str(template["recommended_use"]),
            provider="comfyui",
            default_resource_profile=str(template.get("default_resource_profile") or "standard"),
            recommended_vram_mb=int(template["recommended_vram_mb"]) if template.get("recommended_vram_mb") else None,
            required_assets=[str(item) for item in template.get("required_assets", [])],
            required_nodes=[str(item) for item in template.get("required_nodes", [])],
            required_models=[str(item) for item in template.get("required_models", [])],
            plugin_installation=list(template.get("plugin_installation", [])),
            model_installation=list(template.get("model_installation", [])),
            input_slots=list(template.get("input_slots", [])),
            output_slots=list(template.get("output_slots", [])),
            guardrails=list(template.get("guardrails", [])),
            prompt_contract=prompt_contract,
            workflow_contract=workflow_contract,
            metadata={
                "phase": "67C",
                "source": "digital_human_builtin_workflow_template",
                "no_external_call_performed": True,
            },
        )

    def _workflow_template(self, template_id: str) -> dict[str, Any]:
        normalized = str(template_id or "").strip().lower()
        for template in DIGITAL_HUMAN_WORKFLOW_TEMPLATES:
            if str(template["template_id"]).lower() == normalized:
                return template
        raise AppError("Digital human workflow template not found", status_code=404)

    async def _load_assets_by_ids(
        self,
        session: AsyncSession,
        *,
        workspace_id: str,
        asset_ids: Sequence[str],
    ) -> list[DigitalHumanAsset]:
        assets: list[DigitalHumanAsset] = []
        for raw_id in asset_ids:
            if not raw_id:
                continue
            try:
                asset_id = UUID(str(raw_id))
            except (TypeError, ValueError) as exc:
                raise AppError("Invalid digital human asset id for workflow binding", status_code=400) from exc
            assets.append(await self._get_asset_model(session, workspace_id=workspace_id, asset_id=asset_id))
        return assets

    def _build_comfyui_workflow_binding(
        self,
        *,
        job: DigitalHumanVideoJob,
        template: Mapping[str, Any],
        avatar_asset: DigitalHumanAsset,
        material_assets: Sequence[DigitalHumanAsset],
        reference_assets: Sequence[DigitalHumanAsset],
        resource_profile: str | None,
        width: int | None,
        height: int | None,
        frames: int | None,
        fps: float | None,
        estimated_vram_mb: int | None,
        reserve_vram_mb: int | None,
        operator_parameters: Mapping[str, Any] | None,
        operator_note: str | None,
        metadata: Mapping[str, object] | None,
    ) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        input_assets = [
            self._asset_binding_record(avatar_asset, slot="avatar_portrait", role="authorized_portrait"),
            *[
                self._asset_binding_record(asset, slot="product_materials", role="material")
                for asset in material_assets
            ],
            *[
                self._asset_binding_record(asset, slot="reference_image", role="reference")
                for asset in reference_assets
            ],
        ]
        missing_inputs = self._workflow_missing_inputs(template=template, input_assets=input_assets, job=job)
        binding_id = f"dhwf-{job.id}-{str(template['template_id'])}"
        resource_plan = {
            "resource_profile": resource_profile or str(template.get("default_resource_profile") or "standard"),
            "width": width,
            "height": height,
            "frames": frames or self._frames_from_duration(duration_seconds=job.duration_seconds, fps=fps),
            "fps": fps,
            "duration_seconds": job.duration_seconds,
            "estimated_vram_mb": estimated_vram_mb or template.get("recommended_vram_mb"),
            "reserve_vram_mb": reserve_vram_mb,
        }
        binding: dict[str, Any] = {
            "binding_id": binding_id,
            "phase": "67C",
            "status": "ready_for_operator_review" if not missing_inputs else "needs_inputs",
            "created_at": now.isoformat(),
            "template_id": str(template["template_id"]),
            "template_name": str(template["name"]),
            "workflow_kind": str(template["workflow_kind"]),
            "input_assets": input_assets,
            "missing_inputs": missing_inputs,
            "resource_plan": resource_plan,
            "required_nodes": list(template.get("required_nodes", [])),
            "required_models": list(template.get("required_models", [])),
            "plugin_installation": list(template.get("plugin_installation", [])),
            "model_installation": list(template.get("model_installation", [])),
            "operator_parameters": dict(operator_parameters or {}),
            "operator_note": operator_note,
            "metadata": dict(metadata or {}),
            "submit_policy": "operator_must_import_real_graph_then_enable_guarded_runtime",
            "execution_boundary": "This is a real input binding and workflow contract; it does not install models, mutate ComfyUI, upload files, submit prompts, publish, or control accounts.",
        }
        binding["prompt"] = self._build_bound_comfyui_prompt(job=job, template=template, binding=binding)
        binding["workflow"] = self._build_bound_comfyui_workflow(job=job, template=template, binding=binding)
        return binding

    def _asset_binding_record(self, asset: DigitalHumanAsset, *, slot: str, role: str) -> dict[str, Any]:
        return {
            "slot": slot,
            "role": role,
            "asset_id": str(asset.id),
            "asset_type": asset.asset_type,
            "name": asset.name,
            "source_uri": asset.source_uri,
            "file_name": asset.file_name,
            "mime_type": asset.mime_type,
            "checksum": asset.checksum,
            "consent_status": asset.consent_status,
            "comfyui_upload": self._comfyui_upload_hint(asset),
        }

    def _comfyui_upload_hint(self, asset: DigitalHumanAsset) -> dict[str, Any]:
        mime_type = (asset.mime_type or "").lower()
        if mime_type.startswith("image/"):
            return {"kind": "image", "path": "/upload/image", "field": "image", "requires_operator_upload": True}
        if mime_type.startswith("video/"):
            return {"kind": "video", "path": "operator_import_or_workflow_specific_upload", "field": "video", "requires_operator_upload": True}
        if mime_type.startswith("audio/"):
            return {"kind": "audio", "path": "operator_import_or_workflow_specific_upload", "field": "audio", "requires_operator_upload": True}
        return {"kind": "metadata", "path": None, "field": None, "requires_operator_upload": False}

    def _workflow_missing_inputs(
        self,
        *,
        template: Mapping[str, Any],
        input_assets: Sequence[Mapping[str, Any]],
        job: DigitalHumanVideoJob,
    ) -> list[str]:
        missing: list[str] = []
        for slot in template.get("input_slots", []):
            if not isinstance(slot, Mapping) or not slot.get("required"):
                continue
            slot_name = str(slot.get("slot") or "")
            if slot_name == "script_text":
                if not job.script.strip():
                    missing.append("script_text")
                continue
            if not any(str(asset.get("slot")) == slot_name for asset in input_assets):
                missing.append(slot_name)
        return missing

    def _build_bound_comfyui_prompt(
        self,
        *,
        job: DigitalHumanVideoJob,
        template: Mapping[str, Any],
        binding: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "aiops_bound_digital_human_workflow": {
                "class_type": "AIOpsDigitalHumanWorkflowBinding",
                "inputs": {
                    "template_id": template["template_id"],
                    "binding_id": binding["binding_id"],
                    "objective": job.objective,
                    "script": job.script,
                    "aspect_ratio": job.aspect_ratio,
                    "duration_seconds": job.duration_seconds,
                    "input_assets": binding["input_assets"],
                    "operator_parameters": binding["operator_parameters"],
                    "submission_note": "Replace this contract node with the operator-imported real ComfyUI workflow before enabling prompt submission.",
                },
            }
        }

    def _build_bound_comfyui_workflow(
        self,
        *,
        job: DigitalHumanVideoJob,
        template: Mapping[str, Any],
        binding: Mapping[str, Any],
    ) -> dict[str, Any]:
        return {
            "name": f"aiops_{template['template_id']}",
            "phase": "67C",
            "media_type": "video",
            "job_id": str(job.id),
            "binding_id": binding["binding_id"],
            "template_id": template["template_id"],
            "workflow_kind": template["workflow_kind"],
            "required_nodes": list(template.get("required_nodes", [])),
            "required_models": list(template.get("required_models", [])),
            "input_assets": binding["input_assets"],
            "output_slots": list(template.get("output_slots", [])),
            "resource_plan": binding["resource_plan"],
            "execution_boundary": binding["execution_boundary"],
        }

    def _workflow_binding_from_job(self, job: DigitalHumanVideoJob) -> dict[str, Any]:
        binding = (job.job_metadata or {}).get("comfyui_workflow_binding")
        return dict(binding) if isinstance(binding, Mapping) else {}

    async def _get_asset_model(self, session: AsyncSession, *, workspace_id: str, asset_id: UUID) -> DigitalHumanAsset:
        result = await session.execute(
            select(DigitalHumanAsset).where(
                DigitalHumanAsset.workspace_id == workspace_id,
                DigitalHumanAsset.id == asset_id,
            )
        )
        asset = result.scalar_one_or_none()
        if asset is None:
            raise AppError("Digital human asset not found", status_code=404)
        return asset

    async def _get_video_job_model(self, session: AsyncSession, *, workspace_id: str, job_id: UUID) -> DigitalHumanVideoJob:
        result = await session.execute(
            select(DigitalHumanVideoJob).where(
                DigitalHumanVideoJob.workspace_id == workspace_id,
                DigitalHumanVideoJob.id == job_id,
            )
        )
        job = result.scalar_one_or_none()
        if job is None:
            raise AppError("Digital human video job not found", status_code=404)
        return job

    def _provider(self) -> str:
        return str(getattr(self.settings, "digital_human_provider", "mock") or "mock").strip().lower()

    def _normalize_provider(self, provider: str | None) -> str:
        normalized = str(provider or self._provider() or "mock").strip().lower()
        if normalized == "liveportrait_musetalk":
            return "local_musetalk_liveportrait"
        return normalized or "mock"

    def _provider_calls_enabled(self, provider: str) -> bool:
        if provider == "mock":
            return False
        enabled = bool(getattr(self.settings, "digital_human_enabled", False))
        external_allowed = bool(getattr(self.settings, "digital_human_allow_external_api", False))
        return bool(enabled and (external_allowed or provider.startswith("local_")))

    def _initial_job_status(self, *, provider: str, avatar_asset: DigitalHumanAsset | None) -> str:
        if avatar_asset is None:
            return "needs_assets"
        if avatar_asset.consent_status != "authorized":
            return "needs_consent"
        if provider != "mock" and not self._provider_calls_enabled(provider):
            return "provider_blocked"
        return "planned"

    def _failure_reason(self, *, status: str, provider: str, consent_status: str) -> str | None:
        if status == "needs_assets":
            return "Upload and select an authorized portrait before digital human video execution."
        if status == "needs_consent":
            return f"Portrait consent is {consent_status}; authorized consent is required before execution."
        if status == "provider_blocked":
            return f"Digital human provider {provider} is not enabled for real execution."
        if status == "queued_for_comfyui":
            return "Digital human job is waiting for ComfyUI video resource admission or output refresh."
        return None

    def _result_summary(self, *, status: str, provider: str) -> str:
        if status == "completed":
            return "Digital human video output is ready for delivery."
        if status == "rendering":
            return "Digital human video job is rendering or waiting for generated media review."
        if status == "queued_for_comfyui":
            return "Digital human video job has a guarded ComfyUI handoff and is waiting for GPU/queue progress."
        if status == "approved":
            return "Digital human video job is approved for the execution provider."
        if status == "planned":
            return f"Digital human video plan is ready; provider={provider}, execution remains plan-only unless enabled."
        if status == "provider_blocked":
            return "Digital human job is blocked by provider execution gates."
        if status == "needs_assets":
            return "Digital human job needs an uploaded portrait asset."
        if status == "needs_consent":
            return "Digital human job needs explicit portrait authorization."
        return f"Digital human job status is {status}."

    def _provider_response_stub(self, *, status: str, provider: str) -> dict[str, object]:
        return {
            "phase": "67A",
            "provider": provider,
            "status": status,
            "external_request_attempted": False,
            "message": "Provider execution is not performed in Phase 67A foundation mode.",
        }

    def _build_comfyui_handoff_prompt(self, job: DigitalHumanVideoJob) -> dict[str, object]:
        return {
            "aiops_digital_human_video_handoff": {
                "class_type": "AIOpsDigitalHumanVideoHandoff",
                "inputs": {
                    "objective": job.objective,
                    "script": job.script,
                    "aspect_ratio": job.aspect_ratio,
                    "duration_seconds": job.duration_seconds,
                    "avatar_asset_id": str(job.avatar_asset_id) if job.avatar_asset_id else None,
                    "material_asset_ids": job.material_asset_ids or [],
                    "reference_asset_ids": job.reference_asset_ids or [],
                    "target_channels": job.target_channels or [],
                    "voice_profile": job.voice_profile or {},
                    "handoff_note": "Generated prompt is a contract placeholder. Supply a real ComfyUI workflow prompt before enabling immediate submission.",
                },
            }
        }

    def _build_comfyui_handoff_workflow(self, job: DigitalHumanVideoJob) -> dict[str, object]:
        return {
            "name": "aiops_digital_human_video_handoff",
            "phase": "67B",
            "media_type": "video",
            "job_id": str(job.id),
            "objective": job.objective,
            "required_assets": {
                "avatar_asset_id": str(job.avatar_asset_id) if job.avatar_asset_id else None,
                "material_asset_ids": job.material_asset_ids or [],
                "reference_asset_ids": job.reference_asset_ids or [],
            },
            "pipeline": ["portrait_or_avatar_video", "product_broll", "subtitle_overlay", "ffmpeg_compose"],
            "execution_boundary": "This workflow is a handoff contract; submit a real ComfyUI prompt/workflow to render media.",
        }

    def _digital_status_from_comfyui_status(self, comfyui_status: str) -> str:
        normalized = str(comfyui_status or "").strip().lower()
        if normalized == "output_ready":
            return "rendering"
        if normalized == "submitted":
            return "rendering"
        if normalized in {"queued", "resource_blocked", "draft", "ready_to_submit"}:
            return "queued_for_comfyui"
        if normalized == "failed":
            return "failed"
        return "queued_for_comfyui"

    def _digital_handoff_result_summary(self, *, comfyui_status: str) -> str:
        if comfyui_status == "output_ready":
            return "ComfyUI video outputs are available; review and compose the final digital human deliverable."
        if comfyui_status == "submitted":
            return "Digital human video job has been submitted to guarded ComfyUI runtime."
        if comfyui_status == "queued":
            return "Digital human video handoff is waiting for an available ComfyUI GPU/queue slot."
        if comfyui_status == "ready_to_submit":
            return "Digital human video handoff passed admission planning and is ready for an operator-supplied ComfyUI prompt submission."
        if comfyui_status == "resource_blocked":
            return "Digital human video handoff is blocked by ComfyUI GPU, queue, or runtime gates."
        if comfyui_status == "failed":
            return "Digital human ComfyUI handoff failed before an output was available."
        return "Digital human video handoff has been recorded."

    def _comfyui_resource_block_reason(self, resource_plan: Mapping[str, Any] | None) -> str | None:
        if not isinstance(resource_plan, Mapping):
            return None
        admission_status = str(resource_plan.get("admission_status") or "").strip().lower()
        if admission_status != "blocked":
            return None
        reasons = resource_plan.get("blocking_reasons")
        if isinstance(reasons, list) and reasons:
            return "; ".join(str(reason) for reason in reasons[:3])
        error = resource_plan.get("error")
        return str(error) if error else "ComfyUI video resource admission is blocked."

    def _duration_from_frames(self, *, frames: int | None, fps: float | None) -> float | None:
        if frames and fps and fps > 0:
            return round(float(frames) / float(fps), 3)
        return None

    def _frames_from_duration(self, *, duration_seconds: float | None, fps: float | None) -> int | None:
        if duration_seconds and fps and fps > 0:
            return max(1, int(round(duration_seconds * fps)))
        return None

    def _upsert_output(
        self,
        outputs: list[dict[str, Any]],
        output: dict[str, Any],
        *,
        key: str,
        value: str,
    ) -> list[dict[str, Any]]:
        kept = [item for item in outputs if item.get(key) != value]
        return [*kept, output]

    def _string_from_mapping(self, payload: Mapping[str, object], key: str) -> str | None:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        return None

    def _truncate_text(self, value: str, limit: int) -> str:
        normalized = " ".join(str(value or "").split()).strip()
        return normalized[:limit] if normalized else "digital human output"

    def _build_scene_plan(
        self,
        *,
        status: str,
        provider: str,
        has_avatar: bool,
        material_count: int,
        reference_count: int,
    ) -> list[dict[str, object]]:
        asset_status = "ready" if has_avatar else "blocked"
        if status == "completed":
            provider_status = "complete"
            broll_status = "complete"
            compose_status = "complete"
        elif status == "rendering":
            provider_status = "running"
            broll_status = "running"
            compose_status = "waiting"
        elif status == "queued_for_comfyui":
            provider_status = "ready"
            broll_status = "queued"
            compose_status = "waiting"
        else:
            provider_status = "ready" if status in {"planned", "approved", "ready_for_review"} else status
            broll_status = "planned"
            compose_status = "planned"
        return [
            {
                "step": "asset_intake",
                "label": "Authorized portrait and product/reference assets",
                "status": asset_status,
                "detail": f"portrait={has_avatar}; materials={material_count}; references={reference_count}",
            },
            {
                "step": "script_breakdown",
                "label": "Script to scenes",
                "status": "ready" if has_avatar else "waiting",
                "detail": "Prepare opener, value proof, product evidence, call to action, and closing scene.",
            },
            {
                "step": "tts_voice",
                "label": "TTS voice generation",
                "status": provider_status,
                "detail": "Voice provider remains abstract; output audio is required before lip sync.",
            },
            {
                "step": "avatar_motion",
                "label": "Digital human motion and lip sync",
                "status": provider_status,
                "detail": f"Target provider: {provider}. Options include HeyGen, Tavus, D-ID, or local LivePortrait + MuseTalk.",
            },
            {
                "step": "broll_generation",
                "label": "ComfyUI product scenes and B-roll",
                "status": broll_status,
                "detail": "Product/reference assets can feed ComfyUI video jobs after GPU admission.",
            },
            {
                "step": "ffmpeg_compose",
                "label": "Subtitle, material overlay, and final composition",
                "status": compose_status,
                "detail": "Final video must be reviewed before OpenClaw / Playwright publishing.",
            },
        ]

    def _normalize_asset_type(self, asset_type: str) -> str:
        normalized = str(asset_type or "").strip().lower()
        if normalized not in DIGITAL_HUMAN_ASSET_TYPES:
            raise AppError(f"Unsupported digital human asset_type: {asset_type}", status_code=400)
        return normalized

    def _normalize_consent_status(self, consent_status: str) -> str:
        normalized = str(consent_status or "unverified").strip().lower()
        if normalized not in DIGITAL_HUMAN_CONSENT_STATUSES:
            raise AppError(f"Unsupported digital human consent_status: {consent_status}", status_code=400)
        return normalized

    def _safe_path_part(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_.-]+", "_", value).strip("._") or "workspace"
