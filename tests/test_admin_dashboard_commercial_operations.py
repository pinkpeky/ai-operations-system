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
    assert "Phase 61O" in text
    assert "Approval gates" in text
    assert "Safe dry-runs" in text
    assert "Content drafts" in text
    assert "Asset requests" in text
    assert "Deliverables" in text
    assert "Evidence snapshots" in text
    assert "Execution requests" in text
    assert "Execution runs" in text
    assert "Results" in text
    assert "Monitoring observations" in text
    assert "Optimization decisions" in text
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
    assert "commercialOperationsApi.contentDrafts" in text
    assert "commercialOperationsApi.createContentDraft" in text
    assert "commercialOperationsApi.generateContentDraft" in text
    assert "commercialOperationsApi.updateContentDraft" in text
    assert "commercialOperationsApi.readyContentDraft" in text
    assert "commercialOperationsApi.approveContentDraft" in text
    assert "commercialOperationsApi.rejectContentDraft" in text
    assert "commercialOperationsApi.archiveContentDraft" in text
    assert "commercialOperationsApi.assetRequests" in text
    assert "commercialOperationsApi.createAssetRequest" in text
    assert "commercialOperationsApi.updateAssetRequest" in text
    assert "commercialOperationsApi.readyAssetRequest" in text
    assert "commercialOperationsApi.approveAssetRequest" in text
    assert "commercialOperationsApi.rejectAssetRequest" in text
    assert "commercialOperationsApi.prepareAssetRequest" in text
    assert "commercialOperationsApi.failAssetRequest" in text
    assert "commercialOperationsApi.archiveAssetRequest" in text
    assert "commercialOperationsApi.deliverables" in text
    assert "commercialOperationsApi.createDeliverable" in text
    assert "commercialOperationsApi.updateDeliverable" in text
    assert "commercialOperationsApi.readyDeliverable" in text
    assert "commercialOperationsApi.approveDeliverable" in text
    assert "commercialOperationsApi.rejectDeliverable" in text
    assert "commercialOperationsApi.packageDeliverable" in text
    assert "commercialOperationsApi.failDeliverable" in text
    assert "commercialOperationsApi.archiveDeliverable" in text
    assert "commercialOperationsApi.evidenceSnapshots" in text
    assert "commercialOperationsApi.createEvidenceSnapshot" in text
    assert "commercialOperationsApi.generateEvidenceSnapshot" in text
    assert "commercialOperationsApi.updateEvidenceSnapshot" in text
    assert "commercialOperationsApi.readyEvidenceSnapshot" in text
    assert "commercialOperationsApi.approveEvidenceSnapshot" in text
    assert "commercialOperationsApi.rejectEvidenceSnapshot" in text
    assert "commercialOperationsApi.archiveEvidenceSnapshot" in text
    assert "commercialOperationsApi.executionRequests" in text
    assert "commercialOperationsApi.createExecutionRequest" in text
    assert "commercialOperationsApi.updateExecutionRequest" in text
    assert "commercialOperationsApi.readyExecutionRequest" in text
    assert "commercialOperationsApi.approveExecutionRequest" in text
    assert "commercialOperationsApi.rejectExecutionRequest" in text
    assert "commercialOperationsApi.prepareExecutionRequest" in text
    assert "commercialOperationsApi.failExecutionRequest" in text
    assert "commercialOperationsApi.cancelExecutionRequest" in text
    assert "commercialOperationsApi.archiveExecutionRequest" in text
    assert "commercialOperationsApi.executionRuns" in text
    assert "commercialOperationsApi.createExecutionRun" in text
    assert "commercialOperationsApi.updateExecutionRun" in text
    assert "commercialOperationsApi.startExecutionRun" in text
    assert "commercialOperationsApi.succeedExecutionRun" in text
    assert "commercialOperationsApi.failExecutionRun" in text
    assert "commercialOperationsApi.retryExecutionRun" in text
    assert "commercialOperationsApi.cancelExecutionRun" in text
    assert "commercialOperationsApi.archiveExecutionRun" in text
    assert "commercialOperationsApi.results" in text
    assert "commercialOperationsApi.createResult" in text
    assert "commercialOperationsApi.updateResult" in text
    assert "commercialOperationsApi.readyResult" in text
    assert "commercialOperationsApi.approveResult" in text
    assert "commercialOperationsApi.rejectResult" in text
    assert "commercialOperationsApi.archiveResult" in text
    assert "commercialOperationsApi.monitoringObservations" in text
    assert "commercialOperationsApi.createMonitoringObservation" in text
    assert "commercialOperationsApi.updateMonitoringObservation" in text
    assert "commercialOperationsApi.readyMonitoringObservation" in text
    assert "commercialOperationsApi.approveMonitoringObservation" in text
    assert "commercialOperationsApi.rejectMonitoringObservation" in text
    assert "commercialOperationsApi.archiveMonitoringObservation" in text
    assert "commercialOperationsApi.optimizationDecisions" in text
    assert "commercialOperationsApi.createOptimizationDecision" in text
    assert "commercialOperationsApi.updateOptimizationDecision" in text
    assert "commercialOperationsApi.readyOptimizationDecision" in text
    assert "commercialOperationsApi.approveOptimizationDecision" in text
    assert "commercialOperationsApi.rejectOptimizationDecision" in text
    assert "commercialOperationsApi.archiveOptimizationDecision" in text
    assert "commercialOperationsApi.links" in text
    assert "commercialOperationsApi.createLink" in text
    assert "commercialOperationsApi.deleteLink" in text
    assert "Generate draft from RAG" in text
    assert "RAG query" in text
    assert "Search mode" in text


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
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/generate-rag" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/content-drafts/${encodeURIComponent(draftId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/prepare" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/asset-requests/${encodeURIComponent(assetRequestId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/package" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/deliverables/${encodeURIComponent(deliverableId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/generate-rag" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/evidence-snapshots/${encodeURIComponent(snapshotId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/prepare" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-requests/${encodeURIComponent(executionRequestId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/start" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/succeed" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/fail" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/retry" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/cancel" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/execution-runs/${encodeURIComponent(executionRunId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/results/${encodeURIComponent(resultId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/monitoring-observations/${encodeURIComponent(observationId)}/archive" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/ready" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/approve" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/reject" in text
    assert "/commercial-operations/${encodeURIComponent(operationId)}/optimization-decisions/${encodeURIComponent(optimizationDecisionId)}/archive" in text
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
        ".commercial-content-grid",
        ".commercial-content-list",
        ".commercial-content-item",
        ".commercial-content-actions",
        ".commercial-asset-grid",
        ".commercial-asset-list",
        ".commercial-asset-item",
        ".commercial-asset-actions",
        ".commercial-deliverable-grid",
        ".commercial-deliverable-list",
        ".commercial-deliverable-item",
        ".commercial-deliverable-actions",
        ".commercial-evidence-grid",
        ".commercial-evidence-list",
        ".commercial-evidence-item",
        ".commercial-evidence-actions",
        ".commercial-execution-grid",
        ".commercial-execution-list",
        ".commercial-execution-item",
        ".commercial-execution-actions",
        ".commercial-execution-run-grid",
        ".commercial-execution-run-list",
        ".commercial-execution-run-item",
        ".commercial-execution-run-actions",
        ".commercial-result-grid",
        ".commercial-result-list",
        ".commercial-result-item",
        ".commercial-result-actions",
        ".commercial-observation-grid",
        ".commercial-observation-list",
        ".commercial-observation-item",
        ".commercial-observation-actions",
        ".commercial-optimization-grid",
        ".commercial-optimization-list",
        ".commercial-optimization-item",
        ".commercial-optimization-actions",
        ".commercial-link-grid",
        ".commercial-link-list",
        ".commercial-link-item",
        ".commercial-link-actions",
    ):
        assert selector in text
