"""RAG 检索结果归一化模块。

该模块负责把向量库返回的原始分数转换为稳定、易理解的 similarity_score。
"""

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class NormalizedScore:
    """归一化后的分数结构。"""

    similarity_score: float
    raw_score: float


class RetrievalResultNormalizer:
    """检索结果分数归一化器。"""

    def normalize_score(self, raw_score: float) -> NormalizedScore:
        """将原始相似度分数归一化到 [0, 1]。"""

        try:
            # Qdrant COSINE 分数越大越相似；低于 0 的 dissimilar 结果统一对外显示为 0。
            similarity_score = min(1.0, max(0.0, raw_score))
            return NormalizedScore(
                similarity_score=round(similarity_score, 6),
                raw_score=raw_score,
            )
        except Exception as exc:
            logger.exception("Failed to normalize retrieval score")
            raise RuntimeError("Failed to normalize retrieval score") from exc
