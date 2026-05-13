"""SimplePlannerAgent 测试。"""

from app.planning.services import SimplePlannerAgent


def test_simple_planner_agent_builds_fixed_structured_plan() -> None:
    """Planner 应生成稳定的三步结构化 plan。"""

    planner = SimplePlannerAgent()
    steps = planner.plan(
        root_goal="生成 AI 自动化运营 TikTok 内容",
        metadata={"platform": "tiktok", "style": "专业简洁", "query": "ping"},
    )

    assert [step.agent_name for step in steps] == ["rag_agent", "content_agent", "review_agent"]
    assert [step.step_order for step in steps] == [1, 2, 3]
    assert steps[0].input_payload["query"] == "ping"
    assert steps[1].input_payload["platform"] == "tiktok"
