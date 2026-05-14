from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_ROOT = ROOT / "worker_console_desktop"


def test_desktop_status_sync_uses_local_status_and_health() -> None:
    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    assert "client.getStatus()" in app
    assert "client.getHealth()" in app
    assert "updateTrayTooltip" in app
    assert "buildTrayTooltip" in app
    assert "settings.refreshIntervalMs" in app
    assert "window.setInterval" in app


def test_connection_state_and_logs_ui_are_documented_in_code() -> None:
    app = (DESKTOP_ROOT / "src/main.tsx").read_text(encoding="utf-8")

    for state in ["connected", "reconnecting", "disconnected", "online", "offline", "error"]:
        assert state in app

    assert "Last successful sync" in app
    assert "Last error" in app
    assert "Clear display" in app
    assert "Auto refresh: on" in app
    assert "Last updated" in app
    assert "Worker Runtime 未启动" in app
    assert "本地 Start Runtime 按钮" in app


def test_tray_bridge_does_not_execute_shell_commands() -> None:
    bridge = (DESKTOP_ROOT / "src/desktopBridge.ts").read_text(encoding="utf-8")

    assert "listenForTrayControls" in bridge
    assert "update_tray_tooltip" in bridge
    assert "Command" not in bridge
    assert "shell" not in bridge.lower()
    assert "exec" not in bridge.lower()
