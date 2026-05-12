"""Keyword Search 测试模块。"""

import pytest

from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentIngestStatus, DocumentStatus
from app.rag.hybrid_search import KeywordSearch


async def create_document_chunk(
    session,
    *,
    workspace_id: str,
    source_id: str,
    collection_name: str,
    text: str,
    document_status: str = DocumentStatus.ACTIVE.value,
    chunk_status: str = DocumentStatus.ACTIVE.value,
):  # type: ignore[no-untyped-def]
    """创建测试文档和 chunk。"""

    document = Document(
        workspace_id=workspace_id,
        user_id=f"user-{workspace_id}",
        source_id=source_id,
        source_name=source_id,
        source_type="text",
        version=1,
        status=document_status,
        collection_name=collection_name,
        document_metadata={},
        chunk_count=1,
        ingest_status=DocumentIngestStatus.COMPLETED.value,
    )
    session.add(document)
    await session.flush()
    chunk = DocumentChunk(
        document_id=document.id,
        collection_name=collection_name,
        chunk_index=0,
        text=text,
        qdrant_point_id=f"{workspace_id}-{source_id}-point",
        chunk_metadata={"workspace_id": workspace_id, "source_id": source_id, "status": chunk_status},
        status=chunk_status,
    )
    session.add(chunk)
    await session.commit()
    return chunk


@pytest.mark.asyncio
async def test_keyword_search_filters_workspace_source_and_active_status(session) -> None:  # type: ignore[no-untyped-def]
    """Keyword Search 必须遵守 workspace/source/active 隔离。"""

    await create_document_chunk(
        session,
        workspace_id="workspace-a",
        source_id="source-a",
        collection_name="keyword_collection",
        text="hybrid search keyword alpha knowledge",
    )
    await create_document_chunk(
        session,
        workspace_id="workspace-b",
        source_id="source-a",
        collection_name="keyword_collection",
        text="hybrid search keyword beta knowledge",
    )
    await create_document_chunk(
        session,
        workspace_id="workspace-a",
        source_id="source-deleted",
        collection_name="keyword_collection",
        text="hybrid search keyword deleted knowledge",
        document_status=DocumentStatus.DELETED.value,
        chunk_status=DocumentStatus.DELETED.value,
    )

    keyword_search = KeywordSearch(session)
    results = await keyword_search.search(
        query="hybrid alpha",
        collection_name="keyword_collection",
        top_k=5,
        workspace_id="workspace-a",
        source_id="source-a",
    )

    assert len(results) == 1
    assert results[0].metadata["workspace_id"] == "workspace-a"
    assert results[0].metadata["source_id"] == "source-a"
    assert results[0].metadata["status"] == "active"
    assert results[0].keyword_score is not None
    assert results[0].keyword_score > 0


@pytest.mark.asyncio
async def test_keyword_search_requires_workspace_id(session) -> None:  # type: ignore[no-untyped-def]
    """Keyword Search 不能在缺少 workspace_id 时查全库。"""

    keyword_search = KeywordSearch(session)

    with pytest.raises(ValueError):
        await keyword_search.search(
            query="hybrid",
            collection_name="keyword_collection",
            top_k=5,
            workspace_id="",
        )
