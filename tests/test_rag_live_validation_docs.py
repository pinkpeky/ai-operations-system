"""Phase 60G RAG live validation documentation checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "RAG_LIVE_VALIDATION_GUIDE.md"


def test_rag_live_validation_guide_covers_operator_loop_and_api_surface() -> None:
    """The live validation guide should be executable by operators and maintainers."""

    text = GUIDE.read_text(encoding="utf-8")

    for term in (
        "phase60g_live_validation",
        "Workstation User Flow",
        "Server Maintainer Flow",
        "POST /api/v1/files/upload",
        "POST /api/v1/rag/ingest",
        "GET /api/v1/documents",
        "GET /api/v1/documents/{document_id}",
        "POST /api/v1/rag/search",
        "POST /api/v1/rag/debug",
        "POST /api/v1/documents/reingest",
        "DELETE /api/v1/documents/by-source/{source_id}",
        "GET /api/v1/rag/collections",
        "GET /api/v1/rag/embedding/health",
        "TXT",
        "MD",
        "CSV",
        "DOCX",
        "PDF",
        "Generated test files and result JSON stay outside the repository.",
    ):
        assert term in text


def test_rag_live_validation_guide_records_phase_60g_result_without_committed_artifacts() -> None:
    """The guide should record live evidence while keeping generated files out of the repo."""

    text = GUIDE.read_text(encoding="utf-8")

    for term in (
        "Embedding provider `mock`",
        "dimension `384`",
        "Hybrid search returned five results",
        "Reingest produced version `2`",
        "Delete-by-source removed only `phase60g-delete-check`",
        "does not add OCR",
    ):
        assert term in text

    assert not (ROOT / "phase60g-operator-note.txt").exists()
    assert not (ROOT / "phase60g-api-results.json").exists()
