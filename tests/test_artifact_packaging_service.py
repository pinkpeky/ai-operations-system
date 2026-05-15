"""Phase 44 ArtifactPackagingService tests."""

from __future__ import annotations

from pathlib import Path
import zipfile

import pytest

from app.core.config import Settings
from app.services.artifact_packaging_service import ArtifactPackagingService
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_artifact_packaging_service_creates_bundle_zip(session, tmp_path: Path) -> None:  # type: ignore[no-untyped-def]
    settings = Settings(OUTPUT_ARTIFACT_DIR=str(tmp_path / "artifacts"), OUTPUT_EXPORT_DIR=str(tmp_path / "exports"))
    service = OutputArtifactService(session, settings=settings)
    artifact = await service.create_artifact(
        workspace_id="workspace-package",
        source_type="conversation",
        artifact_type="markdown",
        title="Package me",
        content="hello",
    )

    result = await ArtifactPackagingService(session, settings=settings).package_artifact(
        workspace_id="workspace-package",
        artifact_id=artifact.id,
    )

    zip_path = Path(result["output_path"])
    assert zip_path.exists()
    assert result["generated_artifact"].artifact_type == "bundle"
    with zipfile.ZipFile(zip_path) as archive:
        assert "metadata.json" in archive.namelist()
        assert "report.md" in archive.namelist()
