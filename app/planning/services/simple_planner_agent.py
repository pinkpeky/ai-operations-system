"""SimplePlannerAgent。

这是 Phase 16 的 rule-based planner，只产出有限、可解释的步骤，不做递归规划或自主工具选择。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class PlannedStep:
    """SimplePlannerAgent 产出的结构化 step。"""

    step_order: int
    title: str
    description: str
    agent_name: str | None = None
    tool_name: str | None = None
    input_payload: dict[str, Any] = field(default_factory=dict)


class SimplePlannerAgent:
    """轻量规则 planner。"""

    agent_name = "simple_planner"

    def plan(self, *, root_goal: str, metadata: dict[str, Any] | None = None) -> list[PlannedStep]:
        """根据用户目标生成固定但结构化的执行计划。"""

        normalized_goal = root_goal.strip()
        if not normalized_goal:
            raise ValueError("root_goal is required")
        data = metadata or {}
        topic = str(data.get("topic") or normalized_goal)
        platform = str(data.get("platform") or "tiktok")
        style = str(data.get("style") or "专业简洁")
        collection_name = data.get("collection_name")
        query = str(data.get("query") or normalized_goal)

        return [
            PlannedStep(
                step_order=1,
                agent_name="rag_agent",
                title="收集相关知识",
                description="调用 rag_agent 检索目标相关背景知识，作为后续内容生成上下文。",
                input_payload={
                    "query": query,
                    "rag_query": query,
                    "collection_name": collection_name,
                    "top_k": int(data.get("top_k") or 3),
                    "debug": True,
                },
            ),
            PlannedStep(
                step_order=2,
                agent_name="content_agent",
                title="生成内容",
                description="调用 content_agent 生成结构化内容草稿。",
                input_payload={
                    "topic": topic,
                    "platform": platform,
                    "style": style,
                },
            ),
            PlannedStep(
                step_order=3,
                agent_name="review_agent",
                title="轻量 review",
                description="调用 review_agent 对内容结果做基础结构检查。",
                input_payload={
                    "goal": normalized_goal,
                    "review_policy": "phase16_rule_based_review",
                },
            ),
        ]
