"""Phase 39 frontend approval UI file checks."""

from pathlib import Path


def test_frontend_conversation_clients_include_approval_methods() -> None:
    for path in (
        Path("admin_dashboard/src/api/conversationClient.ts"),
        Path("worker_console/src/api/conversationClient.ts"),
        Path("worker_console_desktop/src/api/conversationClient.ts"),
    ):
        text = path.read_text(encoding="utf-8")
        for token in (
            "ConversationApproval",
            "listApprovals",
            "approveApproval",
            "rejectApproval",
            "cancelApproval",
            "executeApproval",
            "review_first",
            "execute_after_approval",
            "approval_required",
        ):
            assert token in text


def test_frontend_conversation_pages_render_pending_approvals_panel() -> None:
    for path in (
        Path("admin_dashboard/src/main.tsx"),
        Path("worker_console/src/main.tsx"),
        Path("worker_console_desktop/src/main.tsx"),
    ):
        text = path.read_text(encoding="utf-8")
        lower_text = text.lower()
        for token in (
            "approvals panel",
            "proposed_payload",
            "risk",
            "Approve",
            "Reject",
            "Cancel",
            "Execute approved action",
            "approval_status",
        ):
            assert token in lower_text if token == "approvals panel" else token in text
