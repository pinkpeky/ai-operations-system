"""真实 Embedding 配置测试模块。"""

import pytest
from sqlalchemy import select

from app.core.config import Settings
from app.models.collection_metadata import CollectionMetadata
from app.rag.embedding_client import EmbeddingClient
from app.rag.ingestion import IngestionPipeline
from app.rag.providers.local_embedding_provider import LocalEmbeddingProvider
from app.rag.vector_store import QdrantVectorStore
from app.services.document_lifecycle import DocumentLifecycleService
from tests.test_local_embedding_provider import FakeHTTPClient
from tests.test_vector_store import FakeQdrantClient


def test_local_embedding_config_uses_ollama_bge_m3() -> None:
    """local embedding 配置应指向 Ollama bge-m3。"""

    settings = Settings(
        EMBEDDING_PROVIDER="local",
        LOCAL_EMBEDDING_BASE_URL="http://host.docker.internal:11434",
        LOCAL_EMBEDDING_MODEL="bge-m3",
    )
    client = EmbeddingClient(settings=settings)

    assert client.provider.provider_name == "local"
    assert client.provider.model == "bge-m3"


@pytest.mark.asyncio
async def test_lifecycle_records_detected_local_embedding_dimension(session) -> None:  # type: ignore[no-untyped-def]
    """生命周期写入应把 local/bge-m3/真实维度写入 collection metadata。"""

    provider = LocalEmbeddingProvider(
        base_url="http://localhost:11434",
        model="bge-m3",
        dimension=384,
        timeout_seconds=120,
        http_client=FakeHTTPClient(),
    )
    embedding_client = EmbeddingClient(provider=provider)
    vector_store = QdrantVectorStore(
        collection_name="real_embedding_config_collection",
        embedding_dimension=384,
        client=FakeQdrantClient(),  # type: ignore[arg-type]
    )
    service = DocumentLifecycleService(
        session=session,
        ingestion_pipeline=IngestionPipeline(embedding_client=embedding_client, vector_store=vector_store),
    )

    await service.ingest_text(
        text="real embedding config test",
        source_id="real-embedding-config",
        workspace_id="workspace-real-embedding",
        user_id="user-real-embedding",
        chunk_size=80,
        chunk_overlap=10,
    )

    result = await session.execute(
        select(CollectionMetadata).where(
            CollectionMetadata.collection_name == "real_embedding_config_collection",
            CollectionMetadata.workspace_id == "workspace-real-embedding",
        )
    )
    metadata = result.scalar_one()

    assert metadata.embedding_provider == "local"
    assert metadata.embedding_model_name == "bge-m3"
    assert metadata.embedding_dimension == 4
    assert vector_store.embedding_dimension == 4
