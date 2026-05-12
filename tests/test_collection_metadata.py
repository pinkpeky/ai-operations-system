"""Collection metadata 测试模块。"""

import pytest

from app.repositories.collection_repository import CollectionRepository


@pytest.mark.asyncio
async def test_collection_metadata_is_idempotent(session) -> None:  # type: ignore[no-untyped-def]
    """同一 collection 重复确保元数据时应保持幂等。"""

    repository = CollectionRepository(session)

    first = await repository.ensure_collection_metadata(
        collection_name="lifecycle_collection",
        workspace_id="workspace-a",
        embedding_provider="mock",
        embedding_model_name="mock-embedding-model",
        embedding_dimension=384,
    )
    second = await repository.ensure_collection_metadata(
        collection_name="lifecycle_collection",
        workspace_id="workspace-a",
        embedding_provider="mock",
        embedding_model_name="mock-embedding-model",
        embedding_dimension=384,
    )

    assert first.id == second.id
    assert first.embedding_dimension == 384


@pytest.mark.asyncio
async def test_collection_metadata_rejects_dimension_mismatch(session) -> None:  # type: ignore[no-untyped-def]
    """collection 已存在但 embedding_dimension 不一致时必须报错。"""

    repository = CollectionRepository(session)
    await repository.ensure_collection_metadata(
        collection_name="dimension_guard",
        workspace_id="workspace-a",
        embedding_provider="mock",
        embedding_model_name="mock-embedding-model",
        embedding_dimension=384,
    )

    with pytest.raises(ValueError):
        await repository.ensure_collection_metadata(
            collection_name="dimension_guard",
            workspace_id="workspace-a",
            embedding_provider="mock",
            embedding_model_name="mock-embedding-model",
            embedding_dimension=768,
        )


@pytest.mark.asyncio
async def test_collection_metadata_allows_same_name_across_workspaces(session) -> None:  # type: ignore[no-untyped-def]
    """不同 workspace 可以复用同名 collection，但仍由 workspace_id 隔离元数据。"""

    repository = CollectionRepository(session)

    first = await repository.ensure_collection_metadata(
        collection_name="shared_collection",
        workspace_id="workspace-a",
        embedding_provider="mock",
        embedding_model_name="mock-embedding-model",
        embedding_dimension=384,
    )
    second = await repository.ensure_collection_metadata(
        collection_name="shared_collection",
        workspace_id="workspace-b",
        embedding_provider="mock",
        embedding_model_name="mock-embedding-model",
        embedding_dimension=384,
    )

    assert first.id != second.id
    assert first.workspace_id == "workspace-a"
    assert second.workspace_id == "workspace-b"
