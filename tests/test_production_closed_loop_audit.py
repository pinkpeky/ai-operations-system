"""Production closed-loop delivery audit tests."""

from __future__ import annotations

import httpx
import pytest

from scripts.check_production_closed_loop import build_report


def _config_report(success: bool = True) -> dict[str, object]:
    return {
        "success": success,
        "app_env": "production",
        "production_config_strict": True,
        "error_count": 0 if success else 1,
        "warning_count": 0,
        "findings": []
        if success
        else [
            {
                "severity": "error",
                "key": "WORKER_CLIENT_OPENCLAW_PROVIDER",
                "message": "mock",
                "expected": "openclaw_http",
                "actual": "mock",
            }
        ],
    }


def _openclaw_report(success: bool = True) -> dict[str, object]:
    return {
        "success": success,
        "contract": "openclaw_provider_readiness_smoke",
        "server_side_external_execution": False,
        "actual_publish_performed": False,
        "blocking_reasons": [] if success else ["openclaw_provider_is_mock"],
    }


def _release_gate(gate_key: str, ready: bool = True) -> dict[str, object]:
    return {
        "gate_key": gate_key,
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "blocking_reasons": [] if ready else [gate_key],
    }


def _release_gates(ready: bool = True) -> list[dict[str, object]]:
    gate_keys = [
        "operation_project_readiness",
        "customer_machine_execution_handoff",
        "real_openclaw_publish_provider",
        "customer_machine_publish_result_evidence",
        "metric_feedback_and_next_cycle",
        "intervention_queue_clear",
    ]
    if ready:
        return [_release_gate(gate_key, True) for gate_key in gate_keys]
    return [
        _release_gate("operation_project_readiness", False),
        _release_gate("customer_machine_execution_handoff", True),
        _release_gate("real_openclaw_publish_provider", False),
        _release_gate("customer_machine_publish_result_evidence", False),
        _release_gate("metric_feedback_and_next_cycle", False),
        _release_gate("intervention_queue_clear", True),
    ]


def _api_transport(
    accepted: bool = True,
    runbook_evidence_ready: bool = True,
    *,
    include_release_gates: bool = True,
) -> httpx.MockTransport:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/api/v1/health":
            return httpx.Response(200, json={"status": "ok"})
        if request.url.path == "/api/v1/commercial-operations/production-closed-loop/acceptance-summary":
            if accepted:
                payload: dict[str, object] = {
                    "workspace_id": "production-workspace",
                    "acceptance_status": "accepted",
                    "completion_percent": 100,
                    "completion_level": "closed_loop_ready",
                    "operation_count": 1,
                    "accepted_count": 1,
                    "ready_for_customer_machine_execution_count": 1,
                    "ready_for_metric_feedback_count": 1,
                    "ready_for_next_cycle_count": 1,
                    "blocked_count": 0,
                    "intervention_queue_count": 0,
                    "remaining_gates": [],
                    "top_blockers": [],
                    "openclaw_provider_readiness": {"ready": True},
                }
                if include_release_gates:
                    payload.update(
                        {
                            "release_ready": True,
                            "release_gate_ready_count": 6,
                            "release_gate_total_count": 6,
                            "release_gate_status_counts": {"ready": 6},
                            "release_gate_checklist": _release_gates(True),
                        }
                    )
                return httpx.Response(
                    200,
                    json=payload,
                )
            payload = {
                "workspace_id": "production-workspace",
                "acceptance_status": "requires_operator_action",
                "completion_percent": 15,
                "completion_level": "not_ready",
                "operation_count": 2,
                "accepted_count": 1,
                "ready_for_customer_machine_execution_count": 1,
                "ready_for_metric_feedback_count": 0,
                "ready_for_next_cycle_count": 0,
                "blocked_count": 1,
                "intervention_queue_count": 0,
                "remaining_gates": ["close_operation_readiness_gaps"],
                "top_blockers": [{"blocking_reasons": ["approved_operation_plan_missing"]}],
                "openclaw_provider_readiness": {"ready": False, "blocking_reasons": ["openclaw_provider_is_mock"]},
            }
            if include_release_gates:
                payload.update(
                    {
                        "release_ready": False,
                        "release_gate_ready_count": 2,
                        "release_gate_total_count": 6,
                        "release_gate_status_counts": {"ready": 2, "blocked": 4},
                        "release_gate_checklist": _release_gates(False),
                    }
                )
            return httpx.Response(
                200,
                json=payload,
            )
        if (
            request.url.path
            == "/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage"
        ):
            if runbook_evidence_ready:
                return httpx.Response(
                    200,
                    json={
                        "workspace_id": "production-workspace",
                        "coverage_status": "runbook_evidence_resolved",
                        "coverage_percent": 100,
                        "package_count": 1,
                        "evidenced_count": 1,
                        "missing_evidence_count": 0,
                        "resolved_count": 1,
                        "blocked_count": 0,
                        "needs_follow_up_count": 0,
                        "dismissed_count": 0,
                        "next_focus": "refresh_readiness_after_runbook_evidence",
                    },
                )
            return httpx.Response(
                200,
                json={
                    "workspace_id": "production-workspace",
                    "coverage_status": "runbook_evidence_missing",
                    "coverage_percent": 50,
                    "package_count": 2,
                    "evidenced_count": 1,
                    "missing_evidence_count": 1,
                    "resolved_count": 0,
                    "blocked_count": 1,
                    "needs_follow_up_count": 0,
                    "dismissed_count": 0,
                    "next_focus": "record_runbook_evidence:delivery_audit_blocker_runbook:configure_real_openclaw_publish_provider",
                },
            )
        return httpx.Response(404, json={})

    return httpx.MockTransport(handler)


