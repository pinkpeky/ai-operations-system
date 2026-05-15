"""Phase 38 conversation tool router tests."""

from app.conversation.tool_router import ConversationToolRouter


def test_conversation_tool_router_selects_browser_bridge() -> None:
    router = ConversationToolRouter()

    decision = router.route("请打开 https://example.com 并截图")

    assert decision.route_name == "browser"
    assert decision.selected_tool == "browser_tool"
    assert decision.tool_input["action_type"] == "navigate_and_screenshot"
    assert decision.tool_input["target"] == "https://example.com"


def test_conversation_tool_router_selects_openclaw_mock() -> None:
    decision = ConversationToolRouter().route("用 OpenClaw 检查设备状态")

    assert decision.route_name == "openclaw"
    assert decision.selected_tool == "openclaw_tool"
    assert decision.tool_input["openclaw_action_type"] == "mock_inspect"
    assert decision.tool_input["metadata"]["mock"] is True


def test_conversation_tool_router_selects_rag_with_collection_metadata() -> None:
    decision = ConversationToolRouter().route(
        "检索知识库里关于 Phase 35A 的内容",
        metadata={"collection_name": "phase35a_docs"},
    )

    assert decision.route_name == "rag_search"
    assert decision.selected_tool == "rag_search_tool"
    assert decision.tool_input["collection_name"] == "phase35a_docs"


def test_conversation_tool_router_prefers_planning_before_content() -> None:
    decision = ConversationToolRouter().route("请帮我拆解一个浏览器搜索热门视频并生成文案的计划")

    assert decision.route_name == "planning"
    assert decision.route_type == "planning"
