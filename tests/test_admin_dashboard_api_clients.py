"""Admin Dashboard API client tests."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CLIENT = ROOT / "admin_dashboard/src/api/client.ts"


def test_admin_dashboard_api_client_modules_exist() -> None:
    client = CLIENT.read_text(encoding="utf-8")

    for module in (
        "workersApi",
        "browserRuntimeApi",
        "conversationsApi",
        "commercialOperationsApi",
        "tasksApi",
        "openclawApi",
        "auditApi",
        "ragApi",
    ):
        assert f"export const {module}" in client


def test_admin_dashboard_api_client_uses_workspace_headers_and_core_paths() -> None:
    client = CLIENT.read_text(encoding="utf-8")

    for header in ("X-Workspace-Id", "X-User-Id"):
        assert header in client
    for path in (
        "/health",
        "/browser-workers/health/summary",
        "/browser-workers/available",
        "/browser-runtime/sessions",
        "/browser-runtime/sessions/${sessionId}/events",
        "/browser-runtime/sessions/${sessionId}/snapshots",
        "/browser-runtime/sessions/${sessionId}/replay",
        "/conversations",
        "/commercial-operations",
        "/commercial-operations/${encodeURIComponent(operationId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/plan-draft",
        "/commercial-operations/${encodeURIComponent(operationId)}/approvals",
        "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/cancel",
        "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs",
        "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/complete",
        "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/fail",
        "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/cancel",
        "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts",
        "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/ready",
        "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/ready",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/prepare",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/fail",
        "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/ready",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/package",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/fail",
        "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/ready",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/prepare",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/fail",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/cancel",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/start",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/succeed",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/fail",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/retry",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/cancel",
        "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/results",
        "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/ready",
        "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations",
        "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/ready",
        "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions",
        "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}",
        "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/ready",
        "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/approve",
        "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/reject",
        "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/archive",
        "/commercial-operations/${encodeURIComponent(operationId)}/links",
        "/commercial-operations/${encodeURIComponent(operationId)}/links/${encodeURIComponent(linkId)}",
        "/tasks?status=",
        "/openclaw/health",
        "/browser/security/audit-logs",
        "/rag/embedding/health",
        "/files/upload",
        "/documents",
        "/documents/${encodeURIComponent(documentId)}",
        "/documents/reingest",
        "/documents/by-source/${encodeURIComponent(sourceId)}${suffix}",
        "/rag/search",
        "/rag/ingest",
        "/rag/debug",
    ):
        assert path in client


def test_admin_dashboard_api_client_handles_errors() -> None:
    client = CLIENT.read_text(encoding="utf-8")

    assert "safeRequest" in client
    assert "Request failed with status" in client
    assert "API unavailable" in client
