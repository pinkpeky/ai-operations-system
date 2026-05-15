"""Phase 38 frontend bridge event surface tests."""

from pathlib import Path


def test_conversation_frontends_render_tool_bridge_fields() -> None:
    paths = [
        Path("admin_dashboard/src/main.tsx"),
        Path("worker_console/src/main.tsx"),
        Path("worker_console_desktop/src/main.tsx"),
    ]
    for path in paths:
        content = path.read_text(encoding="utf-8")
        assert "selected tool" in content.lower() or "Selected tool" in content
        assert "result_metadata" in content or "lastRunMetadata" in content
        assert "route_name" in content or "route:" in content


def test_conversation_clients_include_phase38_response_fields() -> None:
    paths = [
        Path("admin_dashboard/src/api/conversationClient.ts"),
        Path("worker_console/src/api/conversationClient.ts"),
        Path("worker_console_desktop/src/api/conversationClient.ts"),
    ]
    for path in paths:
        content = path.read_text(encoding="utf-8")
        for term in ("route_name", "selected_tool", "events_created", "success", "summary", "result_metadata"):
            assert term in content
