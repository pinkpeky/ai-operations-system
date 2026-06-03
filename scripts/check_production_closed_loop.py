"""Read-only production closed-loop delivery audit."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.check_openclaw_provider import build_report as build_openclaw_report  # noqa: E402
from scripts.check_production_config import build_report as build_production_config_report  # noqa: E402


DEFAULT_API_BASE_URL = "http://127.0.0.1:8000"
DEFAULT_WORKER_BASE_URL = "http://127.0.0.1:9100"
DEFAULT_WORKSPACE_ID = "production-workspace"


async def _get_json(
    client: httpx.AsyncClient,
    base_url: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
) -> tuple[dict[str, Any] | None, str | None]:
    try:
        response = await client.get(f"{base_url.rstrip('/')}{path}", headers=headers)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            return None, "invalid_json_payload"
        return payload, None
    except httpx.HTTPStatusError as exc:
        return None, f"http_status_{exc.response.status_code}"
    except httpx.RequestError as exc:
        return None, f"request_failed: {exc}"
    except ValueError as exc:
        return None, f"invalid_json_payload: {exc}"


def _worker_ready(worker_status: dict[str, Any] | None, workspace_id: str) -> bool:
    if not worker_status:
        return False
    return (
        worker_status.get("runtime_running") is True
        and worker_status.get("heartbeat_running") is True
        and worker_status.get("registered") is True
        and worker_status.get("workspace_id") == workspace_id
    )


def _acceptance_ready(acceptance_summary: dict[str, Any] | None) -> bool:
    if not acceptance_summary:
        return False
    provider = acceptance_summary.get("openclaw_provider_readiness")
    provider_ready = isinstance(provider, dict) and provider.get("ready") is True
    return (
        acceptance_summary.get("acceptance_status") == "accepted"
        and acceptance_summary.get("completion_level") == "closed_loop_ready"
        and int(acceptance_summary.get("completion_percent") or 0) >= 100
        and int(acceptance_summary.get("blocked_count") or 0) == 0
        and int(acceptance_summary.get("intervention_queue_count") or 0) == 0
        and not acceptance_summary.get("remaining_gates")
        and provider_ready
    )


def _runbook_evidence_coverage_ready(runbook_evidence_coverage: dict[str, Any] | None) -> bool:
    if not runbook_evidence_coverage:
        return False
    coverage_status = str(runbook_evidence_coverage.get("coverage_status") or "")
    package_count = int(runbook_evidence_coverage.get("package_count") or 0)
    resolved_count = int(runbook_evidence_coverage.get("resolved_count") or 0)
    return (
        coverage_status in {"runbook_evidence_resolved", "no_runbook_evidence_required"}
        and int(runbook_evidence_coverage.get("missing_evidence_count") or 0) == 0
        and int(runbook_evidence_coverage.get("blocked_count") or 0) == 0
        and int(runbook_evidence_coverage.get("needs_follow_up_count") or 0) == 0
        and int(runbook_evidence_coverage.get("dismissed_count") or 0) == 0
        and (package_count == 0 or resolved_count >= package_count)
    )


def _append_config_blockers(blockers: list[str], report: dict[str, Any]) -> None:
    for item in report.get("findings", []):
        if isinstance(item, dict) and item.get("severity") == "error":
            blockers.append(f"production_config:{item.get('key')}")


def _append_worker_blockers(blockers: list[str], worker_status: dict[str, Any] | None, workspace_id: str) -> None:
    if not worker_status:
        blockers.append("worker_status_unavailable")
        return
    if worker_status.get("runtime_running") is not True:
        blockers.append("worker_runtime_not_running")
    if worker_status.get("heartbeat_running") is not True:
        blockers.append("worker_heartbeat_not_running")
    if worker_status.get("registered") is not True:
        blockers.append("worker_not_registered")
    if worker_status.get("workspace_id") != workspace_id:
        blockers.append("worker_workspace_mismatch")


def _append_acceptance_blockers(blockers: list[str], acceptance_summary: dict[str, Any] | None) -> None:
    if not acceptance_summary:
        blockers.append("acceptance_summary_unavailable")
        return
    for gate in acceptance_summary.get("remaining_gates") or []:
        blockers.append(f"remaining_gate:{gate}")
    for operation in acceptance_summary.get("top_blockers") or []:
        if isinstance(operation, dict):
            for reason in operation.get("blocking_reasons") or []:
                blockers.append(f"operation_blocker:{reason}")
    provider = acceptance_summary.get("openclaw_provider_readiness")
    if isinstance(provider, dict) and provider.get("ready") is not True:
        for reason in provider.get("blocking_reasons") or []:
            blockers.append(f"openclaw_provider:{reason}")


def _append_runbook_evidence_coverage_blockers(
    blockers: list[str],
    runbook_evidence_coverage: dict[str, Any] | None,
    *,
    acceptance_summary: dict[str, Any] | None,
) -> None:
    if not runbook_evidence_coverage:
        blockers.append("runbook_evidence_coverage_unavailable")
        return
    package_count = int(runbook_evidence_coverage.get("package_count") or 0)
    resolved_count = int(runbook_evidence_coverage.get("resolved_count") or 0)
    missing_evidence_count = int(runbook_evidence_coverage.get("missing_evidence_count") or 0)
    blocked_count = int(runbook_evidence_coverage.get("blocked_count") or 0)
    needs_follow_up_count = int(runbook_evidence_coverage.get("needs_follow_up_count") or 0)
    dismissed_count = int(runbook_evidence_coverage.get("dismissed_count") or 0)
    evidenced_count = int(runbook_evidence_coverage.get("evidenced_count") or 0)
    submitted_or_review_count = max(
        0,
        evidenced_count - resolved_count - blocked_count - needs_follow_up_count - dismissed_count,
    )

    if missing_evidence_count:
        blockers.append(f"runbook_evidence_coverage:missing_evidence_count={missing_evidence_count}")
    if blocked_count:
        blockers.append(f"runbook_evidence_coverage:blocked_count={blocked_count}")
    if needs_follow_up_count:
        blockers.append(f"runbook_evidence_coverage:needs_follow_up_count={needs_follow_up_count}")
    if dismissed_count:
        blockers.append(f"runbook_evidence_coverage:dismissed_count={dismissed_count}")
    if submitted_or_review_count:
        blockers.append(f"runbook_evidence_coverage:submitted_or_review_count={submitted_or_review_count}")
    if package_count and resolved_count < package_count:
        blockers.append(f"runbook_evidence_coverage:resolved_count={resolved_count}/{package_count}")

    coverage_status = str(runbook_evidence_coverage.get("coverage_status") or "unknown")
    if not _runbook_evidence_coverage_ready(runbook_evidence_coverage):
        blockers.append(f"runbook_evidence_coverage_status:{coverage_status}")
    elif package_count and not _acceptance_ready(acceptance_summary):
        blockers.append("runbook_evidence_readiness_refresh_required")


def _action(
    *,
    action_key: str,
    title: str,
    owner: str,
    priority: int,
    source_blocker: str,
    target: str,
    required_endpoint: str | None = None,
    verification_commands: list[str] | None = None,
    external_dependency_required: bool = False,
) -> dict[str, Any]:
    return {
        "action_key": action_key,
        "title": title,
        "owner": owner,
        "priority": priority,
        "source_blockers": [source_blocker],
        "target": target,
        "required_endpoint": required_endpoint,
        "verification_commands": verification_commands or [],
        "external_dependency_required": external_dependency_required,
    }


def _append_audit_next_action(actions: list[dict[str, Any]], action: dict[str, Any]) -> None:
    action_key = str(action.get("action_key") or "")
    for existing in actions:
        if existing.get("action_key") == action_key:
            existing_sources = list(existing.get("source_blockers") or [])
            for blocker in action.get("source_blockers") or []:
                if blocker not in existing_sources:
                    existing_sources.append(blocker)
            existing["source_blockers"] = existing_sources
            existing["priority"] = min(int(existing.get("priority") or 999), int(action.get("priority") or 999))
            existing["external_dependency_required"] = bool(
                existing.get("external_dependency_required") or action.get("external_dependency_required")
            )
            return
    actions.append(action)


def _production_audit_next_actions(
    blockers: list[str],
    *,
    runbook_evidence_coverage: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    runbook_next_focus = (
        str(runbook_evidence_coverage.get("next_focus") or "record_runbook_evidence")
        if isinstance(runbook_evidence_coverage, dict)
        else "record_runbook_evidence"
    )
    blocked_items = (
        runbook_evidence_coverage.get("blocked_items")
        if isinstance(runbook_evidence_coverage, dict) and isinstance(runbook_evidence_coverage.get("blocked_items"), list)
        else []
    )
    missing_items = (
        runbook_evidence_coverage.get("missing_items")
        if isinstance(runbook_evidence_coverage, dict) and isinstance(runbook_evidence_coverage.get("missing_items"), list)
        else []
    )
    runbook_external_dependency_required = any(
        bool(item.get("external_dependency_required")) for item in [*blocked_items, *missing_items] if isinstance(item, dict)
    )

    for blocker in blockers:
        if blocker.startswith("production_config:") or blocker.startswith("openclaw_smoke:") or blocker.startswith("openclaw_provider:"):
            _append_audit_next_action(
                actions,
                _action(
                    action_key="configure_real_openclaw_provider",
                    title="Configure and verify the real OpenClaw publish provider",
                    owner="server_operator",
                    priority=10,
                    source_blocker=blocker,
                    target="production server and customer-machine worker",
                    required_endpoint="/openclaw/provider-diagnostics",
                    verification_commands=[
                        "python scripts/check_production_config.py --require-production",
                        "python scripts/check_openclaw_provider.py",
                    ],
                    external_dependency_required=True,
                ),
            )
        elif blocker.startswith("worker_") or blocker.startswith("worker_status:"):
            _append_audit_next_action(
                actions,
                _action(
                    action_key="restore_registered_customer_worker",
                    title="Restore the registered production customer-machine worker",
                    owner="server_operator",
                    priority=20,
                    source_blocker=blocker,
                    target="worker_client runtime",
                    required_endpoint="/local/status",
                    verification_commands=["python scripts/check_production_closed_loop.py --report-only"],
                ),
            )
        elif blocker.startswith("api_health:"):
            _append_audit_next_action(
                actions,
                _action(
                    action_key="restore_api_health",
                    title="Restore API health before production closed-loop audit",
                    owner="server_operator",
                    priority=20,
                    source_blocker=blocker,
                    target="ai-operations-api",
                    required_endpoint="/api/v1/health",
                    verification_commands=["python scripts/check_production_closed_loop.py --report-only"],
                ),
            )
        elif blocker == "acceptance_summary:release_gate_checklist_missing":
            _append_audit_next_action(
                actions,
                _action(
                    action_key="deploy_release_gate_acceptance_summary_contract",
                    title="Deploy or restart the API so the production acceptance summary returns release gates",
                    owner="server_operator",
                    priority=22,
                    source_blocker=blocker,
                    target="commercial operations API",
                    required_endpoint="/api/v1/commercial-operations/production-closed-loop/acceptance-summary",
                    verification_commands=[
                        "python scripts/check_production_closed_loop.py --report-only --summary-json"
                    ],
                ),
            )
        elif blocker == "runbook_evidence_readiness_refresh_required":
            _append_audit_next_action(
                actions,
                _action(
                    action_key="refresh_runbook_evidence_readiness",
                    title="Run the Phase 71L readiness refresh after resolved runbook evidence",
                    owner="delivery_operator",
                    priority=30,
                    source_blocker=blocker,
                    target="production delivery audit runbook evidence",
                    required_endpoint="/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage/readiness-refresh",
                    verification_commands=["python scripts/check_production_closed_loop.py --report-only"],
                ),
            )
        elif blocker.startswith("runbook_evidence_coverage:") or blocker.startswith("runbook_evidence_coverage_status:"):
            _append_audit_next_action(
                actions,
                _action(
                    action_key="resolve_runbook_evidence_coverage",
                    title="Record or resolve Phase 71J evidence for every Phase 71I runbook package",
                    owner="delivery_operator",
                    priority=35,
                    source_blocker=blocker,
                    target=runbook_next_focus,
                    required_endpoint="/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-records",
                    verification_commands=["python scripts/check_production_closed_loop.py --report-only"],
                    external_dependency_required=runbook_external_dependency_required,
                ),
            )
        elif blocker.startswith("remaining_gate:"):
            gate = blocker.split(":", 1)[1]
            owner = "operation_owner"
            priority = 40
            if gate == "prepare_customer_machine_execution_handoff":
                owner = "customer_machine_operator"
            elif gate == "complete_metric_feedback_setup":
                owner = "operations_analyst"
            elif gate == "approve_analysis_and_next_cycle_decision":
                owner = "approver"
            elif gate == "configure_real_openclaw_publish_provider":
                owner = "server_operator"
                priority = 15
            elif gate == "resolve_or_acknowledge_intervention_queue":
                owner = "operation_owner"
                priority = 25
            _append_audit_next_action(
                actions,
                _action(
                    action_key=f"clear_acceptance_gate:{gate}",
                    title=f"Clear acceptance gate: {gate}",
                    owner=owner,
                    priority=priority,
                    source_blocker=blocker,
                    target="production closed-loop acceptance summary",
                    required_endpoint="/api/v1/commercial-operations/production-closed-loop/acceptance-summary",
                    verification_commands=["python scripts/check_production_closed_loop.py --report-only"],
                    external_dependency_required=gate == "configure_real_openclaw_publish_provider",
                ),
            )
        elif blocker.startswith("operation_blocker:"):
            _append_audit_next_action(
                actions,
                _action(
                    action_key="clear_operation_project_blockers",
                    title="Open the blocked operation project and clear stale or missing project records",
                    owner="operation_owner",
                    priority=45,
                    source_blocker=blocker,
                    target="commercial operation project workbench",
                    required_endpoint="/api/v1/commercial-operations/production-closed-loop/acceptance-summary",
                    verification_commands=["python scripts/check_production_closed_loop.py --report-only"],
                ),
            )
        else:
            _append_audit_next_action(
                actions,
                _action(
                    action_key="review_unmapped_production_audit_blocker",
                    title="Review unmapped production closed-loop audit blocker",
                    owner="server_operator",
                    priority=90,
                    source_blocker=blocker,
                    target="production closed-loop audit report",
                    verification_commands=["python scripts/check_production_closed_loop.py --report-only"],
                ),
            )

    return sorted(actions, key=lambda item: (int(item.get("priority") or 999), str(item.get("action_key") or "")))


def _blocker_category(blocker: str) -> str:
    if ":" in blocker:
        return blocker.split(":", 1)[0]
    if blocker.startswith("worker_"):
        return "worker"
    if blocker.startswith("api_health"):
        return "api_health"
    return "uncategorized"


def _action_summary(action: dict[str, Any] | None) -> dict[str, Any] | None:
    if not isinstance(action, dict):
        return None
    return {
        "action_key": action.get("action_key"),
        "title": action.get("title"),
        "owner": action.get("owner"),
        "priority": action.get("priority"),
        "target": action.get("target"),
        "required_endpoint": action.get("required_endpoint"),
        "external_dependency_required": bool(action.get("external_dependency_required")),
        "source_blocker_count": len(action.get("source_blockers") or []),
        "verification_commands": action.get("verification_commands") or [],
    }


def _unique_sorted(values: list[str]) -> list[str]:
    return sorted(dict.fromkeys(values))


def _int_value(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _release_gate_item(
    *,
    gate_key: str,
    title: str,
    owner: str,
    ready: bool,
    blocking_reasons: list[str],
    evidence: list[str],
    next_action: str,
    source: str,
) -> dict[str, Any]:
    return {
        "gate_key": gate_key,
        "title": title,
        "owner": owner,
        "required": True,
        "ready": ready,
        "status": "ready" if ready else "blocked",
        "blocking_reasons": blocking_reasons,
        "evidence": evidence,
        "next_action": next_action,
        "source": source,
    }


def _synthesized_release_gate_checklist(acceptance_summary: dict[str, Any] | None) -> list[dict[str, Any]]:
    summary = acceptance_summary or {}
    operation_count = _int_value(summary.get("operation_count"))
    accepted_count = _int_value(summary.get("accepted_count"))
    blocked_count = _int_value(summary.get("blocked_count"))
    ready_for_customer_machine_execution_count = _int_value(
        summary.get("ready_for_customer_machine_execution_count")
    )
    ready_for_metric_feedback_count = _int_value(summary.get("ready_for_metric_feedback_count"))
    ready_for_next_cycle_count = _int_value(summary.get("ready_for_next_cycle_count"))
    intervention_queue_count = _int_value(summary.get("intervention_queue_count"))
    provider = summary.get("openclaw_provider_readiness")
    openclaw_provider_ready = isinstance(provider, dict) and provider.get("ready") is True
    provider_blockers = (
        [str(reason) for reason in provider.get("blocking_reasons") or []]
        if isinstance(provider, dict)
        else []
    )
    source = "audit_synthesized_from_acceptance_summary"
    operation_project_ready = bool(operation_count and accepted_count == operation_count and blocked_count == 0)
    customer_machine_handoff_ready = bool(
        operation_count and ready_for_customer_machine_execution_count == operation_count
    )
    publish_result_ready = bool(operation_count and ready_for_metric_feedback_count == operation_count)
    next_cycle_ready = bool(operation_count and ready_for_next_cycle_count == operation_count)

    return [
        _release_gate_item(
            gate_key="operation_project_readiness",
            title="Operation projects are accepted and unblocked",
            owner="operation_owner",
            ready=operation_project_ready,
            blocking_reasons=[
                *([] if operation_count else ["create_or_import_operation_project"]),
                *([] if accepted_count == operation_count else ["close_operation_readiness_gaps"]),
                *([] if blocked_count == 0 else ["clear_blocking_reasons"]),
            ],
            evidence=[
                f"operation_count={operation_count}",
                f"accepted_count={accepted_count}",
                f"blocked_count={blocked_count}",
            ],
            next_action="close_operation_readiness_gaps",
            source=source,
        ),
        _release_gate_item(
            gate_key="customer_machine_execution_handoff",
            title="Customer-machine execution handoff is ready",
            owner="customer_machine_operator",
            ready=customer_machine_handoff_ready,
            blocking_reasons=[] if customer_machine_handoff_ready else ["prepare_customer_machine_execution_handoff"],
            evidence=[
                f"ready_for_customer_machine_execution_count={ready_for_customer_machine_execution_count}",
                f"operation_count={operation_count}",
            ],
            next_action="prepare_customer_machine_execution_handoff",
            source=source,
        ),
        _release_gate_item(
            gate_key="real_openclaw_publish_provider",
            title="Real OpenClaw publish provider is configured and smoke-verified",
            owner="server_operator",
            ready=openclaw_provider_ready,
            blocking_reasons=provider_blockers
            or ([] if openclaw_provider_ready else ["configure_real_openclaw_publish_provider"]),
            evidence=[
                f"readiness_status={provider.get('readiness_status', 'unknown') if isinstance(provider, dict) else 'unknown'}",
                f"provider={provider.get('provider', 'unknown') if isinstance(provider, dict) else 'unknown'}",
            ],
            next_action="configure_real_openclaw_publish_provider",
            source=source,
        ),
        _release_gate_item(
            gate_key="customer_machine_publish_result_evidence",
            title="Customer-machine publish result evidence has returned",
            owner="customer_machine_operator",
            ready=publish_result_ready,
            blocking_reasons=[] if publish_result_ready else ["complete_customer_machine_publish_result_evidence"],
            evidence=[
                f"ready_for_metric_feedback_count={ready_for_metric_feedback_count}",
                f"operation_count={operation_count}",
            ],
            next_action="record_customer_machine_publish_result_and_metrics",
            source=source,
        ),
        _release_gate_item(
            gate_key="metric_feedback_and_next_cycle",
            title="Metric feedback is approved and next cycle is ready",
            owner="operations_analyst",
            ready=next_cycle_ready,
            blocking_reasons=[] if next_cycle_ready else ["approve_analysis_and_next_cycle_decision"],
            evidence=[
                f"ready_for_next_cycle_count={ready_for_next_cycle_count}",
                f"operation_count={operation_count}",
            ],
            next_action="approve_analysis_and_next_cycle_decision",
            source=source,
        ),
        _release_gate_item(
            gate_key="intervention_queue_clear",
            title="Intervention queue is clear",
            owner="operation_owner",
            ready=intervention_queue_count == 0,
            blocking_reasons=[] if intervention_queue_count == 0 else ["resolve_or_acknowledge_intervention_queue"],
            evidence=[f"intervention_queue_count={intervention_queue_count}"],
            next_action="resolve_or_acknowledge_intervention_queue",
            source=source,
        ),
    ]


def _release_gate_status_counts(checklist: list[Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for gate in checklist:
        if isinstance(gate, dict):
            status = str(gate.get("status") or ("ready" if gate.get("ready") is True else "blocked"))
            counts[status] = counts.get(status, 0) + 1
    return counts


def _release_gate_contract_missing(acceptance_summary: dict[str, Any] | None) -> bool:
    return not (
        isinstance(acceptance_summary, dict)
        and isinstance(acceptance_summary.get("release_gate_checklist"), list)
        and len(acceptance_summary.get("release_gate_checklist") or []) > 0
    )


def _production_audit_delivery_summary(
    *,
    success: bool,
    readiness: dict[str, bool],
    blockers: list[str],
    next_actions: list[dict[str, Any]],
    acceptance_summary: dict[str, Any] | None,
    runbook_evidence_coverage: dict[str, Any] | None,
) -> dict[str, Any]:
    failed_readiness = sorted(key for key, value in readiness.items() if not value)
    passed_readiness = sorted(key for key, value in readiness.items() if value)
    blocker_categories: dict[str, int] = {}
    for blocker in blockers:
        category = _blocker_category(blocker)
        blocker_categories[category] = blocker_categories.get(category, 0) + 1

    external_actions = [action for action in next_actions if action.get("external_dependency_required")]
    operator_actions = [action for action in next_actions if not action.get("external_dependency_required")]
    external_blockers: list[str] = []
    operator_blockers: list[str] = []
    for action in external_actions:
        external_blockers.extend(str(item) for item in action.get("source_blockers") or [])
    for action in operator_actions:
        operator_blockers.extend(str(item) for item in action.get("source_blockers") or [])

    completion_percent = int((acceptance_summary or {}).get("completion_percent") or 0)
    acceptance_status = str((acceptance_summary or {}).get("acceptance_status") or "unavailable")
    completion_level = str((acceptance_summary or {}).get("completion_level") or "unknown")
    release_gate_contract_missing = _release_gate_contract_missing(acceptance_summary)
    release_gate_checklist = (
        acceptance_summary.get("release_gate_checklist")
        if not release_gate_contract_missing and isinstance(acceptance_summary, dict)
        else _synthesized_release_gate_checklist(acceptance_summary)
    )
    release_gate_source = (
        "acceptance_summary"
        if not release_gate_contract_missing
        else "audit_synthesized_from_acceptance_summary"
    )
    release_gate_status_counts = (
        acceptance_summary.get("release_gate_status_counts")
        if not release_gate_contract_missing
        and isinstance(acceptance_summary, dict)
        and isinstance(acceptance_summary.get("release_gate_status_counts"), dict)
        else _release_gate_status_counts(release_gate_checklist)
    )
    release_gate_ready_count = (
        _int_value(acceptance_summary.get("release_gate_ready_count"))
        if not release_gate_contract_missing and isinstance(acceptance_summary, dict)
        else _int_value(release_gate_status_counts.get("ready"))
    )
    release_gate_total_count = (
        _int_value(acceptance_summary.get("release_gate_total_count"))
        if not release_gate_contract_missing and isinstance(acceptance_summary, dict)
        else len(release_gate_checklist)
    )
    release_ready = (
        bool(acceptance_summary.get("release_ready"))
        if not release_gate_contract_missing and isinstance(acceptance_summary, dict) and "release_ready" in acceptance_summary
        else success
    )
    if release_gate_contract_missing:
        release_ready = False
    release_gate_blocked_keys = [
        str(gate.get("gate_key"))
        for gate in release_gate_checklist
        if isinstance(gate, dict) and gate.get("ready") is not True and gate.get("gate_key")
    ]
    coverage_status = str((runbook_evidence_coverage or {}).get("coverage_status") or "unavailable")
    primary_action = next_actions[0] if next_actions else None
    next_external_action = external_actions[0] if external_actions else None
    next_operator_action = operator_actions[0] if operator_actions else None
    release_blocked_by_external_dependency = bool(external_actions)
    release_blocked_by_operator_work = bool(operator_actions)
    if success:
        summary_text = "production closed-loop audit is ready"
    else:
        primary_key = str((primary_action or {}).get("action_key") or "review_blockers")
        summary_text = (
            f"{completion_percent}% complete; {len(blockers)} blockers; "
            f"primary action: {primary_key}"
        )

    return {
        "contract": "production_closed_loop_delivery_audit_summary",
        "summary_text": summary_text,
        "acceptance_status": acceptance_status,
        "completion_level": completion_level,
        "completion_percent": completion_percent,
        "release_ready": release_ready,
        "release_gate_contract_missing": release_gate_contract_missing,
        "release_gate_source": release_gate_source,
        "release_gate_ready_count": release_gate_ready_count,
        "release_gate_total_count": release_gate_total_count,
        "release_gate_status_counts": release_gate_status_counts,
        "release_gate_blocked_keys": release_gate_blocked_keys,
        "readiness_passed_count": len(passed_readiness),
        "readiness_failed_count": len(failed_readiness),
        "readiness_total_count": len(readiness),
        "failed_readiness": failed_readiness,
        "passed_readiness": passed_readiness,
        "blocker_count": len(blockers),
        "blocker_categories": dict(sorted(blocker_categories.items())),
        "next_action_count": len(next_actions),
        "external_dependency_action_count": len(external_actions),
        "operator_action_count": len(operator_actions),
        "release_blocked_by_external_dependency": release_blocked_by_external_dependency,
        "release_blocked_by_operator_work": release_blocked_by_operator_work,
        "external_dependency_blockers": _unique_sorted(external_blockers),
        "operator_work_blockers": _unique_sorted(operator_blockers),
        "primary_next_action": _action_summary(primary_action),
        "next_external_dependency_action": _action_summary(next_external_action),
        "next_operator_action": _action_summary(next_operator_action),
        "runbook_evidence_coverage_status": coverage_status,
        "runbook_evidence_package_count": int((runbook_evidence_coverage or {}).get("package_count") or 0),
        "runbook_evidence_missing_count": int((runbook_evidence_coverage or {}).get("missing_evidence_count") or 0),
        "runbook_evidence_blocked_count": int((runbook_evidence_coverage or {}).get("blocked_count") or 0),
        "runbook_evidence_resolved_count": int((runbook_evidence_coverage or {}).get("resolved_count") or 0),
    }


async def build_report(
    *,
    api_base_url: str = DEFAULT_API_BASE_URL,
    worker_base_url: str = DEFAULT_WORKER_BASE_URL,
    workspace_id: str = DEFAULT_WORKSPACE_ID,
    platform: str | None = None,
    force_metric_due: bool = False,
    timeout_seconds: float = 10.0,
    production_config_report: dict[str, Any] | None = None,
    openclaw_report: dict[str, Any] | None = None,
    api_transport: httpx.AsyncBaseTransport | None = None,
    worker_transport: httpx.AsyncBaseTransport | None = None,
) -> dict[str, Any]:
    """Build a no-action production closed-loop delivery report."""

    config_report = production_config_report or build_production_config_report(require_production=True)
    provider_report = openclaw_report or await build_openclaw_report(
        base_url=worker_base_url,
        timeout_seconds=timeout_seconds,
        transport=worker_transport,
    )
    headers = {"X-Workspace-Id": workspace_id, "X-User-Id": "production-closed-loop-audit"}
    query = f"limit=5&scan_limit=10&force_metric_due={str(force_metric_due).lower()}"
    if platform:
        query = f"platform={platform}&{query}"
    async with httpx.AsyncClient(timeout=timeout_seconds, transport=api_transport) as api_client:
        api_health, api_health_error = await _get_json(api_client, api_base_url, "/api/v1/health")
        acceptance_summary, acceptance_error = await _get_json(
            api_client,
            api_base_url,
            f"/api/v1/commercial-operations/production-closed-loop/acceptance-summary?{query}",
            headers=headers,
        )
        runbook_evidence_coverage, runbook_evidence_coverage_error = await _get_json(
            api_client,
            api_base_url,
            f"/api/v1/commercial-operations/production-closed-loop/delivery-audit/blocker-runbook-packages/evidence-coverage?{query}",
            headers=headers,
        )
    async with httpx.AsyncClient(timeout=timeout_seconds, transport=worker_transport) as worker_client:
        worker_status, worker_status_error = await _get_json(worker_client, worker_base_url, "/local/status")

    blockers: list[str] = []
    if not config_report.get("success"):
        _append_config_blockers(blockers, config_report)
    if not provider_report.get("success"):
        for reason in provider_report.get("blocking_reasons") or ["openclaw_provider_smoke_failed"]:
            blockers.append(f"openclaw_smoke:{reason}")
    if api_health_error:
        blockers.append(f"api_health:{api_health_error}")
    if acceptance_error:
        blockers.append(f"acceptance_summary:{acceptance_error}")
    if runbook_evidence_coverage_error:
        blockers.append(f"runbook_evidence_coverage:{runbook_evidence_coverage_error}")
    if worker_status_error:
        blockers.append(f"worker_status:{worker_status_error}")
    _append_worker_blockers(blockers, worker_status, workspace_id)
    _append_acceptance_blockers(blockers, acceptance_summary)
    if acceptance_summary and _release_gate_contract_missing(acceptance_summary):
        blockers.append("acceptance_summary:release_gate_checklist_missing")
    _append_runbook_evidence_coverage_blockers(
        blockers,
        runbook_evidence_coverage,
        acceptance_summary=acceptance_summary,
    )

    readiness = {
        "production_config_ready": bool(config_report.get("success")),
        "api_health_ready": api_health_error is None and bool((api_health or {}).get("status") in {"ok", "healthy"} or (api_health or {}).get("success") is True),
        "worker_ready": _worker_ready(worker_status, workspace_id),
        "openclaw_provider_ready": bool(provider_report.get("success")),
        "acceptance_summary_ready": _acceptance_ready(acceptance_summary),
        "runbook_evidence_coverage_ready": _runbook_evidence_coverage_ready(runbook_evidence_coverage),
    }
    runbook_evidence_readiness_refresh_required = (
        bool(runbook_evidence_coverage)
        and int(runbook_evidence_coverage.get("package_count") or 0) > 0
        and _runbook_evidence_coverage_ready(runbook_evidence_coverage)
        and not _acceptance_ready(acceptance_summary)
    )
    next_actions = _production_audit_next_actions(
        blockers,
        runbook_evidence_coverage=runbook_evidence_coverage,
    )
    success = all(readiness.values()) and not blockers
    delivery_audit_summary = _production_audit_delivery_summary(
        success=success,
        readiness=readiness,
        blockers=blockers,
        next_actions=next_actions,
        acceptance_summary=acceptance_summary,
        runbook_evidence_coverage=runbook_evidence_coverage,
    )
    return {
        "success": success,
        "contract": "production_closed_loop_delivery_audit",
        "server_side_external_execution": False,
        "actual_publish_performed": False,
        "workspace_id": workspace_id,
        "api_base_url": api_base_url,
        "worker_base_url": worker_base_url,
        "platform": platform,
        "force_metric_due": force_metric_due,
        "readiness": readiness,
        "delivery_audit_summary": delivery_audit_summary,
        "runbook_evidence_readiness_refresh_required": runbook_evidence_readiness_refresh_required,
        "blocking_reasons": blockers,
        "next_actions": next_actions,
        "next_action_count": len(next_actions),
        "production_config": config_report,
        "api_health": api_health,
        "worker_status": worker_status,
        "openclaw_provider_smoke": provider_report,
        "acceptance_summary": acceptance_summary,
        "runbook_evidence_coverage": runbook_evidence_coverage,
    }


def print_text_report(report: dict[str, Any]) -> None:
    status = "PASS" if report["success"] else "FAIL"
    print(f"{status}: production closed-loop delivery audit")
    print(f"contract={report['contract']}")
    print(f"workspace_id={report['workspace_id']}")
    print("server_side_external_execution=false")
    print("actual_publish_performed=false")
    for key, value in report["readiness"].items():
        print(f"{key}={str(value).lower()}")
    summary = report.get("delivery_audit_summary")
    if isinstance(summary, dict):
        print(f"completion_percent={summary.get('completion_percent')}")
        print(f"release_ready={str(summary.get('release_ready')).lower()}")
        print(f"release_gate_ready_count={summary.get('release_gate_ready_count')}")
        print(f"release_gate_total_count={summary.get('release_gate_total_count')}")
        for gate_key in summary.get("release_gate_blocked_keys") or []:
            print(f"- release_gate_blocked: {gate_key}")
        print(f"blocker_count={summary.get('blocker_count')}")
        print(f"external_dependency_action_count={summary.get('external_dependency_action_count')}")
        print(f"operator_action_count={summary.get('operator_action_count')}")
        primary_action = summary.get("primary_next_action")
        if isinstance(primary_action, dict):
            print(f"primary_next_action={primary_action.get('action_key')}")
        external_action = summary.get("next_external_dependency_action")
        if isinstance(external_action, dict):
            print(f"next_external_dependency_action={external_action.get('action_key')}")
        operator_action = summary.get("next_operator_action")
        if isinstance(operator_action, dict):
            print(f"next_operator_action={operator_action.get('action_key')}")
    coverage = report.get("runbook_evidence_coverage")
    if isinstance(coverage, dict):
        print(f"runbook_evidence_coverage_status={coverage.get('coverage_status')}")
        print(f"runbook_evidence_coverage_percent={coverage.get('coverage_percent')}")
        print(f"runbook_evidence_package_count={coverage.get('package_count')}")
        print(f"runbook_evidence_missing_count={coverage.get('missing_evidence_count')}")
        print(f"runbook_evidence_blocked_count={coverage.get('blocked_count')}")
        print(
            "runbook_evidence_readiness_refresh_required="
            f"{str(report.get('runbook_evidence_readiness_refresh_required')).lower()}"
        )
    for blocker in report["blocking_reasons"]:
        print(f"- blocker: {blocker}")
    for action in report.get("next_actions") or []:
        if not isinstance(action, dict):
            continue
        print(
            "- next_action: "
            f"[{action.get('owner')}] {action.get('action_key')} - {action.get('title')}"
        )


def main() -> int:
    parser = argparse.ArgumentParser(description="Read-only production closed-loop delivery audit.")
    parser.add_argument("--api-base-url", default=DEFAULT_API_BASE_URL)
    parser.add_argument("--worker-base-url", default=DEFAULT_WORKER_BASE_URL)
    parser.add_argument("--workspace-id", default=DEFAULT_WORKSPACE_ID)
    parser.add_argument("--platform", default=None)
    parser.add_argument("--force-metric-due", action="store_true")
    parser.add_argument("--timeout-seconds", type=float, default=10.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--summary-json", action="store_true")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()

    report = asyncio.run(
        build_report(
            api_base_url=args.api_base_url,
            worker_base_url=args.worker_base_url,
            workspace_id=args.workspace_id,
            platform=args.platform,
            force_metric_due=args.force_metric_due,
            timeout_seconds=args.timeout_seconds,
        )
    )
    if args.summary_json:
        print(json.dumps(report["delivery_audit_summary"], ensure_ascii=False, indent=2, sort_keys=True))
    elif args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print_text_report(report)
    if args.report_only:
        return 0
    return 0 if report["success"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
