"""Phase 37 Admin Dashboard Conversation UI tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADMIN_MAIN = ROOT / "admin_dashboard" / "src" / "main.tsx"


def test_admin_dashboard_conversation_page_supports_create_send_run_and_polling() -> None:
    """The dashboard conversation page should be more than a read-only list."""

    text = ADMIN_MAIN.read_text(encoding="utf-8")

    for term in (
        "Create thread",
        "Send message",
        "Run conversation",
        "Refresh messages/events",
        "Poll events every 5 seconds",
        "Latest assistant",
        "Latest Event Payload",
        "AI Server unreachable",
        "conversationClient.createThread",
        "conversationClient.sendMessage",
        "conversationClient.runConversation",
        "conversationClient.listMessages",
        "conversationClient.listEvents",
    ):
        assert term in text


def test_admin_dashboard_conversation_ui_declares_foundation_limits() -> None:
    """Phase 37 must not claim true streaming or a full ChatGPT UI."""

    text = ADMIN_MAIN.read_text(encoding="utf-8")

    assert "not WebSocket" in text
    assert "not SSE" in text
    assert "not a full ChatGPT UI" in text
    assert "WebSocket(" not in text
    assert "EventSource(" not in text
