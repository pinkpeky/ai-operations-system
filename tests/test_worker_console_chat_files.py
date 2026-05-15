"""Worker Console Chat panel file tests."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_worker_console_chat_panel_files_exist() -> None:
    """Web/Desktop Console 都应包含 Chat 面板和 Conversation API client。"""

    web_client = ROOT / "worker_console" / "src" / "api" / "conversationClient.ts"
    desktop_client = ROOT / "worker_console_desktop" / "src" / "api" / "conversationClient.ts"
    assert web_client.exists()
    assert desktop_client.exists()

    web_main = (ROOT / "worker_console" / "src" / "main.tsx").read_text(encoding="utf-8")
    desktop_main = (ROOT / "worker_console_desktop" / "src" / "main.tsx").read_text(encoding="utf-8")
    for text in (web_main, desktop_main):
        assert "function ChatPanel" in text
        assert "Refresh messages/events" in text
        assert "conversationClient.runConversation" in text
        assert "not WebSocket" in text
        assert "not SSE" in text


def test_worker_console_chat_env_examples_document_ai_server() -> None:
    """env 示例应声明 AI Server API 和 workspace headers。"""

    for relative in ("worker_console/.env.example", "worker_console_desktop/.env.example"):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "VITE_AI_SERVER_API=http://localhost:8000" in text
        assert "VITE_WORKSPACE_ID=demo-workspace" in text
        assert "VITE_USER_ID=demo-user" in text
