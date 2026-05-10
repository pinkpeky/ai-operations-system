"""PromptManager 测试模块。

验证 system prompt、user prompt 和模板渲染的基础行为。
"""

import pytest

from app.services.prompt_manager import PromptManager


def test_prompt_manager_builds_system_and_user_prompt() -> None:
    """应能组合 system prompt 和 user prompt。"""

    manager = PromptManager()

    prompt = manager.build_prompt(
        system_prompt="你是一个运营助手。",
        user_prompt="生成一条测试文案。",
    )

    assert prompt.system_prompt == "你是一个运营助手。"
    assert prompt.user_prompt == "生成一条测试文案。"
    assert prompt.full_prompt == "System:\n你是一个运营助手。\n\nUser:\n生成一条测试文案。"


def test_prompt_manager_renders_template_with_variables() -> None:
    """模板应能渲染用户输入和自定义变量。"""

    manager = PromptManager()

    prompt = manager.build_prompt(
        system_prompt=None,
        user_prompt="新品上线",
        template="请围绕 {user_prompt} 写一条 {tone} 风格的内容。",
        variables={"tone": "专业"},
    )

    assert prompt.system_prompt is None
    assert prompt.user_prompt == "请围绕 新品上线 写一条 专业 风格的内容。"
    assert prompt.full_prompt == prompt.user_prompt


def test_prompt_manager_raises_for_missing_template_variable() -> None:
    """缺少模板变量时应给出明确错误。"""

    manager = PromptManager()

    with pytest.raises(ValueError, match="Missing prompt template variable: tone"):
        manager.build_prompt(
            system_prompt=None,
            user_prompt="新品上线",
            template="请写一条 {tone} 风格的内容：{user_prompt}",
            variables={},
        )
