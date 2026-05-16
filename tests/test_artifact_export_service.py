"""Phase 44 ArtifactExportService tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.config import Settings
from app.services.artifact_export_service import ArtifactExportService
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_artifact_export_service_creates_exported_child_artifact(session, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    settings = Settings(OUTPUT_ARTIFACT_DIR=str(tmp_path / "artifacts"), OUTPUT_EXPORT_DIR=str(tmp_path / "exports"))
    artifact = await OutputArtifactService(session, settings=settings).create_artifact(
        workspace_id="workspace-export-pipeline",
        source_type="playbook",
        artifact_type="report",
        title="Pipeline report",
        summary="summary",
        content="body",
    )

    result = await ArtifactExportService(session, settings=settings).export_markdown(
        workspace_id="workspace-export-pipeline",
        artifact_id=artifact.id,
    )

    assert Path(result["output_path"]).exists()
    assert result["generated_artifact"].parent_artifact_id == artifact.id
    assert result["generated_artifact"].artifact_stage == "exported"
    assert "# Pipeline report" in result["content"]
