"""Retention and cleanup preview for output artifacts."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models.enums import OutputArtifactRetentionPolicy
from app.services.output_artifact_service import OutputArtifactService


class ArtifactRetentionService:
    """Soft-archive retention candidates without deleting physical files."""

    def __init__(self, session: AsyncSession, *, settings: Settings | None = None) -> None:
        self.session = session
        self.settings = settings or get_settings()
        self.artifacts = OutputArtifactService(session, settings=self.settings)

    async def cleanup_preview(
        self,
        *,
        workspace_id: str,
        retention_policy: str | None = None,
        now: datetime | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Return artifacts that would be archived by retention cleanup."""

        candidates = await self._expired_candidates(
            workspace_id=workspace_id,
            retention_policy=retention_policy,
            now=now,
            limit=limit,
        )
        items = [
            {
                "artifact_id": artifact.id,
                "title": artifact.title,
                "retention_policy": artifact.retention_policy,
                "expires_at": artifact.expires_at,
                "reason": "expires_at is in the past; cleanup is preview-only by default",
            }
            for artifact in candidates
        ]
        return {"workspace_id": workspace_id, "count": len(items), "items": items, "execution_mode": "preview_only"}

    async def archive_expired(
        self,
        *,
        workspace_id: str,
        retention_policy: str | None = None,
        now: datetime | None = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Soft archive expired artifacts. Physical files are not deleted."""

        candidates = await self._expired_candidates(
            workspace_id=workspace_id,
            retention_policy=retention_policy,
            now=now,
            limit=limit,
        )
        archived = []
        for artifact in candidates:
            archived.append(
                await self.artifacts.archive_artifact(
                    workspace_id=workspace_id,
                    artifact_id=artifact.id,
                    reason="retention cleanup",
                    commit=False,
                )
            )
        await self.session.commit()
        return {"workspace_id": workspace_id, "count": len(archived), "artifact_ids": [str(item.id) for item in archived]}

    async def _expired_candidates(
        self,
        *,
        workspace_id: str,
        retention_policy: str | None,
        now: datetime | None,
        limit: int,
    ):
        normalized_now = now or datetime.now(timezone.utc)
        artifacts = await self.artifacts.list_artifacts(
            workspace_id=workspace_id,
            retention_policy=retention_policy,
            archived=False,
            include_deleted=False,
            limit=limit,
        )
        return [
            artifact
            for artifact in artifacts
            if artifact.retention_policy != OutputArtifactRetentionPolicy.COMPLIANCE_HOLD.value
            and artifact.expires_at is not None
            and self._normalize_dt(artifact.expires_at) <= self._normalize_dt(normalized_now)
        ]

    def _normalize_dt(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value
