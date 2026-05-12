"""文档生命周期 Service 测试模块。"""

import pytest
from sqlalchemy import select

from app.models.document import Document, DocumentChunk
from app.models.enums import DocumentStatus
from app.rag.embedding_client import EmbeddingClient
from app.rag.ingestion import IngestionPipeline
from app.rag.providers.mock_embedding_provider import MockEmbeddingProvider
from app.rag.vector_store import QdrantVectorStore
from app.services.document_lifecycle import DocumentLifecycleService
from tests.test_vector_store import FakeQdrantClient


def create_lifecycle_service(session, client: FakeQdrantClient) -> DocumentLifecycleService:  # type: ignore[no-untyped-def]
    """创建使用 fake Qdrant 的生命周期服务。"""

    embedding_client = EmbeddingClient(provider=MockEmbeddingProvider(dimension=32))
    vector_store = QdrantVectorStore(
        collection_name="lifecycle_collection",
        embedding_dimension=32,
        client=client,  # type: ignore[arg-type]
    )
    return DocumentLifecycleService(
        session=session,
        ingestion_pipeline=IngestionPipeline(embedding_client=embedding_client, vector_store=vector_store),
    )


@pytest.mark.asyncio
async def test_reingest_marks_old_document_outdated(session) -> None:  # type: ignore[no-untyped-def]
    """同一 source_id 再次 ingest 时，旧文档应标记为 outdated，新文档版本递增。"""

    client = FakeQdrantClient()
    service = create_lifecycle_service(session, client)

    first = await service.ingest_text(
        text="first lifecycle document about AI operations",
        source_id="source-lifecycle",
        chunk_size=80,
        chunk_overlap=10,
    )
    second = await service.ingest_text(
        text="second lifecycle document about AI operations and RAG quality",
        source_id="source-lifecycle",
        chunk_size=80,
        chunk_overlap=10,
    )

    result = await session.execute(select(Document).order_by(Document.version.asc()))
    documents = list(result.scalars().all())

    assert first.version == 1
    assert second.version == 2
    assert [document.status for document in documents] == [
        DocumentStatus.OUTDATED.value,
        DocumentStatus.ACTIVE.value,
    ]
    assert documents[0].chunk_count == 1
    assert documents[1].chunk_count == 1
    assert first.chunk_ids[0] not in {str(point.id) for point in client.collections["lifecycle_collection"]["points"]}
    assert second.chunk_ids[0] in {str(point.id) for point in client.collections["lifecycle_collection"]["points"]}


@pytest.mark.asyncio
async def test_delete_by_source_soft_deletes_records_and_qdrant_points(session) -> None:  # type: ignore[no-untyped-def]
    """delete by source 应软删除数据库记录，并删除 Qdrant points。"""

    client = FakeQdrantClient()
    service = create_lifecycle_service(session, client)

    ingest_result = await service.ingest_text(
        text="document to delete from lifecycle collection",
        source_id="source-delete",
        chunk_size=80,
        chunk_overlap=10,
    )
    delete_result = await service.delete_by_source(
        source_id="source-delete",
        collection_name="lifecycle_collection",
    )

    document_result = await session.execute(select(Document).where(Document.source_id == "source-delete"))
    chunk_result = await session.execute(select(DocumentChunk).where(DocumentChunk.qdrant_point_id == ingest_result.chunk_ids[0]))
    document = document_result.scalar_one()
    chunk = chunk_result.scalar_one()

    assert delete_result.deleted_documents == 1
    assert delete_result.deleted_chunks == 1
    assert delete_result.qdrant_deleted_points == 1
    assert document.status == DocumentStatus.DELETED.value
    assert chunk.status == DocumentStatus.DELETED.value
    assert client.collections["lifecycle_collection"]["points"] == []
