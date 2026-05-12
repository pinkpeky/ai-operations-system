"""Collection 元数据 Repository 模块。"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.collection_metadata import CollectionMetadata
from app.models.enums import CollectionMetadataStatus

logger = logging.getLogger(__name__)


class CollectionRepository:
    """collections_metadata 数据访问层。"""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_name(self, collection_name: str, workspace_id: str | None = None) -> CollectionMetadata | None:
        """按 collection_name 和 workspace_id 查询元数据。"""

        statement = select(CollectionMetadata).where(CollectionMetadata.collection_name == collection_name)
        if workspace_id is None:
            statement = statement.where(CollectionMetadata.workspace_id.is_(None))
        else:
            statement = statement.where(CollectionMetadata.workspace_id == workspace_id)
        result = await self.session.execute(statement)
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: str, limit: int = 200) -> list[CollectionMetadata]:
        """查询指定 workspace 下的 collection 元数据。"""

        statement = (
            select(CollectionMetadata)
            .where(CollectionMetadata.workspace_id == workspace_id)
            .order_by(CollectionMetadata.created_at.desc())
            .limit(limit)
        )
        result = await self.session.execute(statement)
        return list(result.scalars().all())

    async def ensure_collection_metadata(
        self,
        *,
        collection_name: str,
        embedding_provider: str,
        embedding_model_name: str,
        embedding_dimension: int,
        workspace_id: str | None = None,
        distance_metric: str = "cosine",
    ) -> CollectionMetadata:
        """确保 collection 元数据存在，并阻止维度不一致的混写。"""

        existing = await self.get_by_name(collection_name, workspace_id=workspace_id)
        if existing is not None:
            if existing.embedding_dimension != embedding_dimension:
                raise ValueError(
                    "Collection embedding dimension mismatch: "
                    f"{collection_name} existing={existing.embedding_dimension}, requested={embedding_dimension}"
                )
            logger.info("Collection metadata already exists", extra={"collection": collection_name})
            return existing

        metadata = CollectionMetadata(
            collection_name=collection_name,
            workspace_id=workspace_id,
            embedding_provider=embedding_provider,
            embedding_model_name=embedding_model_name,
            embedding_dimension=embedding_dimension,
            distance_metric=distance_metric,
            status=CollectionMetadataStatus.ACTIVE.value,
        )
        self.session.add(metadata)
        await self.session.flush()
        logger.info(
            "Collection metadata created",
            extra={"collection": collection_name, "dimension": embedding_dimension},
        )
        return metadata
