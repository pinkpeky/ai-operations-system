"""Mock Embedding Provider 模块。

默认 Provider，不调用真实 embedding 服务，用稳定、非负且归一化的伪向量验证 RAG 流程。
"""

import hashlib
import logging
import math
import re

from app.rag.providers.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """固定维度的 Mock Embedding Provider。"""

    provider_name = "mock"

    def __init__(self, dimension: int = 384, model: str = "mock-embedding-model") -> None:
        super().__init__(dimension=dimension, model=model)

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """返回固定维度的稳定伪向量。"""

        try:
            embeddings = [self._embed_text(text) for text in texts]
            logger.info(
                "Mock embeddings generated",
                extra={
                    "provider": self.provider_name,
                    "model": self.model,
                    "count": len(embeddings),
                    "dimension": self.dimension,
                },
            )
            return embeddings
        except Exception as exc:
            logger.exception("Mock embedding provider failed")
            raise RuntimeError("Mock embedding provider failed") from exc

    def _embed_text(self, text: str) -> list[float]:
        """基于 token hash 生成稳定、非负且 L2 归一化的伪向量。"""

        if self.dimension <= 0:
            raise ValueError("Embedding dimension must be positive")

        vector = [0.0 for _ in range(self.dimension)]
        for token in self._tokenize(text):
            self._add_feature(vector, token, weight=1.0)
            for index in range(max(0, len(token) - 2)):
                # 字符 3-gram 让 query 与 chunk 有部分词形重叠时也能得到稳定相似度。
                self._add_feature(vector, token[index : index + 3], weight=0.25)

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]

    def _tokenize(self, text: str) -> list[str]:
        """提取稳定 token，兼容英文、数字和中文文本。"""

        tokens = [token.lower() for token in re.findall(r"\w+", text, flags=re.UNICODE)]
        if tokens:
            return tokens
        return [char for char in text.strip().lower() if not char.isspace()]

    def _add_feature(self, vector: list[float], feature: str, weight: float) -> None:
        """将一个特征稳定映射到向量维度。"""

        digest = hashlib.sha256(feature.encode("utf-8")).digest()
        index = int.from_bytes(digest[:8], "big") % self.dimension
        vector[index] += weight
