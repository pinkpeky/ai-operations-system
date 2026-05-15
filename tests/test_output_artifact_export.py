"""Output artifact export format tests."""

from __future__ import annotations

import pytest

from app.core.config import Settings
from app.services.output_artifact_service import OutputArtifactService


@pytest.mark.asyncio
async def test_output_artifact_rejects_unknown_export_format(session, tmp_path) -> None:  # type: ignore[no-untyped-def]
    service = OutputArtifactService(session, settings=Settings(OUTPUT_ARTIFACT_DIR=str(tmp_path)))
    artifact = await service.create_artifact(
        workspace_id="workspace-export-format",
        source_type="rag",
        artifact_type="rag_answer",
        title="RAG answer",
        content="Answer",
    )

    with pytest.raises(ValueError, match="export format"):
        await service.export_artifact(
            workspace_id="workspace-export-format",
            artifact_id=artifact.id,
            export_format="pdf",
        )
