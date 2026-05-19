"""Commercial operations documentation checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_commercial_operations_foundation_doc_covers_runtime_and_boundary() -> None:
    text = (ROOT / "docs/COMMERCIAL_OPERATIONS_FOUNDATION.md").read_text(encoding="utf-8")

    for marker in (
        "Phase 61A",
        "Phase 61B",
        "commercial_operations",
        "commercial_operation_links",
        "CommercialOperationService",
        "CommercialOperationLink",
        "/api/v1/commercial-operations",
        "/api/v1/commercial-operations/{operation_id}/links",
        "Admin Dashboard",
        "Evidence",
        "handoff",
        "does not publish",
        "does not execute OpenClaw actions",
        "does not run ComfyUI jobs",
        "does not bypass approval",
    ):
        assert marker in text


def test_recovery_docs_point_to_phase_61b_commercial_operation_links() -> None:
    for relative in (
        "docs/PHASE_INDEX.md",
        "docs/CURRENT_NEXT_PHASE.md",
        "docs/PROJECT_STATUS.md",
        "docs/PROJECT_OVERVIEW.md",
        "docs/en/PROJECT_STATUS.md",
        "docs/zh/PROJECT_STATUS.md",
        "docs/en/API_REFERENCE.md",
        "docs/zh/API_REFERENCE.md",
    ):
        text = (ROOT / relative).read_text(encoding="utf-8")
        assert "Phase 61B" in text or "61B" in text, relative
        assert "commercial-operations" in text or "commercial_operations" in text, relative
        assert "commercial_operation_links" in text or "/links" in text, relative
