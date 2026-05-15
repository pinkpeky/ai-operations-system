"""OutputArtifactService behavior tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_output_artifact_export_writes_markdown_json_and_txt(session, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    service = OutputArtifactService(session, settings=Settings(OUTPUT_ARTIFACT_DIR=str(tmp_path)))
    artifact = await service.create_artifact(
        workspace_id="workspace-export",
        source_type="playbook",
        artifact_type="report",
        title="Report artifact",
        summary="Short summary",
        content="Longer report body",
        metadata={"phase": "41"},
    )

    exported, markdown_path, markdown = await service.export_artifact(
        workspace_id="workspace-export",
        artifact_id=artifact.id,
        export_format="markdown",
    )
    _, json_path, json_content = await service.export_artifact(
        workspace_id="workspace-export",
        artifact_id=artifact.id,
        export_format="json",
    )
    _, txt_path, txt = await service.export_artifact(
        workspace_id="workspace-export",
        artifact_id=artifact.id,
        export_format="txt",
    )

    assert exported.id == artifact.id
    assert markdown_path.exists()
    assert json_path.exists()
    assert txt_path.exists()
    assert "# Report artifact" in markdown
    assert '"artifact_type": "report"' in json_content
    assert "Longer report body" in txt
