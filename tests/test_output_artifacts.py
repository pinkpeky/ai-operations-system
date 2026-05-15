"""Phase 41 output artifact model tests."""

from __future__ import annotations

import pytest

from app.models.enums import OutputArtifactStatus, OutputArtifactType
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_output_artifact_create_list_and_soft_delete(session) -> None:  # type: ignore[no-untyped-def]
    service = OutputArtifactService(session)
    artifact = await service.create_artifact(
        workspace_id="workspace-artifacts",
        source_type="conversation",
        artifact_type="markdown",
        title="Reusable answer",
        summary="A saved assistant answer",
        content="# Answer",
        created_by="tester",
    )

    items = await service.list_artifacts(workspace_id="workspace-artifacts", artifact_type=OutputArtifactType.MARKDOWN.value)
    assert [item.id for item in items] == [artifact.id]

    deleted = await service.delete_artifact(workspace_id="workspace-artifacts", artifact_id=artifact.id)
    assert deleted.status == OutputArtifactStatus.DELETED.value
    assert await service.list_artifacts(workspace_id="workspace-artifacts") == []
    assert len(await service.list_artifacts(workspace_id="workspace-artifacts", include_deleted=True)) == 1
