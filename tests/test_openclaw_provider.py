"""OpenClaw provider tests."""

import pytest

from worker_client.openclaw import MockOpenClawProvider, OpenClawActionRequest, OpenClawRuntime


@pytest.mark.asyncio
async def test_mock_openclaw_provider_returns_stable_response() -> None:
    """Mock provider 应返回稳定结果，且不调用真实 OpenClaw。"""

    provider = MockOpenClawProvider()
    response = await provider.execute_action(
        OpenClawActionRequest(
            action_type="inspect_page",
            target="https://example.com",
            input_payload={"hint": "phase28"},
            profile_id="profile-1",
            browser_session_id="session-1",
        )
    )

    assert response.success is True
    assert response.provider == "mock"
    assert response.mock is True
    assert response.output_payload["real_openclaw_called"] is False
    assert response.output_payload["target"] == "https://example.com"


@pytest.mark.asyncio
async def test_openclaw_runtime_disabled_is_graceful() -> None:
    """Runtime 关闭时应清晰返回错误，不抛未处理异常。"""

    runtime = OpenClawRuntime(provider_name="mock", enabled=False)

    health = await runtime.health_check()
    capabilities = await runtime.capabilities()

    assert health.success is False
    assert health.enabled is False
    assert capabilities.success is False
    assert capabilities.capabilities["openclaw"] is False
