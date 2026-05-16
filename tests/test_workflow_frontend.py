"""Frontend Workflow State integration file tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_admin_dashboard_workflow_ui_exists() -> None:
    main = (ROOT / "admin_dashboard/src/main.tsx").read_text(encoding="utf-8")
    client = (ROOT / "admin_dashboard/src/api/workflowClient.ts").read_text(encoding="utf-8")

    assert "Workflows" in main
    assert "Workflow Runs" in main
    assert "Agent Memory Snapshots" in main
    assert "not a full workflow builder" in main
    assert "/workflow-runs" in client
    assert "pause" in client and "resume" in client


def test_worker_console_workflow_state_panel_exists() -> None:
    for relative in ("worker_console/src/main.tsx", "worker_console_desktop/src/main.tsx"):
        main = (ROOT / relative).read_text(encoding="utf-8")
        assert "Workflow State" in main
        assert "Agent Memory Snapshots" in main
        assert "workflow_run_id" in main


def test_worker_console_workflow_clients_exist() -> None:
    for relative in ("worker_console/src/api/workflowClient.ts", "worker_console_desktop/src/api/workflowClient.ts"):
        client = (ROOT / relative).read_text(encoding="utf-8")
        assert "/workflow-runs" in client
        assert "listMemorySnapshots" in client
        assert "WorkflowRun" in client
