"""Admin Dashboard commercial operations page checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MAIN = ROOT / "admin_dashboard/src/main.tsx"
CLIENT = ROOT / "admin_dashboard/src/api/client.ts"
STYLES = ROOT / "admin_dashboard/src/styles.css"


def test_admin_dashboard_exposes_commercial_operations_page() -> None:
    text = MAIN.read_text(encoding="utf-8")

    assert '"commercial-operations"' in text
    assert "CommercialOperationsPage" in text
    assert "商业运营" in text
    assert "Commercial Ops" in text
    assert "商业运营项目中心" in text
    assert "Commercial operations center" in text
    assert "Phase 61D" in text
    assert "Approval gates" in text
    assert "Safe dry-runs" in text
    assert "证据与交接" in text
    assert "Evidence and handoff" in text
    assert "不会自动发布" in text
    assert "does not publish" in text
    assert "commercialOperationsApi.list" in text
    assert "commercialOperationsApi.create" in text
    assert "commercialOperationsApi.planDraft" in text
    assert "commercialOperationsApi.update" in text
    assert "commercialOperationsApi.approvals" in text
    assert "commercialOperationsApi.createApproval" in text
    assert "commercialOperationsApi.approveApproval" in text
    assert "commercialOperationsApi.rejectApproval" in text
    assert "commercialOperationsApi.cancelApproval" in text
    assert "commercialOperationsApi.dryRuns" in text
    assert "commercialOperationsApi.createDryRun" in text
    assert "commercialOperationsApi.completeDryRun" in text
    assert "commercialOperationsApi.failDryRun" in text
    assert "commercialOperationsApi.cancelDryRun" in text
    assert "commercialOperationsApi.links" in text
    assert "commercialOperationsApi.createLink" in text
    assert "commercialOperationsApi.deleteLink" in text


def test_admin_dashboard_commercial_operations_api_client_paths() -> None:
    text = CLIENT.read_text(encoding="utf-8")

    assert "export const commercialOperationsApi" in text
    assert "/commercial-operations" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/plan-draft" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/approvals/${encodeURIComponent(approvalId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/complete" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/dry-runs/${encodeURIComponent(dryRunId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/links" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/links/${encodeURIComponent(linkId)}" in text
    assert 'method: "PATCH"' in text
    assert 'method: "DELETE"' in text


def test_admin_dashboard_commercial_operations_styles_are_present() -> None:
    text = STYLES.read_text(encoding="utf-8")

    for selector in (
        ".commercial-command-center",
        ".commercial-flow-grid",
        ".commercial-metrics-grid",
        ".commercial-grid",
        ".commercial-form-grid",
        ".commercial-detail-grid",
        ".commercial-action-row",
        ".commercial-approval-grid",
        ".commercial-approval-list",
        ".commercial-approval-item",
        ".commercial-approval-actions",
        ".commercial-dry-run-grid",
        ".commercial-dry-run-list",
        ".commercial-dry-run-item",
        ".commercial-dry-run-actions",
        ".commercial-link-grid",
        ".commercial-link-list",
        ".commercial-link-item",
        ".commercial-link-actions",
    ):
        assert selector in text
