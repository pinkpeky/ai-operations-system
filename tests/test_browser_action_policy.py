"""Browser action permission policy tests."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.browser.services import BrowserActionPolicyService, BrowserService


@pytest.mark.asyncio
async def test_browser_action_policy_allows_example_and_blocks_external(session: AsyncSession) -> None:
    """默认策略只允许 example.com / localhost / 127.0.0.1。"""

    service = BrowserActionPolicyService(session)
    allowed = service.validate_target_domain(action_type="navigate", target="https://example.com")
    blocked = service.validate_target_domain(action_type="navigate", target="https://not-allowed.example.org")

    assert allowed.allowed is True
    assert blocked.allowed is False
    assert blocked.reason == "domain_not_allowed:not-allowed.example.org"


@pytest.mark.asyncio
async def test_browser_service_blocks_disallowed_navigation_and_logs(session: AsyncSession) -> None:
    """被 policy 拦截的 browser action 不应调用 provider，并应写入 action log。"""

    browser_service = BrowserService(session)
    browser_session = await browser_service.create_browser_session(
        workspace_id="workspace-policy",
        user_id="user-a",
    )
    action = await browser_service.execute_action(
        workspace_id="workspace-policy",
        session_id=browser_session.id,
        action_type="navigate",
        target="https://not-allowed.example.org",
    )
    logs = await browser_service.list_logs(workspace_id="workspace-policy", session_id=browser_session.id)

    assert action.status == "failed"
    assert action.error == "domain_not_allowed:not-allowed.example.org"
    assert any(log.message == "Browser action blocked by policy" for log in logs)
