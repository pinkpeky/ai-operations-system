"""RAG workspace 过滤测试模块。"""

import pytest

from app.rag.embedding_client import EmbeddingClient
from app.rag.ingestion import IngestionPipeline
from app.rag.providers.mock_embedding_provider import MockEmbeddingProvider
from app.rag.retrieval import RetrievalPipeline
from app.rag.vector_store import QdrantVectorStore
from app.services.document_lifecycle import DocumentLifecycleService
from tests.test_vector_store import FakeQdrantClient


@pytest.mark.asyncio
async def test_rag_search_isolated_by_workspace_and_active_status(session) -> None:  # type: ignore[no-untyped-def]
    """不同 workspace 无法互相检索数据，且 active 过滤继续生效。"""

    client = FakeQdrantClient()
    embedding_client = EmbeddingClient(provider=MockEmbeddingProvider(dimension=32))
    vector_store = QdrantVectorStore(
        collection_name="workspace_filter_collection",
        embedding_dimension=32,
        client=client,  # type: ignore[arg-type]
    )
    ingestion = IngestionPipeline(embedding_client=embedding_client, vector_store=vector_store)
    retrieval = RetrievalPipeline(embedding_client=embedding_client, vector_store=vector_store)
    service = DocumentLifecycleService(session=session, ingestion_pipeline=ingestion)

    await service.ingest_text(
        text="workspace alpha private lifecycle knowledge",
        source_id="workspace-filter-source",
        workspace_id="workspace-a",
        user_id="user-a",
        chunk_size=80,
        chunk_overlap=10,
    )
    await service.ingest_text(
        text="workspace beta private lifecycle knowledge",
        source_id="workspace-filter-source",
        workspace_id="workspace-b",
        user_id="user-b",
        chunk_size=80,
        chunk_overlap=10,
    )
    latest_a = await service.ingest_text(
        text="workspace alpha active replacement lifecycle knowledge",
        source_id="workspace-filter-source",
        workspace_id="workspace-a",
        user_id="user-a",
        chunk_size=80,
        chunk_overlap=10,
    )

    workspace_a_results = await retrieval.search(
        query="active replacement lifecycle knowledge",
        source_id="workspace-filter-source",
        workspace_id="workspace-a",
        top_k=5,
    )
    workspace_b_results = await retrieval.search(
        query="active replacement lifecycle knowledge",
        source_id="workspace-filter-source",
        workspace_id="workspace-b",
        top_k=5,
    )

    assert len(workspace_a_results) == 1
    assert workspace_a_results[0].metadata["document_id"] == latest_a.document_id
    assert workspace_a_results[0].metadata["status"] == "active"
    assert len(workspace_b_results) == 1
    assert workspace_b_results[0].metadata["workspace_id"] == "workspace-b"
