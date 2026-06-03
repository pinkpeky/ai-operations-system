"""Local metric dispatch scheduler tests."""

from __future__ import annotations

import httpx
import pytest

from worker_client.config import WorkerClientConfig
from worker_client.metric_dispatch_scheduler import EXPECTED_POLL_ENDPOINT, WorkerMetricDispatchScheduler


def _config(tmp_path) -> WorkerClientConfig:  # type: ignore[no-untyped-def]
    return WorkerClientConfig(
        server_url="http://server.local",
        worker_name="customer-machine-a",
        worker_type="playwright",
        workspace_id="workspace-a",
        state_path=tmp_path / "worker_state.json",
        timeout_seconds=5,
    )


def _scheduler_payload() -> dict[str, object]:
    return {
        "scheduler_status": "scheduled",
        "scheduler_enabled": True,
        "customer_machine_id": "customer-machine-a",
        "workspace_id": "workspace-a",
        "recommended_poll_interval_seconds": 60,
        "client_timer_payload": {
            "endpoint": EXPECTED_POLL_ENDPOINT,
            "request_body": {
                "platform": "douyin",
                "customer_machine_id": "customer-machine-a",
                "operator_confirmed": True,
                "metadata": {"access_token": "must-not-persist"},
            },
        },
        "notification_events": [{"event_type": "metric_dispatch_ready", "severity": "warning"}],
        "metadata": {"contract": "commercial_operation_metric_dispatch_customer_poll_scheduler"},
    }


def test_metric_dispatch_scheduler_configures_and_redacts_state(tmp_path) -> None:
    scheduler = WorkerMetricDispatchScheduler(_config(tmp_path))

    state = scheduler.configure(_scheduler_payload())

    assert state["configured"] is True
    assert state["scheduler_status"] == "scheduled"
    assert state["client_timer_payload"]["request_body"]["metadata"]["access_token"] == "[redacted]"
    assert state["notification_records"][0]["event_type"] == "metric_dispatch_ready"


@pytest.mark.asyncio
async def test_metric_dispatch_scheduler_tick_calls_customer_poll_endpoint(tmp_path) -> None:
    scheduler = WorkerMetricDispatchScheduler(_config(tmp_path))
    scheduler.configure(_scheduler_payload())
    seen: dict[str, object] = {}

    async def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["workspace"] = request.headers.get("X-Workspace-Id")
        seen["body"] = request.read().decode("utf-8")
        return httpx.Response(
            200,
            json={
                "poll_status": "ready_to_claim",
                "customer_machine_id": "customer-machine-a",
                "auto_claimed": False,
                "assigned_claims": [{"claim_id": "claim-1"}],
                "expired_claims": [],
                "poll_interval_seconds": 60,
                "next_actions": ["open customer console"],
            },
        )

    async with httpx.AsyncClient(transport=httpx.MockTransport(handler), base_url="http://server.local") as client:
        state = await scheduler.tick(force=True, http_client=client)

    assert seen["path"] == EXPECTED_POLL_ENDPOINT
    assert seen["workspace"] == "workspace-a"
    assert state["tick_status"] == "poll_executed"
    assert state["scheduler_status"] == "local_ready_to_claim"
    assert state["last_poll_status"] == "ready_to_claim"
    assert state["history"][-1]["assigned_claim_count"] == 1
    assert state["notification_records"][-1]["source"] == "68u_local_poll_tick"


@pytest.mark.asyncio
async def test_metric_dispatch_scheduler_waits_until_next_poll(tmp_path) -> None:
    scheduler = WorkerMetricDispatchScheduler(_config(tmp_path))
    payload = _scheduler_payload()
    payload["next_poll_at"] = "2999-01-01T00:00:00+00:00"
    scheduler.configure(payload)

    state = await scheduler.tick()

    assert state["tick_status"] == "waiting_for_next_poll"
    assert state["seconds_until_next_poll"] > 0


def test_metric_dispatch_scheduler_rejects_wrong_endpoint(tmp_path) -> None:
    scheduler = WorkerMetricDispatchScheduler(_config(tmp_path))
    payload = _scheduler_payload()
    payload["client_timer_payload"] = {"endpoint": "/wrong", "request_body": {"customer_machine_id": "a"}}

    with pytest.raises(ValueError, match="customer-poll"):
        scheduler.configure(payload)
