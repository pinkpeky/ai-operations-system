"""Phase 39 conversation risk policy tests."""

from app.conversation.risk_policy import ConversationRiskPolicy
from app.conversation.tool_router import ConversationRouteDecision


def decision(route_name: str, selected_tool: str | None, tool_input: dict[str, object], route_type: str = "tool") -> ConversationRouteDecision:
    return ConversationRouteDecision(
        route_name=route_name,
        selected_tool=selected_tool,
        reason="test",
        confidence=1.0,
        tool_input=tool_input,
        route_type=route_type,  # type: ignore[arg-type]
    )


def test_conversation_risk_policy_low_safe_routes() -> None:
    policy = ConversationRiskPolicy()
    assert policy.assess(decision("content", None, {}, "agent")) == "low"
    assert policy.assess(decision("rag_search", "rag_search_tool", {"query": "phase"}, "tool")) == "low"
    assert policy.assess(decision("planning", None, {"root_goal": "plan"}, "planning")) == "low"


def test_conversation_risk_policy_medium_browser_and_mock_openclaw() -> None:
    policy = ConversationRiskPolicy()
    assert policy.assess(decision("browser", "browser_tool", {"action_type": "navigate"})) == "medium"
    assert policy.assess(
        decision(
            "openclaw",
            "openclaw_tool",
            {"openclaw_action_type": "mock_inspect", "metadata": {"mock": True}},
        )
    ) == "medium"


def test_conversation_risk_policy_high_for_click_upload_publish_and_real_openclaw() -> None:
    policy = ConversationRiskPolicy()
    assert policy.assess(decision("browser", "browser_tool", {"action_type": "click", "target": "#publish"})) == "high"
    assert policy.assess(decision("browser", "browser_tool", {"action_type": "upload"})) == "high"
    assert policy.assess(decision("openclaw", "openclaw_tool", {"openclaw_action_type": "real_openclaw"})) == "high"
