"""Phase 44 frontend artifact explorer file tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_admin_dashboard_artifact_explorer_has_lineage_export_and_retention_ui() -> None:
    main = (ROOT / "admin_dashboard" / "src" / "main.tsx").read_text(encoding="utf-8")
    client = (ROOT / "admin_dashboard" / "src" / "api" / "outputArtifactClient.ts").read_text(encoding="utf-8")

    assert "Output Library" in main
    assert "artifact_role" in main
    assert "artifact_stage" in main
    assert "retention_policy" in main
    assert "Load lineage" in main
    assert "Package lineage" in main
    assert "getLineage" in client
    assert "packageArtifact" in client
    assert "cleanupPreview" in client


def test_worker_consoles_expose_simplified_export_package_lineage_controls() -> None:
    for relative in ["worker_console/src/main.tsx", "worker_console_desktop/src/main.tsx"]:
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Package" in text
        assert "Lineage" in text
        assert "retention_policy" in text
