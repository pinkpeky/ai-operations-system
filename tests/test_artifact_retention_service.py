"""Phase 44 ArtifactRetentionService tests."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from app.services.artifact_retention_service import ArtifactRetentionService
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_artifact_retention_preview_lists_expired_non_hold_artifacts(session) -> None:  # type: ignore[no-untyped-def]
    service = OutputArtifactService(session)
    expired = await service.create_artifact(
        workspace_id="workspace-retention",
        source_type="tool",
        artifact_type="json",
        title="Temporary output",
        retention_policy="temporary",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )
    await service.create_artifact(
        workspace_id="workspace-retention",
        source_type="tool",
        artifact_type="json",
        title="Hold output",
        retention_policy="compliance_hold",
        expires_at=datetime.now(timezone.utc) - timedelta(days=1),
    )

    preview = await ArtifactRetentionService(session).cleanup_preview(workspace_id="workspace-retention")

    assert preview["count"] == 1
    assert preview["items"][0]["artifact_id"] == expired.id
    assert preview["execution_mode"] == "preview_only"
