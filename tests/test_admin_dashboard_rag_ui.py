"""Admin Dashboard RAG / Documents UI checks."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ADMIN_MAIN = ROOT / "admin_dashboard" / "src" / "main.tsx"


def test_admin_dashboard_rag_documents_page_has_operator_console_and_i18n() -> None:
    """RAG / Documents should be simple enough for operators and maintainers."""

    text = ADMIN_MAIN.read_text(encoding="utf-8")

    for term in (
        "rag-command-center",
        "rag-flow-grid",
        "rag-status-grid",
        "rag-search-form",
        "ragConsoleTitle",
        "ragOperatorSummary",
        "ragSearchAction",
        "ragApi.embeddingHealth",
        "ragApi.documents",
        "ragApi.collections",
        "ragApi.search",
        "知识库操作台",
        "混合检索",
        "异常文档",
        "检索结果",
        "Knowledge Console",
        "hybrid search",
        "not a full document management console",
    ):
        assert term in text


def test_admin_dashboard_rag_documents_page_surfaces_search_errors() -> None:
    """Search should report a clear inline error instead of failing silently."""

    text = ADMIN_MAIN.read_text(encoding="utf-8")

    assert "RAG search unavailable" in text
    assert "setSearchState({ data: toItems(response)" in text
    assert "disabled={!collection.trim() || !query.trim() || searchState.loading}" in text
