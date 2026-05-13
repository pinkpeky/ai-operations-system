"""Collection 元数据 ORM 模型模块。

该表记录 Qdrant collection 的 embedding 配置，避免不同维度向量混写。
"""

from sqlalchemy import Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdTimestampMixin
from app.models.enums import CollectionMetadataStatus


class CollectionMetadata(IdTimestampMixin, Base):
    """Qdrant collection 元数据模型。"""

    __tablename__ = "collections_metadata"
    __table_args__ = (
        UniqueConstraint("workspace_id", "collection_name", name="uq_collections_metadata_workspace_collection"),
    )

    collection_name: Mapped[str] = mapped_column(String(128), nullable=False, index=True, comment="Qdrant collection 名称")
    workspace_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True, comment="预留工作区 ID")
    embedding_provider: Mapped[str] = mapped_column(String(64), nullable=False, comment="Embedding Provider 名称")
    embedding_model_name: Mapped[str] = mapped_column(String(128), nullable=False, comment="Embedding 模型名称")
    embedding_dimension: Mapped[int] = mapped_column(Integer, nullable=False, comment="Embedding 向量维度")
    distance_metric: Mapped[str] = mapped_column(String(32), default="cosine", nullable=False, comment="向量距离度量")
    status: Mapped[str] = mapped_column(
        String(32),
        default=CollectionMetadataStatus.ACTIVE.value,
        nullable=False,
        index=True,
        comment="Collection 元数据状态",
    )
