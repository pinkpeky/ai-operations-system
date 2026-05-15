"""Phase 42 frontend task run integration tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_frontend_task_run_clients_and_panels_exist() -> None:
    paths = [
        ROOT / "admin_dashboard/src/api/taskRunClient.ts",
        ROOT / "worker_console/src/api/taskRunClient.ts",
        ROOT / "worker_console_desktop/src/api/taskRunClient.ts",
    ]
    for path in paths:
        text = path.read_text(encoding="utf-8")
        assert "/task-runs" in text
        assert "/retry" in text
        assert "/cancel" in text
        assert "/resume" in text

    for app in (ROOT / "worker_console/src/main.tsx", ROOT / "worker_console_desktop/src/main.tsx"):
        text = app.read_text(encoding="utf-8")
        assert "Task Runs" in text
        assert "Run background" in text
        assert "not Celery" in text

    admin = (ROOT / "admin_dashboard/src/main.tsx").read_text(encoding="utf-8")
    assert "Task Orchestration Foundation" in admin
    assert "Queue background" in admin
