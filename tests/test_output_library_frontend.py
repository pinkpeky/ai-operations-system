"""Output Library frontend integration tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_output_library_frontend_files_and_labels() -> None:
    """All three frontends should expose Output Library entry points."""

    files = [
        ROOT / "admin_dashboard/src/api/outputArtifactClient.ts",
        ROOT / "worker_console/src/api/outputArtifactClient.ts",
        ROOT / "worker_console_desktop/src/api/outputArtifactClient.ts",
    ]
    for path in files:
        assert path.exists(), path
        text = path.read_text(encoding="utf-8")
        assert "/output-artifacts" in text
        assert "exportArtifact" in text

    admin = (ROOT / "admin_dashboard/src/main.tsx").read_text(encoding="utf-8")
    worker = (ROOT / "worker_console/src/main.tsx").read_text(encoding="utf-8")
    desktop = (ROOT / "worker_console_desktop/src/main.tsx").read_text(encoding="utf-8")
    for text in (admin, worker, desktop):
        assert "Output Library" in text
        assert "Save as Artifact" in text or "generated artifacts" in text
        assert "artifact_type" in text
