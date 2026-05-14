"""Phase 37 Conversation frontend client file tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_conversation_clients_exist_for_all_frontends() -> None:
    """Admin Dashboard, Worker Console, and Desktop Console all expose a Conversation client."""

    required = [
        "admin_dashboard/src/api/conversationClient.ts",
        "worker_console/src/api/conversationClient.ts",
        "worker_console_desktop/src/api/conversationClient.ts",
    ]
    for relative in required:
        assert (ROOT / relative).exists(), relative


def test_conversation_clients_cover_runtime_methods_and_headers() -> None:
    """Clients should wrap the complete polling Conversation Runtime API."""

    for relative in (
        "admin_dashboard/src/api/conversationClient.ts",
        "worker_console/src/api/conversationClient.ts",
        "worker_console_desktop/src/api/conversationClient.ts",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        for term in (
            "createThread",
            "listThreads",
            "getThread",
            "sendMessage",
            "listMessages",
            "listEvents",
            "runConversation",
            "/conversations",
            "/messages",
            "/events",
            "/run",
        ):
            assert term in text, f"{term} missing from {relative}"

    for relative in (
        "admin_dashboard/src/api/client.ts",
        "worker_console/src/api/conversationClient.ts",
        "worker_console_desktop/src/api/conversationClient.ts",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "X-Workspace-Id" in text
        assert "X-User-Id" in text


def test_worker_console_conversation_clients_normalize_ai_server_base_url() -> None:
    """Worker Console env examples use server root while clients append /api/v1."""

    for relative in (
        "worker_console/src/api/conversationClient.ts",
        "worker_console_desktop/src/api/conversationClient.ts",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "normalizeApiBase" in text
        assert 'endsWith("/api/v1")' in text
        assert '`${trimmed}/api/v1`' in text
