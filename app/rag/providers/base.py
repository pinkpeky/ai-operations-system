"""Embedding Provider 抽象模块。

Provider 层只负责文本向量化，不直接处理 Qdrant 写入和检索。
"""

from abc import ABC, abstractmethod
from typing import ClassVar


class BaseEmbeddingProvider(ABC):
    """Embedding Provider 基类。"""

    provider_name: ClassVar[str] = "base"

    def __init__(self, dimension: int, model: str) -> None:
        self.dimension = dimension
        self.model = model

    @abstractmethod
    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """将一批文本转换为向量。"""

    async def embed_query(self, query: str) -> list[float]:
        """将查询文本转换为向量。"""

        embeddings = await self.embed_texts([query])
        return embeddings[0]
