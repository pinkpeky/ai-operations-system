"""Collection 元数据 API 数据模型模块。"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.collection_metadata import CollectionMetadata


class CollectionMetadataResponse(BaseModel):
    """Collection 元数据响应。"""

    id: UUID
    collection_name: str
    workspace_id: str | None
    embedding_provider: str
    embedding_model_name: str
    embedding_dimension: int
    distance_metric: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_model(cls, metadata: CollectionMetadata) -> "CollectionMetadataResponse":
        """从 ORM 对象构建响应。"""

        return cls(
            id=metadata.id,
            collection_name=metadata.collection_name,
            workspace_id=metadata.workspace_id,
            embedding_provider=metadata.embedding_provider,
            embedding_model_name=metadata.embedding_model_name,
            embedding_dimension=metadata.embedding_dimension,
            distance_metric=metadata.distance_metric,
            status=metadata.status,
            created_at=metadata.created_at,
            updated_at=metadata.updated_at,
        )
