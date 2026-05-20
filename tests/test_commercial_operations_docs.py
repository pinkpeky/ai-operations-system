"""Commercial operations documentation checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_commercial_operations_foundation_doc_covers_runtime_and_boundary() -> None:
    text = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for marker in (
        "Phase 61A",
        "Phase 61B",
        "Phase 61C",
        "Phase 61D",
        "Phase 61E",
        "Phase 61F",
        "Phase 61G",
        "Phase 61H",
        "Phase 61I",
        "Phase 61J",
        "Phase 61K",
        "commercial_operations",
        "commercial_operation_links",
        "commercial_operation_approvals",
        "commercial_operation_dry_runs",
        "commercial_operation_content_drafts",
        "commercial_operation_asset_requests",
        "commercial_operation_deliverables",
        "commercial_operation_execution_requests",
        "commercial_operation_execution_runs",
        "commercial_operation_results",
        "commercial_operation_monitoring_observations",
        "CommercialOperationService",
        "CommercialOperationLink",
        "CommercialOperationApproval",
        "CommercialOperationDryRun",
        "CommercialOperationContentDraft",
        "CommercialOperationAssetRequest",
        "CommercialOperationDeliverable",
        "CommercialOperationExecutionRequest",
        "CommercialOperationExecutionRun",
        "CommercialOperationResult",
        "CommercialOperationMonitoringObservation",
        "/api/v1/commercial-operations",
        "/api/v1/commercial-operations/{operation_id}/links",
        "/api/v1/commercial-operations/{operation_id}/approvals",
        "/api/v1/commercial-operations/{operation_id}/dry-runs",
        "/api/v1/commercial-operations/{operation_id}/content-drafts",
        "/api/v1/commercial-operations/{operation_id}/asset-requests",
        "/api/v1/commercial-operations/{operation_id}/deliverables",
        "/api/v1/commercial-operations/{operation_id}/execution-requests",
        "/api/v1/commercial-operations/{operation_id}/execution-runs",
        "/api/v1/commercial-operations/{operation_id}/results",
        "/api/v1/commercial-operations/{operation_id}/monitoring-observations",
        "Admin Dashboard",
        "Evidence",
        "handoff",
        "Approval",
        "Dry-Run",
        "Content Draft",
        "Asset Request",
        "Deliverable",
        "Execution Request",
        "Execution Run",
        "Result",
        "Monitoring Observation",
        "Output Library",
        "source_type=commercial_operation",
        "does not publish",
        "does not execute OpenClaw actions",
        "does not run ComfyUI jobs",
        "does not bypass approval",
    ):
        assert marker in text


def test_recovery_docs_point_to_phase_61k_commercial_operation_monitoring_observations() -> None:
    for relative in (
        "docs/PHASE_INDEX.md",
        "docs/CURRENT_NEXT_PHASE.md",
        "docs/PROJECT_STATUS.md",
        "docs/PROJECT_OVERVIEW.md",
        "docs/CURRENT_RUNTIME.md",
        "docs/en/PROJECT_STATUS.md",
        "docs/zh/PROJECT_STATUS.md",
        "docs/en/API_REFERENCE.md",
        "docs/zh/API_REFERENCE.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Phase 61K" in text or "61K" in text, relative
        assert "commercial-operations" in text or "commercial_operations" in text, relative
        assert "commercial_operation_monitoring_observations" in text or "/monitoring-observations" in text, relative
