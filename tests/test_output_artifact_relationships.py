"""Phase 44 artifact relationship tests."""

from __future__ import annotations

import pytest

from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_artifact_relationships_are_workspace_scoped(session):  # type: ignore[no-untyped-def]
    service = OutputArtifactService(session)
    parent = await service.create_artifact(
        workspace_id="workspace-rel",
        source_type="conversation",
        artifact_type="text",
        title="Transcript",
    )
    child = await service.create_artifact(
        workspace_id="workspace-rel",
        source_type="tool",
        artifact_type="json",
        title="JSON export",
    )

    relationship = await service.create_relationship(
        workspace_id="workspace-rel",
        parent_artifact_id=parent.id,
        child_artifact_id=child.id,
        relationship_type="exported_from",
        metadata={"format": "json"},
    )
    relationships = await service.list_relationships(workspace_id="workspace-rel", artifact_id=parent.id)

    assert relationships == [relationship]
    assert relationships[0].relationship_metadata["format"] == "json"
    with pytest.raises(ValueError):
        await service.list_relationships(workspace_id="other-workspace", artifact_id=parent.id)
