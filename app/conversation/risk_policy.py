"""Risk policy for Conversation approval flow."""

from __future__ import annotations

from typing import Any

from app.conversation.tool_router import ConversationRouteDecision
from app.models.enums import ConversationApprovalRiskLevel


class ConversationRiskPolicy:
    """Assign a conservative risk level to a routed conversation action."""

    HIGH_ACTION_KEYWORDS = (
        "click",
        "type",
        "type_text",
        "fill",
        "form",
        "upload",
        "publish",
        "account",
        "profile",
        "login",
        "cookie",
        "real_openclaw",
    )

    def assess(self, decision: ConversationRouteDecision) -> str:
        """Return low/medium/high for the proposed route."""

        route_name = decision.route_name
        selected_tool = decision.selected_tool or ""
        tool_input = decision.tool_input or {}
        action_type = str(tool_input.get("action_type") or tool_input.get("openclaw_action_type") or "").lower()
        serialized = " ".join(
            str(value).lower()
            for value in (
                route_name,
                selected_tool,
                action_type,
                tool_input.get("target"),
                tool_input.get("url"),
            )
            if value is not None
        )

        if any(keyword in serialized for keyword in self.HIGH_ACTION_KEYWORDS):
            return ConversationApprovalRiskLevel.HIGH.value
        if selected_tool == "browser_tool":
            return ConversationApprovalRiskLevel.MEDIUM.value
        if selected_tool == "openclaw_tool":
            # Phase 39 only allows mock OpenClaw inspect, but it is still an external-device bridge.
            if self._is_mock_openclaw(tool_input):
                return ConversationApprovalRiskLevel.MEDIUM.value
            return ConversationApprovalRiskLevel.HIGH.value
        if selected_tool == "create_task_tool":
            if str(tool_input.get("task_type") or "") == "content_generation":
                return ConversationApprovalRiskLevel.LOW.value
            return ConversationApprovalRiskLevel.MEDIUM.value
        if route_name in {"content", "rag_search", "planning", "fallback", "playbook_message", "playbook_summarize"}:
            return ConversationApprovalRiskLevel.LOW.value
        return ConversationApprovalRiskLevel.MEDIUM.value

    def _is_mock_openclaw(self, tool_input: dict[str, Any]) -> bool:
        metadata = tool_input.get("metadata") if isinstance(tool_input.get("metadata"), dict) else {}
        return bool(metadata.get("mock")) or str(tool_input.get("openclaw_action_type") or "").lower().startswith("mock")
