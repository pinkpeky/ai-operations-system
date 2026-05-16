"""Phase 43 frontend scheduler health coverage tests."""

from __future__ import annotations

from pathlib import Path


def test_admin_dashboard_exposes_scheduler_health_and_recovery_ui() -> None:
    root = Path(__file__).resolve().parents[1]
    main_tsx = (root / "admin_dashboard" / "src" / "main.tsx").read_text(encoding="utf-8")
    client_ts = (root / "admin_dashboard" / "src" / "api" / "taskRunClient.ts").read_text(encoding="utf-8")

    assert "TaskSchedulerHealth" in client_ts
    assert "schedulerHealth" in main_tsx
    assert "Recover" in main_tsx
    assert "Diagnostics" in main_tsx
    assert "lease_expires_at" in main_tsx


def test_worker_consoles_show_simplified_task_recovery_status() -> None:
    root = Path(__file__).resolve().parents[1]
    web_main = (root / "worker_console" / "src" / "main.tsx").read_text(encoding="utf-8")
    desktop_main = (root / "worker_console_desktop" / "src" / "main.tsx").read_text(encoding="utf-8")
    for content in (web_main, desktop_main):
        assert "schedulerHealth" in content
        assert "Recover" in content
        assert "lease_expires_at" in content
        assert "suggested_action" in content
