"""Digital human production service foundation."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from hashlib import sha256
from pathlib import Path
import re
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.core.errors import AppError
from app.models.digital_human import DigitalHumanAsset, DigitalHumanVideoJob
from app.schemas.digital_human import (
    DigitalHumanAssetListResponse,
    DigitalHumanAssetResponse,
    DigitalHumanCapabilitiesResponse,
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
    "rendering",
    "completed",
    "failed",
    "cancelled",
    "archived",
}
DIGITAL_HUMAN_PROVIDER_ORDER = ["heygen", "tavus", "local_musetalk_liveportrait", "mock"]


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
                "Generated videos must go through human review before publishing.",
            ],
            workspace_id=workspace_id,
            raw={
                "phase": "67A",
                "no_external_call_performed": True,
                "asset_types": sorted(DIGITAL_HUMAN_ASSET_TYPES),
            },
        )

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
        return None

    def _result_summary(self, *, status: str, provider: str) -> str:
        if status == "completed":
            return "Digital human video output is ready for delivery."
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
        provider_status = "ready" if status in {"planned", "approved", "ready_for_review"} else status
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
                "status": "planned",
                "detail": "Product/reference assets can feed ComfyUI video jobs after GPU admission.",
            },
            {
                "step": "ffmpeg_compose",
                "label": "Subtitle, material overlay, and final composition",
                "status": "planned",
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
