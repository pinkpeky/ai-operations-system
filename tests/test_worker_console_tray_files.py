from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_tray_runtime_files_exist() -> None:
    """Phase 32 必须包含系统托盘、设置和自启动占位文件。"""

    required_files = [
        "src/desktopBridge.ts",
        "src/settings.ts",
        "settings.example.json",
        "src-tauri/desktop-runtime.json",
        "autostart/README.md",
        "autostart/windows_registry_placeholder.md",
        "autostart/mac_launch_agent_placeholder.md",
    ]

    for relative_path in required_files:
        assert (DESKTOP_ROOT / relative_path).exists(), relative_path


def test_tauri_tray_menu_contains_required_actions() -> None:
    main_rs = (DESKTOP_ROOT / "src-tauri/src/main.rs").read_text(encoding="utf-8")

    for label in [
        "Show Console",
        "Hide Window",
        "Start Runtime",
        "Stop Runtime",
        "Restart Runtime",
        "Start Heartbeat",
        "Stop Heartbeat",
        "Refresh Status",
        "Quit",
    ]:
        assert label in main_rs

    for action in [
        "startRuntime",
        "stopRuntime",
        "restartRuntime",
        "startHeartbeat",
        "stopHeartbeat",
        "refreshStatus",
    ]:
        assert action in main_rs


def test_minimize_to_tray_close_handler_is_present() -> None:
    main_rs = (DESKTOP_ROOT / "src-tauri/src/main.rs").read_text(encoding="utf-8")
    runtime_config = (DESKTOP_ROOT / "src-tauri/desktop-runtime.json").read_text(encoding="utf-8")

    assert "MINIMIZE_TO_TRAY: bool = true" in main_rs
    assert "CloseRequested" in main_rs
    assert "api.prevent_close()" in main_rs
    assert ".hide()" in main_rs
    assert '"minimize_to_tray": true' in runtime_config
