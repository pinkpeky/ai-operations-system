"""Phase 44 artifact lineage tests."""

from __future__ import annotations

import pytest

from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_output_artifact_lineage_tracks_parent_root_and_descendants(session):  # type: ignore[no-untyped-def]
    service = OutputArtifactService(session)
    parent = await service.create_artifact(
        workspace_id="workspace-lineage",
        source_type="playbook",
        artifact_type="report",
        artifact_role="report",
        title="Root report",
        content="root",
    )
    child = await service.create_artifact(
        workspace_id="workspace-lineage",
        source_type="tool",
        artifact_type="markdown",
        artifact_role="markdown",
        parent_artifact_id=parent.id,
        title="Markdown export",
        content="derived",
    )
    await service.create_relationship(
        workspace_id="workspace-lineage",
        parent_artifact_id=parent.id,
        child_artifact_id=child.id,
        relationship_type="derived_from",
    )

    lineage = await service.lineage_for_artifact(workspace_id="workspace-lineage", artifact_id=parent.id)

    assert child.root_artifact_id == parent.id
    assert lineage["root_artifact_id"] == parent.id
    assert [item.id for item in lineage["descendants"]] == [child.id]
    assert lineage["relationships"][0].relationship_type == "derived_from"
