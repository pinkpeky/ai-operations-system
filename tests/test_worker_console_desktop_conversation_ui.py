"""Phase 37 Desktop Worker Console Conversation UI tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESKTOP_MAIN = ROOT / "worker_console_desktop" / "src" / "main.tsx"


def test_desktop_console_chat_panel_has_config_and_polling() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")

    for term in (
        "Chat Panel",
        "AI Server URL",
        "Workspace ID",
        "User ID",
        "Create thread",
        "Send and run",
        "Refresh messages/events",
        "Poll events every 5 seconds",
        "AI Server unreachable",
        "event-payload",
        "Latest assistant message",
    ):
        assert term in text


def test_desktop_console_chat_panel_declares_native_and_streaming_limits() -> None:
    text = DESKTOP_MAIN.read_text(encoding="utf-8")

    assert "Tauri native validation still depends" in text
    assert "not WebSocket" in text
    assert "not SSE" in text
    assert "not a full ChatGPT UI" in text
    assert "WebSocket(" not in text
    assert "EventSource(" not in text