def _worker_transport(ready: bool = True) -> httpx.MockTransport:
    async def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path == "/local/status":
            return httpx.Response(
                200,
                json={
                    "runtime_running": ready,
                    "heartbeat_running": ready,
                    "registered": ready,
                    "workspace_id": "production-workspace" if ready else "wrong-workspace",
                },
            )
        return httpx.Response(404, json={})

    return httpx.MockTransport(handler)


@pytest.mark.asyncio
async def test_production_closed_loop_audit_passes_when_all_gates_are_ready() -> None:
    report = await build_report(
        production_config_report=_config_report(True),
        openclaw_report=_openclaw_report(True),
        api_transport=_api_transport(True),
        worker_transport=_worker_transport(True),
    )

    assert report["success"] is True
    assert report["contract"] == "production_closed_loop_delivery_audit"
    assert report["server_side_external_execution"] is False
    assert report["actual_publish_performed"] is False
    assert report["blocking_reasons"] == []
    assert all(report["readiness"].values())
    assert report["runbook_evidence_readiness_refresh_required"] is False
    assert report["runbook_evidence_coverage"]["coverage_status"] == "runbook_evidence_resolved"
    assert report["next_action_count"] == 0
    assert report["next_actions"] == []
    summary = report["delivery_audit_summary"]
    assert summary["contract"] == "production_closed_loop_delivery_audit_summary"
    assert summary["release_ready"] is True
    assert summary["release_gate_contract_missing"] is False
    assert summary["release_gate_source"] == "acceptance_summary"
    assert summary["release_gate_ready_count"] == 6
    assert summary["release_gate_total_count"] == 6
    assert summary["release_gate_status_counts"] == {"ready": 6}
    assert summary["release_gate_blocked_keys"] == []
    assert summary["completion_percent"] == 100
    assert summary["readiness_failed_count"] == 0
    assert summary["blocker_count"] == 0
    assert summary["primary_next_action"] is None
    assert summary["next_operator_action"] is None
    assert summary["next_external_dependency_action"] is None


