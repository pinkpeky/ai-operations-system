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
        "rag-live-loop",
        "rag-status-grid",
        "rag-search-form",
        "rag-operations-grid",
        "rag-form-grid",
        "rag-detail-grid",
        "ragConsoleTitle",
        "ragOperatorSummary",
        "ragValidationLoopTitle",
        "ragValidationUploadStep",
        "ragValidationInspectStep",
        "ragValidationSearchStep",
        "ragValidationDebugStep",
        "ragValidationCleanupStep",
        "ragSearchAction",
        "ragUploadAction",
        "ragIngestTextAction",
        "ragReingestTextAction",
        "ragDeleteSourceAction",
        "ragDebugAction",
        "ragApi.embeddingHealth",
        "ragApi.documents",
        "ragApi.collections",
        "ragApi.search",
        "ragApi.uploadFile",
        "ragApi.ingestText",
        "ragApi.reingestText",
        "ragApi.deleteBySource",
        "ragApi.debug",
        "知识库操作台",
        "操作闭环",
        "上传或写入",
        "查看文档索引",
        "检索验证",
        "调试分数",
        "重写或删除确认",
        "上传知识文件",
        "写入文本知识",
        "危险操作",
        "检索调试",
        "混合检索",
        "异常文档",
        "检索结果",
        "Knowledge Console",
        "Operation loop",
        "Upload or ingest",
        "Inspect document index",
        "Search to verify",
        "Debug scores",
        "Reingest or confirm delete",
        "Upload knowledge file",
        "Ingest text knowledge",
        "Danger zone",
        "Retrieval debug",
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


def test_admin_dashboard_rag_documents_page_guards_dangerous_operations() -> None:
    """Delete and reingest controls should require deliberate operator input."""

    text = ADMIN_MAIN.read_text(encoding="utf-8")

    assert "source_id is required for reingest" in text
    assert "source_id confirmation does not match" in text
    assert "deleteConfirmSource.trim() !== selectedSourceId" in text
    assert "danger-button" in text
    assert "Force reingest" in text
    assert "force_reingest" in text
