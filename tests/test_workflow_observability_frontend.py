"""Workflow Replay Center frontend file checks."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_admin_dashboard_replay_center_ui_files() -> None:
    main = (ROOT / "admin_dashboard" / "src" / "main.tsx").read_text(encoding="utf-8")
    client = (ROOT / "admin_dashboard" / "src" / "api" / "workflowClient.ts").read_text(encoding="utf-8")

    assert "Replay Center" in main
    assert "Execution Trace Timeline" in main
    assert "Diagnostics" in main
    assert "workflow-observability-command-center" in main
    assert "workflow-observability-flow-grid" in main
    assert "workflow-observability-metrics" in main
    assert "workflow-trace-toolbar" in main
    assert "workflowObsConsoleTitle" in main
    assert "workflowObsTraceViewAttention" in main
    assert "工作流观测台" in main
    assert "Workflow observability console" in main
    assert "createReplaySession" in client
    assert "/workflow-replay-sessions" in client


def test_worker_console_simplified_observability_ui_files() -> None:
    web_main = (ROOT / "worker_console" / "src" / "main.tsx").read_text(encoding="utf-8")
    desktop_main = (ROOT / "worker_console_desktop" / "src" / "main.tsx").read_text(encoding="utf-8")

    for content in (web_main, desktop_main):
        assert "Execution Traces / Diagnostics" in content
        assert "Replay Center" in content
        assert "workflowAnalytics" in content
