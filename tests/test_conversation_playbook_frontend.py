"""Phase 40 frontend playbook UI file checks."""

from pathlib import Path


def test_conversation_clients_include_playbook_methods() -> None:
    for path in (
        Path("admin_dashboard/src/api/conversationClient.ts"),
        Path("worker_console/src/api/conversationClient.ts"),
        Path("worker_console_desktop/src/api/conversationClient.ts"),
    ):
        text = path.read_text(encoding="utf-8")
        for token in (
            "ConversationPlaybook",
            "ConversationPlaybookRun",
            "listPlaybooks",
            "runPlaybook",
            "listPlaybookRuns",
            "playbook_name",
            "playbook_run_id",
        ):
            assert token in text


def test_conversation_pages_render_playbook_controls() -> None:
    for path in (
        Path("admin_dashboard/src/main.tsx"),
        Path("worker_console/src/main.tsx"),
        Path("worker_console_desktop/src/main.tsx"),
    ):
        text = path.read_text(encoding="utf-8")
        for token in (
            "Playbook selector",
            "Run playbook",
            "Playbook runs",
            "Step timeline",
            "browser_screenshot_report",
        ):
            assert token in text
