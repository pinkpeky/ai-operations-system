from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_start_runtime_error_states_are_visible() -> None:
    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    for status in [
        "starting",
        "started",
        "failed",
        "unavailable",
        "port_conflict",
        "missing_config",
        "server_environment_warning",
    ]:
        assert status in app

    assert "runtime_action_status" in app
    assert "last_error_detail" in app
    assert "Start Runtime failed" in app


def test_native_launcher_reports_config_and_port_errors() -> None:
    main_rs = (DESKTOP_ROOT / "src-tauri/src/main.rs").read_text(encoding="utf-8")

    assert "missing_config: missing worker config" in main_rs
    assert "Copy worker_config.example.yaml first" in main_rs
    assert "port_conflict: port" in main_rs
    assert "already in use" in main_rs
    assert "server_environment_warning" in main_rs

