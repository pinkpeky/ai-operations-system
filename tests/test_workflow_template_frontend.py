"""Workflow template frontend integration file tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_admin_dashboard_template_library_exists() -> None:
    main = (ROOT / "admin_dashboard/src/main.tsx").read_text(encoding="utf-8")
    client = (ROOT / "admin_dashboard/src/api/workflowTemplateClient.ts").read_text(encoding="utf-8")

    assert "Workflow Templates" in main
    assert "Template Library" in main
    assert "workflowTemplateClient" in main
    assert "Import dry-run" in main
    assert "not a visual DAG builder" in main
    assert "/workflow-templates" in client
    assert "/workflow-template-runs" in client
    assert "runTemplate" in client


def test_worker_consoles_template_library_exists() -> None:
    for relative in ("worker_console/src/main.tsx", "worker_console_desktop/src/main.tsx"):
        main = (ROOT / relative).read_text(encoding="utf-8")
        assert "Template Library" in main
        assert "Workflow Template Registry foundation" in main
        assert "runSelectedWorkflowTemplate" in main
        assert "not a visual DAG builder" in main


def test_worker_template_clients_exist() -> None:
    for relative in (
        "worker_console/src/api/workflowTemplateClient.ts",
        "worker_console_desktop/src/api/workflowTemplateClient.ts",
    ):
        client = (ROOT / relative).read_text(encoding="utf-8")
        assert "/workflow-templates" in client
        assert "/workflow-template-runs" in client
        assert "validateTemplate" in client
