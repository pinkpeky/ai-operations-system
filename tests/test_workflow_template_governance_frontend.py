"""Workflow template governance frontend file tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_admin_dashboard_template_governance_ui_exists() -> None:
    main = (ROOT / "admin_dashboard/src/main.tsx").read_text(encoding="utf-8")
    client = (ROOT / "admin_dashboard/src/api/workflowTemplateClient.ts").read_text(encoding="utf-8")

    assert "Template Governance" in main
    assert "Review Queue" in main
    assert "Marketplace View" in main
    assert "Compatibility Matrix" in main
    assert "Rollback" in main
    assert "/workflow-template-reviews" in client
    assert "/workflow-template-marketplace" in client
    assert "/workflow-template-compatibility-matrix" in client


def test_worker_consoles_show_governance_status() -> None:
    for relative in ("worker_console/src/main.tsx", "worker_console_desktop/src/main.tsx"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Governance status" in text
        assert "verified" in text
        assert "not a public marketplace" in text
