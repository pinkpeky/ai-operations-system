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