@pytest.mark.asyncio
async def test_production_closed_loop_audit_reports_current_blockers() -> None:
    report = await build_report(
        production_config_report=_config_report(False),
        openclaw_report=_openclaw_report(False),
        api_transport=_api_transport(False, runbook_evidence_ready=False),
        worker_transport=_worker_transport(False),
    )

    assert report["success"] is False
    blockers = set(report["blocking_reasons"])
    assert "production_config:WORKER_CLIENT_OPENCLAW_PROVIDER" in blockers
    assert "openclaw_smoke:openclaw_provider_is_mock" in blockers
    assert "worker_workspace_mismatch" in blockers
    assert "remaining_gate:close_operation_readiness_gaps" in blockers
    assert "operation_blocker:approved_operation_plan_missing" in blockers
    assert "openclaw_provider:openclaw_provider_is_mock" in blockers
    assert "runbook_evidence_coverage:missing_evidence_count=1" in blockers
    assert "runbook_evidence_coverage:blocked_count=1" in blockers
    assert "runbook_evidence_coverage:resolved_count=0/2" in blockers
    assert "runbook_evidence_coverage_status:runbook_evidence_missing" in blockers
    assert report["readiness"]["runbook_evidence_coverage_ready"] is False
    action_keys = {str(action["action_key"]) for action in report["next_actions"]}
    assert "configure_real_openclaw_provider" in action_keys
    assert "resolve_runbook_evidence_coverage" in action_keys
    assert "clear_operation_project_blockers" in action_keys
    assert "clear_acceptance_gate:close_operation_readiness_gaps" in action_keys
    summary = report["delivery_audit_summary"]
    assert summary["release_ready"] is False
    assert summary["release_gate_contract_missing"] is False
    assert summary["release_gate_source"] == "acceptance_summary"
    assert summary["release_gate_ready_count"] == 2
    assert summary["release_gate_total_count"] == 6
    assert summary["release_gate_status_counts"]["blocked"] == 4
    assert "real_openclaw_publish_provider" in summary["release_gate_blocked_keys"]
    assert summary["completion_percent"] == 15
    assert summary["blocker_count"] == len(report["blocking_reasons"])
    assert summary["readiness_failed_count"] >= 1
    assert summary["release_blocked_by_external_dependency"] is True
    assert summary["release_blocked_by_operator_work"] is True
    assert summary["external_dependency_action_count"] >= 1
    assert summary["operator_action_count"] >= 1
    assert summary["primary_next_action"]["action_key"] == "configure_real_openclaw_provider"
    assert summary["next_external_dependency_action"]["action_key"] == "configure_real_openclaw_provider"
    assert summary["next_operator_action"]["action_key"] == "restore_registered_customer_worker"
    assert summary["blocker_categories"]["production_config"] == 1
    assert summary["blocker_categories"]["openclaw_smoke"] == 1
    assert summary["blocker_categories"]["remaining_gate"] == 1
    assert summary["blocker_categories"]["operation_blocker"] == 1
    assert summary["runbook_evidence_coverage_status"] == "runbook_evidence_missing"
    assert summary["runbook_evidence_missing_count"] == 1
    assert summary["runbook_evidence_blocked_count"] == 1
    assert summary["runbook_evidence_resolved_count"] == 0


@pytest.mark.asyncio
async def test_production_closed_loop_audit_requires_readiness_refresh_after_resolved_runbook_evidence() -> None:
    report = await build_report(
        production_config_report=_config_report(True),
        openclaw_report=_openclaw_report(True),
        api_transport=_api_transport(False, runbook_evidence_ready=True),
        worker_transport=_worker_transport(True),
    )

    assert report["success"] is False
    assert report["readiness"]["runbook_evidence_coverage_ready"] is True
    assert report["runbook_evidence_readiness_refresh_required"] is True
    assert "runbook_evidence_readiness_refresh_required" in report["blocking_reasons"]
    action_keys = {str(action["action_key"]) for action in report["next_actions"]}
    assert "refresh_runbook_evidence_readiness" in action_keys
    summary = report["delivery_audit_summary"]
    assert summary["release_ready"] is False
    assert "real_openclaw_publish_provider" in summary["release_gate_blocked_keys"]
    assert summary["runbook_evidence_coverage_status"] == "runbook_evidence_resolved"
    assert summary["runbook_evidence_missing_count"] == 0
    assert summary["runbook_evidence_resolved_count"] == 1
    assert summary["release_blocked_by_external_dependency"] is True
    assert summary["release_blocked_by_operator_work"] is True
    assert summary["next_external_dependency_action"]["action_key"] == "configure_real_openclaw_provider"
    assert summary["next_operator_action"]["action_key"] == "refresh_runbook_evidence_readiness"


@pytest.mark.asyncio
async def test_production_closed_loop_audit_synthesizes_release_gates_when_api_contract_is_missing() -> None:
    report = await build_report(
        production_config_report=_config_report(True),
        openclaw_report=_openclaw_report(True),
        api_transport=_api_transport(False, runbook_evidence_ready=True, include_release_gates=False),
        worker_transport=_worker_transport(True),
    )

    assert report["success"] is False
    assert "acceptance_summary:release_gate_checklist_missing" in report["blocking_reasons"]
    action_keys = {str(action["action_key"]) for action in report["next_actions"]}
    assert "deploy_release_gate_acceptance_summary_contract" in action_keys
    summary = report["delivery_audit_summary"]
    assert summary["release_ready"] is False
    assert summary["release_gate_contract_missing"] is True
    assert summary["release_gate_source"] == "audit_synthesized_from_acceptance_summary"
    assert summary["release_gate_total_count"] == 6
    assert summary["release_gate_status_counts"]["blocked"] >= 1
    assert "operation_project_readiness" in summary["release_gate_blocked_keys"]
    assert "real_openclaw_publish_provider" in summary["release_gate_blocked_keys"]
    assert "customer_machine_publish_result_evidence" in summary["release_gate_blocked_keys"]
