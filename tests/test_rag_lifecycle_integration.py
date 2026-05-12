"""RAG 生命周期集成测试模块。"""

import pytest

from app.rag.embedding_client import EmbeddingClient
from app.rag.ingestion import IngestionPipeline
from app.rag.providers.mock_embedding_provider import MockEmbeddingProvider
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import QdrantVectorStore
from app.services.document_lifecycle import DocumentLifecycleService
from tests.test_vector_store import FakeQdrantClient


@pytest.mark.asyncio
async def test_rag_search_returns_only_active_document_after_reingest(session) -> None:  # type: ignore[no-untyped-def]
    """re-ingest 后 search 默认只返回 active 文档 chunk。"""

    client = FakeQdrantClient()
    embedding_client = EmbeddingClient(provider=MockEmbeddingProvider(dimension=32))
    vector_store = QdrantVectorStore(
        collection_name="rag_lifecycle_collection",
        embedding_dimension=32,
        client=client,  # type: ignore[arg-type]
    )
    ingestion = IngestionPipeline(embedding_client=embedding_client, vector_store=vector_store)
    retrieval = RetrievalPipeline(embedding_client=embedding_client, vector_store=vector_store)
    service = DocumentLifecycleService(session=session, ingestion_pipeline=ingestion)

    await service.ingest_text(
        text="old content about duplicate ingest pollution",
        source_id="source-rag-lifecycle",
        chunk_size=80,
        chunk_overlap=10,
    )
    latest = await service.ingest_text(
        text="active content about lifecycle management and clean RAG retrieval",
        source_id="source-rag-lifecycle",
        chunk_size=80,
        chunk_overlap=10,
    )

    results = await retrieval.search(
        query="lifecycle management clean RAG retrieval",
        top_k=5,
        source_id="source-rag-lifecycle",
    )

    assert len(results) == 1
    assert results[0].metadata["document_id"] == latest.document_id
    assert results[0].metadata["version"] == 2
    assert results[0].metadata["status"] == "active"
